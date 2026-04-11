import ast
import sys
import os
import logging

# Configure logging for CLI output
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def extract_function(filepath: str, func_name: str) -> None:
    """Extract and print ONLY the source code of a specific function from a file."""
    if not os.path.exists(filepath):
        logger.error(f"Error: File '{filepath}' not found.")
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8-sig") as f:
        source_lines = f.readlines()
        source = "".join(source_lines)

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        logger.error(f"Error: Failed to parse '{filepath}': {e}")
        sys.exit(1)

    for node in ast.walk(tree):
        if (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == func_name
        ):
            start = node.lineno - 1
            end = node.end_lineno
            logger.info(
                f"# {os.path.basename(filepath)} :: {func_name} (L{node.lineno}-L{end})"
            )
            logger.info("".join(source_lines[start:end]))
            return

    logger.error(f"Error: Function '{func_name}' not found in '{filepath}'.")
    sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        logger.info("Usage: python3 extract_func.py <filepath> <function_name>")
        sys.exit(1)
    extract_function(sys.argv[1], sys.argv[2])
