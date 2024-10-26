import unittest
from collections import Counter

from corelogic_without_streamlit_for_testing import create_rule, ast_to_string, combine_rules, tokenize
class TestCombineRulesExtended(unittest.TestCase):
    def test_combine_additional_rules(self):
        # Additional complex rules to combine
        rules = [
            "age > 25 and experience >= 5",        # contains 'and'
            "salary <= 70000 or experience > 5000",      # contains 'or'
            "department = 'engineering'",           # neutral, no 'and' or 'or'
            "age < 40 and experience < 10"      # contains 'and'
       
        ]

        # Print input rules
        print("Input Rules:")
        for rule in rules:
            print(f"- {rule}")

        # Try to combine the rules and add debug statements to check AST generation
        rule_asts = []
        for rule in rules:
            ast = create_rule(rule)
            if ast is None:
                print(f"Error: Rule '{rule}' could not be parsed into an AST.")
            else:
                print(f"Rule '{rule}' successfully parsed into AST: {ast_to_string(ast)}")
                rule_asts.append(ast)

        # Now that we know which ASTs are valid, proceed with combining
        combined_ast = combine_rules(rules)

        # Ensure the combined AST is not None
        self.assertIsNotNone(combined_ast, "Combined AST should not be None")

        # Convert the combined AST back to a string for verification
        combined_rule_string = ast_to_string(combined_ast)

        # Print the combined rule string to inspect the output (for visual confirmation)
        print("\nCombined Rule String (Extended Rules):")
        print(combined_rule_string)

# Run the test case
if __name__ == '__main__':
    unittest.main()
