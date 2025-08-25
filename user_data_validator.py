import json
import re

def load_schema(schema_path):
    """Load the user data schema from a JSON file."""
    with open(schema_path, 'r') as f:
        return json.load(f)

def validate_field(field, value, spec):
    """Validate a single field value according to its spec."""
    errors = []
    if 'type' in spec:
        if spec['type'] == 'string':
            if not isinstance(value, str):
                errors.append(f"{field} should be a string.")
        elif spec['type'] == 'integer':
            if not isinstance(value, int):
                errors.append(f"{field} should be an integer.")
        elif spec['type'] == 'boolean':
            if not isinstance(value, bool):
                errors.append(f"{field} should be a boolean.")
        # Add other types as needed

    if 'min_length' in spec and isinstance(value, str):
        if len(value) < spec['min_length']:
            errors.append(f"{field} should be at least {spec['min_length']} characters.")

    if 'max_length' in spec and isinstance(value, str):
        if len(value) > spec['max_length']:
            errors.append(f"{field} should be at most {spec['max_length']} characters.")

    if 'pattern' in spec and isinstance(value, str):
        if not re.match(spec['pattern'], value):
            errors.append(f"{field} does not match required pattern.")

    if 'enum' in spec:
        if value not in spec['enum']:
            errors.append(f"{field} must be one of {spec['enum']}.")

    if 'minimum' in spec and isinstance(value, int):
        if value < spec['minimum']:
            errors.append(f"{field} must be at least {spec['minimum']}.")

    if 'maximum' in spec and isinstance(value, int):
        if value > spec['maximum']:
            errors.append(f"{field} must be at most {spec['maximum']}.")

    return errors

def validate_data(schema, user_data):
    """Validate user_data dict according to schema."""
    errors = []
    for field, spec in schema.get('properties', {}).items():
        if field not in user_data:
            if schema.get('required', []) and field in schema['required']:
                errors.append(f"{field} is required.")
            continue
        errors.extend(validate_field(field, user_data[field], spec))
    return errors

def generate_test_cases(schema):
    """Generate test cases from schema."""
    cases = []
    # Generate basic valid case
    valid_case = {}
    for field, spec in schema.get('properties', {}).items():
        if spec['type'] == 'string':
            if 'enum' in spec:
                valid_case[field] = spec['enum'][0]
            elif 'min_length' in spec:
                valid_case[field] = "x" * spec['min_length']
            else:
                valid_case[field] = "test"
        elif spec['type'] == 'integer':
            valid_case[field] = spec.get('minimum', 0)
        elif spec['type'] == 'boolean':
            valid_case[field] = True
        else:
            valid_case[field] = None
    cases.append(('Valid case', valid_case))

    # Generate invalid cases for each rule
    for field, spec in schema.get('properties', {}).items():
        if spec['type'] == 'string':
            if 'min_length' in spec:
                invalid = valid_case.copy()
                invalid[field] = ""
                cases.append((f"{field}: too short", invalid))
            if 'pattern' in spec:
                invalid = valid_case.copy()
                invalid[field] = "invalid"
                cases.append((f"{field}: invalid pattern", invalid))
        if spec['type'] == 'integer':
            if 'minimum' in spec:
                invalid = valid_case.copy()
                invalid[field] = spec['minimum'] - 1
                cases.append((f"{field}: below minimum", invalid))
            if 'maximum' in spec:
                invalid = valid_case.copy()
                invalid[field] = spec['maximum'] + 1
                cases.append((f"{field}: above maximum", invalid))
        if 'enum' in spec:
            invalid = valid_case.copy()
            invalid[field] = "not-in-enum"
            cases.append((f"{field}: not in enum", invalid))
    return cases

def run_test_cases(schema, cases):
    """Run all test cases and print results."""
    for name, case in cases:
        errors = validate_data(schema, case)
        print(f"Test case: {name}")
        print("Input:", case)
        if errors:
            print("Errors:", errors)
        else:
            print("Valid!")
        print("-" * 40)

def manual_test_case_input(schema):
    """Prompt user to enter custom test case."""
    user_data = {}
    for field, spec in schema.get('properties', {}).items():
        value = input(f"Enter value for {field} ({spec['type']}): ")
        if spec['type'] == 'integer':
            try:
                value = int(value)
            except ValueError:
                print(f"Invalid integer for {field}, using 0.")
                value = 0
        elif spec['type'] == 'boolean':
            value = value.lower() in ['true', '1', 'yes']
        user_data[field] = value
    return user_data

def main():
    schema_path = input("Enter schema JSON path (default: user_schema.json): ").strip() or "user_schema.json"
    schema = load_schema(schema_path)
    cases = generate_test_cases(schema)
    run_test_cases(schema, cases)

    while True:
        custom = input("Do you want to enter a custom test case? (y/n): ").strip().lower()
        if custom == 'y':
            case = manual_test_case_input(schema)
            errors = validate_data(schema, case)
            print("Custom test case input:", case)
            if errors:
                print("Errors:", errors)
            else:
                print("Valid!")
            print("-" * 40)
        else:
            break

if __name__ == "__main__":
    main()