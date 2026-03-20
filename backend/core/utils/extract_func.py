import ast
import sys
import os
import logging

# Initialize logger
logger = logging.getLogger(__name__)

def extract_function(filepath: str, func_name: str) -> str:
    """Extract and return ONLY the source code of a specific function from a file."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File '{filepath}' not found.")

    with open(filepath, "r", encoding="utf-8-sig") as f:
        source_lines = f.readlines()
        source = "".join(source_lines)

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        logger.error(f"Failed to parse '{filepath}': {e}")
        raise

    for node in ast.walk(tree):
        if (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == func_name
        ):
            start = node.lineno - 1
            # end_lineno is available in Python 3.8+
            end = node.end_lineno if hasattr(node, 'end_lineno') else start + 1
            
            header = f"# {os.path.basename(filepath)} :: {func_name} (L{node.lineno}-L{end})\n"
            content = "".join(source_lines[start:end])
            return f"{header}{content}"

    raise NameError(f"Function '{func_name}' not found in '{filepath}'.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    if len(sys.argv) != 3:
        logger.error("Usage: python3 extract_func.py <filepath> <function_name>")
        sys.exit(1)
    try:
        logger.info(extract_function(sys.argv[1], sys.argv[2]))
    except Exception as e:
        logger.error(str(e))
        sys.exit(1)
