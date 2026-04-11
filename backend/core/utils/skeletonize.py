import ast
import sys
import os
import logging

# Configure logging for CLI output
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def skeletonize(filepath):
    """
    Extracts Class and Function signatures + Docstrings from a Python file.
    Designed for Dev-Time Token Optimization.
    """
    if not os.path.exists(filepath):
        logger.error(f"Error: File {filepath} not found.")
        return

    try:
        with open(filepath, "r", encoding="utf-8-sig") as f:
            tree = ast.parse(f.read())
    except Exception as e:
        logger.error(f"Error parsing {filepath}: {e}")
        return

    def get_docstring(node):
        doc = ast.get_docstring(node)
        return f'    """{doc}"""' if doc else ""

    logger.info(f"# Skeleton of {os.path.basename(filepath)}")

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            logger.info(f"\nclass {node.name}:")
            doc = get_docstring(node)
            if doc:
                logger.info(doc)

            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    args = ast.unparse(item.args)
                    logger.info(f"  def {item.name}({args}):")
                    item_doc = get_docstring(item)
                    if item_doc:
                        logger.info(f"  {item_doc}")

        elif isinstance(node, ast.FunctionDef):
            args = ast.unparse(node.args)
            logger.info(f"\ndef {node.name}({args}):")
            doc = get_docstring(node)
            if doc:
                logger.info(doc)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.info("Usage: python skeletonize.py <file_path>")
    else:
        skeletonize(sys.argv[1])
