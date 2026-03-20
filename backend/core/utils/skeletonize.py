import ast
import sys
import os
import logging
from typing import Optional, Union

# Initialize logger
logger = logging.getLogger(__name__)

def skeletonize(filepath: str) -> Optional[str]:
    """
    Extracts Class and Function signatures + Docstrings from a Python file.
    Designed for Dev-Time Token Optimization.
    Returns the skeleton as a string or None if file not found.
    """
    if not os.path.exists(filepath):
        logger.error(f"File {filepath} not found.")
        return None

    try:
        with open(filepath, "r", encoding="utf-8-sig") as f:
            tree = ast.parse(f.read())
    except (OSError, SyntaxError) as e:
        logger.error(f"Error parsing {filepath}: {e}")
        return None

    skeleton_lines = [f"# Skeleton of {os.path.basename(filepath)}"]

    def get_docstring(node: ast.AST) -> str:
        doc = ast.get_docstring(node)
        return f'    """{doc}"""' if doc else ""

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            skeleton_lines.append(f"\nclass {node.name}:")
            doc = get_docstring(node)
            if doc:
                skeleton_lines.append(doc)

            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    prefix = "async def" if isinstance(item, ast.AsyncFunctionDef) else "def"
                    args = ast.unparse(item.args)
                    skeleton_lines.append(f"  {prefix} {item.name}({args}):")
                    item_doc = get_docstring(item)
                    if item_doc:
                        skeleton_lines.append(f"  {item_doc}")

        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
            args = ast.unparse(node.args)
            skeleton_lines.append(f"\n{prefix} {node.name}({args}):")
            doc = get_docstring(node)
            if doc:
                skeleton_lines.append(doc)

    return "\n".join(skeleton_lines)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    if len(sys.argv) < 2:
        logger.error("Usage: python skeletonize.py <file_path>")
        sys.exit(1)
    else:
        result = skeletonize(sys.argv[1])
        if result:
            logger.info(result)
        else:
            sys.exit(1)
