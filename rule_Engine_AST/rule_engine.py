import re
import streamlit as st
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
            host='rule-engine-db',  # Your MySQL host
            port=3306,  # MySQL port
            database='rule_engine',  # The database name
            user='root',  # MySQL username
            password='9961'  # MySQL password
        )
        if connection.is_connected():
            st.success("Connected to MySQL database")
            return connection
    except Error as e:
        st.error(f"Error while connecting to MySQL: {e}")
        return None

# Insert rule into the database
def insert_rule(connection, rule_string):
    """Insert a new rule into the rules table."""
    try:
        cursor = connection.cursor()
        query = "INSERT INTO rules (rule_string) VALUES (%s)"
        cursor.execute(query, (rule_string,))
        connection.commit()
        st.success(f"Rule saved in database with ID: {cursor.lastrowid}")
    except Error as e:
        st.error(f"Error while saving the rule: {e}")

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
        st.error(f"Error fetching rules from database: {e}")
        return []

# Delete rule from the database
def delete_rule(connection, rule_id):
    """Delete a rule from the rules table."""
    try:
        cursor = connection.cursor()
        query = "DELETE FROM rules WHERE id = %s"
        cursor.execute(query, (rule_id,))
        connection.commit()
        st.success(f"Rule with ID {rule_id} deleted successfully")
    except Error as e:
        st.error(f"Error while deleting the rule: {e}")

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
        st.error(f"Error in tokenizing rule: {e}")
        return []

# Validate attribute against the catalog
def validate_attribute(attribute):
    """Check if the attribute is part of the valid catalog."""
    if attribute not in VALID_ATTRIBUTES:
        st.error(f"Invalid attribute '{attribute}'. Allowed attributes: {', '.join(VALID_ATTRIBUTES.keys())}")
        return False
    return True

# Recursive Parser function with validation and error handling
def parse_tokens(tokens):
    valid_operators = {">", "<", ">=", "<=", "=", "==", "!=", "and", "or"}

    def parse_expression(index):
        """Recursive function to parse an expression."""
        if index >= len(tokens):
            st.error("Unexpected end of input.")
            return None, index

        token = tokens[index]

        # Handle left parenthesis for subexpressions
        if token == "(":
            left_node, next_index = parse_subexpression(index + 1)
            if next_index >= len(tokens) or tokens[next_index] != ")":
                st.error("Mismatched or missing parentheses.")
                return None, next_index
            return left_node, next_index + 1

        # Handle operand (field operator value)
        if token.isidentifier():
            # Check if we have enough tokens to form a valid condition
            if index + 2 >= len(tokens):
                st.error("Incomplete operand. Expected 'field operator value'.")
                return None, index + 2

            field = token
            operator = tokens[index + 1]
            value = tokens[index + 2]

            # Validate the field against the catalog
            if not validate_attribute(field):
                return None, index + 3

            # Validate the operator
            if operator not in valid_operators:
                st.error(f"Invalid operator: '{operator}'. Use valid operators like >=, <=, =, etc.")
                return None, index + 3

            # Strict check to ensure value is not another field/operator
            if value.isidentifier() or value in valid_operators:
                #st.error(f"Invalid value '{value}'. A valid value (e.g., number, string) is expected, not a field or operator.")
                return None, index + 3

            # If the format is valid, create an operand node
            operand_node = Node("operand", value=f"{field} {operator} {value}")
            return operand_node, index + 3

        # If we encounter an unexpected token, it's an error
        st.error(f"Unexpected token: {token}")
        return None, index + 1

    def parse_subexpression(index):
        left_node, index = parse_expression(index)

        # If parsing failed, halt further processing
        if left_node is None:
            return None, index

        # If no more tokens, return left node
        if index >= len(tokens):
            return left_node, index

        # Handle AND/OR operators
        if tokens[index] in ["and", "or"]:
            operator = tokens[index]
            right_node, next_index = parse_subexpression(index + 1)

            # If the right node is invalid, stop parsing
            if right_node is None:
                return None, next_index

            return Node("operator", left=left_node, right=right_node, value=operator), next_index

        return left_node, index

    # Parse the full expression
    try:
        ast, final_index = parse_subexpression(0)

        # Ensure that the whole rule has been parsed without errors
        if ast is None or final_index < len(tokens):
            st.error("Invalid rule structure detected. Please correct the rule.")
            return None

        #st.write(f"Parsed AST: {ast_to_string(ast)}")  # Debug output to check the parsed structure
        return ast
    except Exception as e:
        st.error(f"Error in parsing rule: {e}")
        return None


def validate_rule_string(rule_string):
    tokens = tokenize(rule_string)
    operators = {"and", "or", ">", "<", ">=", "<=", "=", "==", "!="}

    for token in tokens:
        # Only validate if it's not an operator
        if token.isidentifier() and token not in operators:
            if not validate_attribute(token):
                return False
    return True


# Rule creation with error handling
def create_rule(rule_string):
    if not rule_string or len(rule_string) < 3:
        st.error("Invalid rule format: Rule is too short or empty.")
        return None

    if not validate_rule_string(rule_string):
        #st.error("Invalid rule due to unsupported attributes.")
        return None

    tokens = tokenize(rule_string)
    if not tokens:
        st.error("Invalid rule format: Failed to tokenize the rule.")
        return None

    ast = parse_tokens(tokens)
    if ast is None:
        #st.error("Failed to create a valid AST from the provided rule.")
        return None

    return ast

# Convert AST back to human-readable string
def ast_to_string(ast):
    if ast is None:
        return "Invalid AST"
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
    value = value.strip("'").strip('"')

    if field not in user_data or user_data[field] is None:
        return None  # Skip this operand


    user_value = user_data[field]
    #st.write(f"Evaluating: field={field}, operator={operator}, user_value={user_value}, rule_value={value}")
    if operator in ["=", "=="]:
        if field == 'department':  # Case-insensitive comparison for 'department'
            return str(user_value).lower() == value.lower()
        else:
            return str(user_value) == value
    elif operator == "!=":
        return str(user_value) != value
    elif operator == ">=":
        return int(user_value) >= int(value)
    elif operator == ">":
        return int(user_value) > int(value)
    elif operator == "<=":
        return int(user_value) <= int(value)
    elif operator == "<":
        return int(user_value) < int(value)

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
            return bool(left_result) or bool(right_result)

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
        st.error("No rules to combine.")
        return None

    rule_asts = []
    operator_count = Counter()

    for rule in rules:
        ast = create_rule(rule)
        if ast is not None:
            rule_asts.append(ast)
            count_operators_in_ast(ast, operator_count)

    if not rule_asts:
        st.error("No valid rules found.")
        return None

    most_frequent_operator = operator_count.most_common(1)[0][0] if operator_count else "or"

    combined_ast = rule_asts[0]
    for rule_ast in rule_asts[1:]:
        combined_ast = CombinedNode("operator", left=combined_ast, right=rule_ast, value=most_frequent_operator)

    st.info(f"Rules are combined using the most frequent operator: '{most_frequent_operator}'")
    return combined_ast

def is_duplicate_rule(connection, rule_string):
    """Check if the rule already exists in the database."""
    try:
        cursor = connection.cursor()
        query = "SELECT COUNT(*) FROM rules WHERE rule_string = %s"
        cursor.execute(query, (rule_string,))
        result = cursor.fetchone()
        return result[0] > 0  # True if the rule exists, False otherwise
    except Error as e:
        st.error(f"Error while checking for duplicate rules: {e}")
        return False


def count_operators_in_ast(ast, operator_count):
    if ast.type == "operator":
        operator_count[ast.value] += 1
        count_operators_in_ast(ast.left, operator_count)
        count_operators_in_ast(ast.right, operator_count)

# Streamlit UI
st.title("Rule Engine")

# Connect to MySQL Database
connection = create_connection()

if connection:
    existing_rules = fetch_rules(connection)

    st.subheader("Existing Rules")

    rule_options = ["Select a rule"] + [f"Rule {rule_id}: {rule_string}" for rule_id, rule_string in existing_rules]
    selected_rule = st.selectbox("Choose a rule to view/delete:", rule_options)

    if selected_rule != "Select a rule" and st.button("Delete Selected Rule"):
        selected_rule_id = int(selected_rule.split()[1].replace(':', ''))
        delete_rule(connection, selected_rule_id)

    st.subheader("Create a New Rule")

    # Show allowed attributes directly in a single line
    st.markdown("**Available Attributes:** age (integer), salary (integer), experience (integer), department (string)")

    # Show rule format guide using an expander
    with st.expander("Rule Format Guide"):
        st.markdown("""
        **Rule Format Examples:**

        - `age > 30 and salary < 50000`
        - `experience >= 5 or department = 'sales'`
        - `age <= 40 and department != 'HR'`

        **Supported Operators:**

        - Comparison: `>`, `<`, `>=`, `<=`, `=`, `==`, `!=`
        - Logical: `and`, `or`

        **Notes:**

        - Use single quotes for string values (e.g., `'sales'`).
        - Multiple conditions can be combined using `and` or `or`.
        - Parentheses `()` can be used to group conditions.
        """)

    # The rest of your existing code follows here...

    new_rule_input = st.text_input("Enter a new rule (e.g., 'age > 30 and salary < 50000')")

    if st.button("Create Rule"):
        if new_rule_input:
            ast = create_rule(new_rule_input)
            if ast:
                rule_string = ast_to_string(ast)

                # Check if the rule is a duplicate before inserting
                if is_duplicate_rule(connection, rule_string):
                    st.warning("This rule already exists in the database. Please enter a different rule.")
                else:
                    st.write(f"Rule string to be inserted: {rule_string}")
                    insert_rule(connection, rule_string)
            else:
                st.error("Failed to create the rule. Please enter a valid rule.")
        else:
            st.error("Please enter a valid rule before submitting.")

    st.subheader("Modify Existing Rule")

    # Select an existing rule to modify
    selected_rule_to_modify = st.selectbox("Choose a rule to modify:", rule_options)

    if selected_rule_to_modify != "Select a rule":
        selected_rule_id = int(selected_rule_to_modify.split()[1].replace(':', ''))
        # Fetch the original rule string
        rule_to_modify = [rule_string for rule_id, rule_string in existing_rules if rule_id == selected_rule_id][0]

        # Display the rule in a text input field for editing
        modified_rule_input = st.text_area("Modify the rule:", value=rule_to_modify, height=100)

        # Button to update the rule
        if st.button("Update Rule"):
            if modified_rule_input:
                # Parse and validate the modified rule
                modified_ast = create_rule(modified_rule_input)

                if modified_ast:
                    # If parsing is successful, update the rule in the database
                    try:
                        cursor = connection.cursor()
                        query = "UPDATE rules SET rule_string = %s WHERE id = %s"
                        cursor.execute(query, (modified_rule_input, selected_rule_id))
                        connection.commit()
                        st.success(f"Rule with ID {selected_rule_id} has been updated successfully")
                    except Error as e:
                        st.error(f"Error while updating the rule: {e}")
                else:
                    st.error("Invalid rule format. Please correct the rule and try again.")
            else:
                st.error("The rule cannot be empty. Please provide a valid rule.")

    st.subheader("Combine Rules")

    selected_rules = st.multiselect("Select rules to combine", rule_options[1:])
    combined_ast = None

    if selected_rules:
        selected_rule_ids = [int(rule.split()[1].replace(':', '')) for rule in selected_rules]
        selected_rule_strings = [rule_string for rule_id, rule_string in existing_rules if rule_id in selected_rule_ids]

        combined_ast = combine_rules(selected_rule_strings)

        if combined_ast:
            combined_rule_string = ast_to_string(combined_ast)
            st.write(f"Combined Rule: {combined_rule_string}")

    with st.sidebar:

        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.subheader("Input Attributes for Rule Evaluation")

        user_data = {}
        for attribute, data_type in VALID_ATTRIBUTES.items():
            if data_type == "integer":
                user_data[attribute] = st.number_input(f"Enter {attribute}", min_value=0,value=None)
            elif data_type == "string":
                user_data[attribute] = st.text_input(f"Enter {attribute}")

        provided_attributes = {k for k, v in user_data.items() if v != 0 and v != ''}
        #st.write(f"Captured input values: {user_data}")

        if st.button("Evaluate Rules"):
            # Filter out fields with blank or None values (0 is considered valid)
            provided_attributes = {k for k, v in user_data.items() if v not in [None, '']}

            # Check if all input fields are empty or None (0 is considered valid)
            if all(value == '' or value is None for value in user_data.values()):
                st.error("Please enter input values")
            else:
                rule_satisfied = False
                rule_evaluated = False
                any_rule_evaluated = False

                # Evaluate combined rules (if any)
                if combined_ast:
                    combined_rule_satisfied = evaluate_ast(combined_ast, user_data)
                    rule_evaluated = True
                    if combined_rule_satisfied:
                        st.write("Combined rule evaluation: True")

                    else:
                        st.write("Combined rule evaluation: False")

                # Evaluate individual rules
                for rule_id, rule_string in existing_rules:
                    ast = create_rule(rule_string)
                    if ast is None:
                        st.error(f"Failed to parse rule {rule_id}.")
                        continue

                    rule_fields = extract_fields_from_ast(ast)

                    # Check if all required attributes are provided (must match exactly)
                    if not rule_fields.issubset(provided_attributes):
                        #st.warning(f"Rule {rule_id} skipped due to missing required attributes.")
                        continue

                    # Check if there are extra attributes that don't belong to the rule
                    if len(provided_attributes) != len(rule_fields):
                        #st.warning(f"Rule {rule_id} skipped due to extra attributes.")
                        continue

                    # Evaluate the rule if all required attributes are provided and no extra attributes
                    rule_evaluated = True
                    any_rule_evaluated = True
                    if evaluate_ast(ast, user_data):
                        st.write(f"Evaluation result for Rule {rule_id}: True")
                        rule_satisfied = True
                    else:
                        st.write(f"Evaluation result for Rule {rule_id}: False")

                # Display results
                if not rule_satisfied and rule_evaluated:
                    pass
                if not any_rule_evaluated:
                    st.warning(
                        "No rules match the provided attributes. Consider creating a new rule based on the input."
                    )


