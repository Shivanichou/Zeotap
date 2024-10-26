import unittest
from collections import Counter

from corelogic_without_streamlit_for_testing import create_rule, ast_to_string, combine_rules, tokenize


class TestCombineRules(unittest.TestCase):
    def test_combine_rules_with_most_frequent_operator(self):
        # Example rules to combine, with a mix of 'and' and 'or'
        rules = [
            "age > 20 or experience >= 3",  # contains 'and'
            "salary <= 60000",               # neutral, no 'and' or 'or'
            "department != 'sales' or age < 30"  # contains 'or'
        ]

        # Combine the rules
        combined_ast = combine_rules(rules)

        # Ensure the combined AST is not None
        self.assertIsNotNone(combined_ast, "Combined AST should not be None")

        # Check that the root node of the AST is an operator (since multiple rules are being combined)
        self.assertEqual(combined_ast.type, "operator", "Root node should be of type 'operator'")

        # Calculate the most frequent operator ('and' should occur more in this case)
        operator_count = Counter()
        for rule in rules:
            tokens = tokenize(rule)
            operator_count.update([token for token in tokens if token in ["and", "or"]])

        most_frequent_operator = operator_count.most_common(1)[0][0]

        # Ensure the most frequent operator is used in the combined AST
        self.assertEqual(combined_ast.value, most_frequent_operator, f"The combined operator should be '{most_frequent_operator}'")

        # Convert the combined AST back to a string for verification
        combined_rule_string = ast_to_string(combined_ast)

        # Expected logic must contain the original conditions, combined with the most frequent operator
        expected_substrings = [
            "(age > 20 or experience >= 3",
            "salary <= 60000",
            "department != 'sales' or age < 30"
        ]

        # Ensure each individual rule is present in the combined rule
        for substring in expected_substrings:
            self.assertIn(substring, combined_rule_string, f"Combined rule should contain '{substring}'")

        # Print the combined rule string to inspect the output (for visual confirmation)
        print("\nCombined Rule String (Most Frequent Operator Used):")
        print(combined_rule_string)

# Run the test
if __name__ == '__main__':
    unittest.main()
