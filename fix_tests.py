import re

files = [
    "tests/test_database_core.py",
    "tests/test_database_manager.py",
    "tests/test_database_manager_class_surgical.py",
]


def fix_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    # Clean up the previous bad kwarg injection
    content = content.replace(', user_id="test_user"', "")
    content = content.replace(',\n        user_id="test_user"', "")

    # Now formally inject "test_user" as the SECOND positional arg.
    # Pattern: method_name("literal" OR 'literal', ... )

    # upsert_customer
    content = re.sub(
        r"(upsert_customer\s*\(\s*[\"\'][+\w]+[\"\'])\s*,", r'\1, "test_user",', content
    )

    # save_interaction
    content = re.sub(
        r"(save_interaction\s*\(\s*[\"\'][\w-]+[\"\'])\s*,",
        r'\1, "test_user",',
        content,
    )

    # get_customer_interactions
    content = re.sub(
        r"(get_customer_interactions\s*\(\s*[\"\'][\w-]+[\"\'])\s*,",
        r'\1, "test_user",',
        content,
    )
    content = re.sub(
        r"(get_customer_interactions\s*\(\s*[\"\'][\w-]+[\"\'])\s*\)",
        r'\1, "test_user")',
        content,
    )

    # save_analytics
    content = re.sub(
        r"(save_analytics\s*\(\s*[\"\'][\w-]+[\"\'])\s*,", r'\1, "test_user",', content
    )

    # get_customer_by_phone
    content = re.sub(
        r"(get_customer_by_phone\s*\(\s*[\"\'][+\w]+[\"\'])\s*,",
        r'\1, "test_user",',
        content,
    )
    content = re.sub(
        r"(get_customer_by_phone\s*\(\s*[\"\'][+\w]+[\"\'])\s*\)",
        r'\1, "test_user")',
        content,
    )

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)


for f in files:
    fix_file(f)
