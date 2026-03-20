import ast
import sys
import os


def skeletonize(filepath):
    """
    Extracts Class and Function signatures + Docstrings from a Python file.
    Designed for Dev-Time Token Optimization.
    """
    if not os.path.exists(filepath):
        print(f"Error: File {filepath} not found.")
        return

    try:
        with open(filepath, "r", encoding="utf-8-sig") as f:
            tree = ast.parse(f.read())
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        return

    def get_docstring(node):
        doc = ast.get_docstring(node)
        return f'    """{doc}"""' if doc else ""

    print(f"# Skeleton of {os.path.basename(filepath)}")

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            print(f"\nclass {node.name}:")
            doc = get_docstring(node)
            if doc:
                print(doc)

            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    args = ast.unparse(item.args)
                    print(f"  def {item.name}({args}):")
                    item_doc = get_docstring(item)
                    if item_doc:
                        print(f"  {item_doc}")

        elif isinstance(node, ast.FunctionDef):
            args = ast.unparse(node.args)
            print(f"\ndef {node.name}({args}):")
            doc = get_docstring(node)
            if doc:
                print(doc)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python skeletonize.py <file_path>")
    else:
        skeletonize(sys.argv[1])
