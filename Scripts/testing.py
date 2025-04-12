import hashlib

birth_date = "2095-01-28"
family_name = "Patient_10104335"
identifier_value = "10104335"
raw_password = f"{birth_date}{family_name}"
salted_input = f"{identifier_value}:{raw_password}"
expected_hash = hashlib.sha256(salted_input.encode()).hexdigest()
print(expected_hash)
