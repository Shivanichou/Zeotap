#python -m unittest -v test_rule_creation.py

import unittest
from corelogic_without_streamlit_for_testing import create_rule, ast_to_string


class TestRuleCreation(unittest.TestCase):

    def test_single_operand_rule(self):
        rule_string = "age > 30"
        expected_ast_representation = "age > 30"
        ast = create_rule(rule_string)

        # Verify the AST is not None
        self.assertIsNotNone(ast)

        # Verify the AST string representation matches the expected string
        ast_string = ast_to_string(ast)
        self.assertEqual(ast_string, expected_ast_representation)

    def test_complex_rule_with_and(self):
        rule_string = "age > 30 and salary < 50000"
        expected_ast_representation = "(age > 30 and salary < 50000)"
        ast = create_rule(rule_string)

        # Verify the AST is not None
        self.assertIsNotNone(ast)

        # Verify the AST string representation matches the expected string
        ast_string = ast_to_string(ast)
        self.assertEqual(ast_string, expected_ast_representation)

    def test_complex_rule_with_or(self):
        rule_string = "experience >= 5 or department = 'HR'"
        expected_ast_representation = "(experience >= 5 or department = 'hr')"
        ast = create_rule(rule_string)

        # Verify the AST is not None
        self.assertIsNotNone(ast)

        # Verify the AST string representation matches the expected string
        ast_string = ast_to_string(ast)
        self.assertEqual(ast_string, expected_ast_representation)

    def test_nested_rule_with_parentheses(self):
        rule_string = "(age > 30 and salary < 50000) or experience >= 10"
        expected_ast_representation = "((age > 30 and salary < 50000) or experience >= 10)"
        ast = create_rule(rule_string)

        # Verify the AST is not None
        self.assertIsNotNone(ast)

        # Verify the AST string representation matches the expected string
        ast_string = ast_to_string(ast)
        self.assertEqual(ast_string, expected_ast_representation)

    def test_invalid_rule(self):
        rule_string = "age >"
        ast = create_rule(rule_string)

        # Verify that an invalid rule returns None
        self.assertIsNone(ast)


if __name__ == '__main__':
    unittest.main()
