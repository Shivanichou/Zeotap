import re
import mysql.connector
from mysql.connector import Error
from collections import Counter
import json

# Predefined catalog of valid attributes
VALID_ATTRIBUTES = {
    "age": "integer",
    "salary": "integer",
    "experience": "integer",
    "department": "string"
}

# Connect to the MySQL Database
def create_connection():
    """Create and return a database connection."""
    try:
        connection = mysql.connector.connect(
            host='localhost',  # Your MySQL host
            port=3306,  # MySQL port
            database='rule_engine',  # The database name
            user='root',  # MySQL username
            password='9961'  # MySQL password
        )
        if connection.is_connected():
            return connection
    except Error as e:
        return None

# Insert rule into the database
def insert_rule(connection, rule_string):
    """Insert a new rule into the rules table."""
    try:
        cursor = connection.cursor()
        query = "INSERT INTO rules (rule_string) VALUES (%s)"
        cursor.execute(query, (rule_string,))
        connection.commit()
    except Error as e:
        pass

# Fetch all rules from the database
def fetch_rules(connection):
    """Fetch all rules from the database."""
    try:
        cursor = connection.cursor()
        query = "SELECT id, rule_string FROM rules"
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        return []

# Delete rule from the database
def delete_rule(connection, rule_id):
    """Delete a rule from the rules table."""
    try:
        cursor = connection.cursor()
        query = "DELETE FROM rules WHERE id = %s"
        cursor.execute(query, (rule_id,))
        connection.commit()
    except Error as e:
        pass

# AST Node definition (for use in rule creation)
class Node:
    def __init__(self, node_type, left=None, right=None, value=None):
        self.type = node_type  # 'operator' or 'operand'
        self.left = left
        self.right = right
        self.value = value  # For operands (e.g., 'age > 30')

# Tokenizer function with error handling
def tokenize(rule_string):
    try:
        token_pattern = r'(\band\b|\bor\b|\(|\)|[><!=]=?|=|[a-zA-Z_]\w*|\d+|\'[^\']*\')'
        tokens = re.findall(token_pattern, rule_string, flags=re.IGNORECASE)
        return [token.strip().lower() for token in tokens]
    except Exception as e:
        return []

# Validate attribute against the catalog
def validate_attribute(attribute):
    """Check if the attribute is part of the valid catalog."""
    if attribute not in VALID_ATTRIBUTES:
        return False
    return True

# Recursive Parser function with validation and error handling
def parse_tokens(tokens):
    def parse_expression(index):
        """Recursive function to parse an expression."""
        if index >= len(tokens):
            return None, index

        token = tokens[index]

        # Handle left parenthesis for subexpressions
        if token == "(":
            left_node, next_index = parse_subexpression(index + 1)
            if next_index >= len(tokens) or tokens[next_index] != ")":
                return None, next_index
            return left_node, next_index + 1

        # Handle operand (field operator value)
        if token.isidentifier():
            if index + 2 >= len(tokens):
                return None, index + 2

            field = token
            operator = tokens[index + 1]
            value = tokens[index + 2]

            # Validate the field against the catalog
            if not validate_attribute(field):
                return None, index + 3

            # Validate operator
            if operator not in [">", "<", "=", "==", "!=", ">=", "<="]:
                return None, index + 3

            operand_node = Node("operand", value=f"{field} {operator} {value}")
            return operand_node, index + 3

        return None, index + 1

    def parse_subexpression(index):
        left_node, index = parse_expression(index)

        # If no more tokens, return left node
        if index >= len(tokens):
            return left_node, index

        # Handle AND/OR operators
        if tokens[index] in ["and", "or"]:
            operator = tokens[index]
            right_node, next_index = parse_subexpression(index + 1)
            return Node("operator", left=left_node, right=right_node, value=operator), next_index

        return left_node, index

    # Parse the full expression
    try:
        ast, _ = parse_subexpression(0)
        return ast
    except Exception as e:

        return None

# Rule creation with error handling
def create_rule(rule_string):
    if not rule_string or len(rule_string) < 3:

        return None

    tokens = tokenize(rule_string)
    if not tokens:

        return None

    ast = parse_tokens(tokens)
    if ast is None:

        return None

    return ast

# Convert AST back to human-readable string
def ast_to_string(ast):
    if ast.type == "operand":
        return ast.value
    elif ast.type == "operator":
        left_string = ast_to_string(ast.left)
        right_string = ast_to_string(ast.right)
        return f"({left_string} {ast.value} {right_string})"
    return ""

# Rule evaluation
def evaluate_operand(operand, user_data):
    field, operator, value = operand.value.split(" ")

    if field not in user_data or user_data[field] is None:
        return None  # Skip this operand

    user_value = user_data[field]
    if operator == ">=":
        return int(user_value) >= int(value)
    elif operator == ">":
        return int(user_value) > int(value)
    elif operator == "<=":
        return int(user_value) <= int(value)
    elif operator == "<":
        return int(user_value) < int(value)
    elif operator in ["=", "=="]:
        return str(user_value) == value
    elif operator == "!=":
        return str(user_value) != value
    return False

def evaluate_ast(ast, user_data):
    if ast.type == "operand":
        return evaluate_operand(ast, user_data)

    elif ast.type == "operator":
        left_result = evaluate_ast(ast.left, user_data)
        right_result = evaluate_ast(ast.right, user_data)

        if ast.value == "and":
            if left_result is None or right_result is None:
                return left_result or right_result
            return left_result and right_result

        elif ast.value == "or":
            if left_result is None and right_result is None:
                return False
            return (left_result is not None and left_result) or (right_result is not None and right_result)

    return False

# Extract the required fields from the AST
def extract_fields_from_ast(ast):
    if ast.type == "operand":
        field, _, _ = ast.value.split(" ")
        return {field}
    elif ast.type == "operator":
        left_fields = extract_fields_from_ast(ast.left)
        right_fields = extract_fields_from_ast(ast.right)
        return left_fields.union(right_fields)
    return set()

# Function to evaluate a rule using JSON AST format
def evaluate_rule(ast_json, user_data):
    if ast_json["type"] == "operand":
        field, operator, value = ast_json["value"].split(" ")

        if field not in user_data or user_data[field] is None:
            return None

        user_value = user_data[field]
        if operator == ">=":
            return int(user_value) >= int(value)
        elif operator == ">":
            return int(user_value) > int(value)
        elif operator == "<=":
            return int(user_value) <= int(value)
        elif operator == "<":
            return int(user_value) < int(value)
        elif operator in ["=", "=="]:
            return str(user_value) == value
        elif operator == "!=":
            return str(user_value) != value
        return False

    elif ast_json["type"] == "operator":
        left_result = evaluate_rule(ast_json["left"], user_data)
        right_result = evaluate_rule(ast_json["right"], user_data)

        if ast_json["value"] == "and":
            if left_result is None or right_result is None:
                return left_result or right_result
            return left_result and right_result

        elif ast_json["value"] == "or":
            if left_result is None and right_result is None:
                return False
            return (left_result is not None and left_result) or (right_result is not None and right_result)

    return False

# New function to combine rules
class CombinedNode(Node):
    def __init__(self, node_type, left=None, right=None, value=None):
        super().__init__(node_type, left, right, value)

def combine_rules(rules):
    if not rules:

        return None

    rule_asts = []
    operator_count = Counter()

    for rule in rules:
        ast = create_rule(rule)
        if ast is not None:
            rule_asts.append(ast)
            count_operators_in_ast(ast, operator_count)

    if not rule_asts:

        return None

    most_frequent_operator = operator_count.most_common(1)[0][0] if operator_count else "or"

    combined_ast = rule_asts[0]
    for rule_ast in rule_asts[1:]:
        combined_ast = CombinedNode("operator", left=combined_ast, right=rule_ast, value=most_frequent_operator)

    return combined_ast

def count_operators_in_ast(ast, operator_count):
    if ast.type == "operator":
        operator_count[ast.value] += 1
        count_operators_in_ast(ast.left, operator_count)
        count_operators_in_ast(ast.right, operator_count)

# Streamlit UI

