import unittest
from corelogic_without_streamlit_for_testing import evaluate_rule


class TestEvaluateRule(unittest.TestCase):

    def test_single_operand_rule_true(self):
        # Sample JSON AST for rule: "age > 30"
        rule_json = {
            "type": "operand",
            "value": "age > 30"
        }
        # User data where age is 35
        user_data = {
            "age": 35
        }

        # Evaluate the rule
        result = evaluate_rule(rule_json, user_data)

        # Expected result should be True since 35 > 30
        self.assertTrue(result)

    def test_single_operand_rule_false(self):
        # Sample JSON AST for rule: "age > 30"
        rule_json = {
            "type": "operand",
            "value": "age > 30"
        }
        # User data where age is 25
        user_data = {
            "age": 25
        }

        # Evaluate the rule
        result = evaluate_rule(rule_json, user_data)

        # Expected result should be False since 25 is not greater than 30
        self.assertFalse(result)

    def test_complex_and_rule_true(self):
        # Sample JSON AST for rule: "age > 30 and salary < 50000"
        rule_json = {
            "type": "operator",
            "value": "and",
            "left": {
                "type": "operand",
                "value": "age > 30"
            },
            "right": {
                "type": "operand",
                "value": "salary < 50000"
            }
        }
        # User data where age is 35 and salary is 45000
        user_data = {
            "age": 35,
            "salary": 45000
        }

        # Evaluate the rule
        result = evaluate_rule(rule_json, user_data)

        # Expected result should be True since both conditions are satisfied
        self.assertTrue(result)

    def test_complex_and_rule_false(self):
        # Sample JSON AST for rule: "age > 30 and salary < 50000"
        rule_json = {
            "type": "operator",
            "value": "and",
            "left": {
                "type": "operand",
                "value": "age > 30"
            },
            "right": {
                "type": "operand",
                "value": "salary < 50000"
            }
        }
        # User data where age is 35 but salary is 60000
        user_data = {
            "age": 35,
            "salary": 60000
        }

        # Evaluate the rule
        result = evaluate_rule(rule_json, user_data)

        # Expected result should be False since salary is not less than 50000
        self.assertFalse(result)

    def test_complex_or_rule_true(self):
        # Sample JSON AST for rule: "age > 30 or salary < 50000"
        rule_json = {
            "type": "operator",
            "value": "or",
            "left": {
                "type": "operand",
                "value": "age > 30"
            },
            "right": {
                "type": "operand",
                "value": "salary < 50000"
            }
        }
        # User data where age is 25 but salary is 45000
        user_data = {
            "age": 25,
            "salary": 45000
        }

        # Evaluate the rule
        result = evaluate_rule(rule_json, user_data)

        # Expected result should be True since salary < 50000 even though age is not greater than 30
        self.assertTrue(result)

    def test_complex_or_rule_false(self):
        # Sample JSON AST for rule: "age > 30 or salary < 50000"
        rule_json = {
            "type": "operator",
            "value": "or",
            "left": {
                "type": "operand",
                "value": "age > 30"
            },
            "right": {
                "type": "operand",
                "value": "salary < 50000"
            }
        }
        # User data where age is 25 and salary is 60000
        user_data = {
            "age": 25,
            "salary": 60000
        }

        # Evaluate the rule
        result = evaluate_rule(rule_json, user_data)

        # Expected result should be False since neither condition is satisfied
        self.assertFalse(result)


    def test_string_equality_rule_false(self):
        # Sample JSON AST for rule: "department = 'HR'"
        rule_json = {
            "type": "operand",
            "value": "department = 'HR'"
        }
        # User data where department is 'Finance'
        user_data = {
            "department": "Finance"
        }

        # Evaluate the rule
        result = evaluate_rule(rule_json, user_data)

        # Expected result should be False since the department is not 'HR'
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
