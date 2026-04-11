"""
Figma Converter
Converts Figma JSON Nodes into NiceGUI Python code string.
"""
from typing import Dict, Any, List

class FigmaConverter:
    def __init__(self):
        self.generated_code = []
        self.indent_level = 0

    def convert_node(self, node: Dict[str, Any]) -> str:
        """
        Main entry point to convert a node tree to Python code.
        """
        self.generated_code = []
        self.indent_level = 0
        
        # Start with a container
        self._add_line("with ui.card().classes('w-full h-full p-0 relative overflow-hidden'):")
        self.indent_level += 1
        
        self._process_node_recursive(node)
        
        return "\n".join(self.generated_code)

    def _process_node_recursive(self, node: Dict[str, Any]):
        node_type = node.get("type")
        name = node.get("name")
        
        # Basic mapping logic
        if node_type in ["FRAME", "COMPONENT", "INSTANCE", "GROUP"]:
            self._render_container(node)
        elif node_type == "TEXT":
            self._render_text(node)
        elif node_type == "RECTANGLE":
            self._render_rectangle(node)
        elif node_type == "VECTOR":
            # For now, ignore vectors or render as placeholders
            pass
        
        # Recursively process children
        if "children" in node:
            current_indent = self.indent_level
            # If we opened a context manager (like ui.row/column), indent is already increased
            # But we need to ensure we don't double indent if the container didn't open a new block (e.g. absolute positioning)
            
            for child in node["children"]:
                # Basic layout assumption: if parent is absolute, children just render.
                # Use absolute positioning for high fidelity if needed, but Flexbox is better for responsive.
                # For this v1, let's try to map to Flexbox where possible, or use absolute if "layoutMode" is missing.
                self._process_node_recursive(child)
            
            self.indent_level = current_indent

    def _render_container(self, node: Dict[str, Any]):
        """Render ui.row, ui.column, or simple div"""
        layout_mode = node.get("layoutMode") # NONE, HORIZONTAL, VERTICAL
        styles = self._get_styles(node)
        
        element = "ui.element('div')"
        if layout_mode == "HORIZONTAL":
            element = "ui.row()"
        elif layout_mode == "VERTICAL":
            element = "ui.column()"
            
        line = f"with {element}.classes('{styles}'):"
        self._add_line(line)
        self.indent_level += 1

    def _render_text(self, node: Dict[str, Any]):
        text_content = node.get("characters", "").replace("'", "\\'").replace("\n", "\\n")
        styles = self._get_text_styles(node)
        self._add_line(f"ui.label('{text_content}').style('{styles}')")

    def _render_rectangle(self, node: Dict[str, Any]):
        """Render a rectangle as a div"""
        styles = self._get_styles(node)
        self._add_line(f"ui.element('div').style('{styles}')")

    def _get_styles(self, node: Dict[str, Any]) -> str:
        """Extract CSS styles from Figma node"""
        styles = []
        
        # Dimensions
        absolute_bounding_box = node.get("absoluteBoundingBox", {})
        width = absolute_bounding_box.get("width")
        height = absolute_bounding_box.get("height")
        
        if width: styles.append(f"width: {width}px;")
        if height: styles.append(f"height: {height}px;")
        
        # Background color
        fills = node.get("fills", [])
        for fill in fills:
            if fill.get("type") == "SOLID" and fill.get("visible", True):
                color = fill.get("color")
                r, g, b = int(color["r"]*255), int(color["g"]*255), int(color["b"]*255)
                opacity = fill.get("opacity", 1.0)
                styles.append(f"background-color: rgba({r},{g},{b},{opacity});")
                break # Only one fill for now
        
        # Border
        strokes = node.get("strokes", [])
        for stroke in strokes:
             if stroke.get("type") == "SOLID" and stroke.get("visible", True):
                 color = stroke.get("color")
                 r, g, b = int(color["r"]*255), int(color["g"]*255), int(color["b"]*255)
                 weight = node.get("strokeWeight", 1)
                 styles.append(f"border: {weight}px solid rgb({r},{g},{b});")
                 break

        # Corner Radius
        radius = node.get("cornerRadius")
        if radius:
            styles.append(f"border-radius: {radius}px;")

        # Absolute Positioning (if parent has no auto-layout)
        # For simple mapping, we might verify parent layoutMode, but here we'll assume relative/absolute mix
        # x = node.get("x", 0)
        # y = node.get("y", 0)
        # styles.append(f"position: absolute; left: {x}px; top: {y}px;")

        return " ".join(styles)

    def _get_text_styles(self, node: Dict[str, Any]) -> str:
        """Extract text specific styles"""
        style = node.get("style", {})
        css = []
        
        font_size = style.get("fontSize")
        if font_size: css.append(f"font-size: {font_size}px;")
        
        font_weight = style.get("fontWeight")
        if font_weight: css.append(f"font-weight: {font_weight};")
        
        text_align = style.get("textAlignHorizontal", "LEFT").lower()
        if text_align == "center": css.append("text-align: center;")
        elif text_align == "right": css.append("text-align: right;")
        
        # Color
        fills = node.get("fills", [])
        for fill in fills:
            if fill.get("type") == "SOLID" and fill.get("visible", True):
                 color = fill.get("color")
                 r, g, b = int(color["r"]*255), int(color["g"]*255), int(color["b"]*255)
                 opacity = fill.get("opacity", 1.0)
                 css.append(f"color: rgba({r},{g},{b},{opacity});")
                 break
                 
        return " ".join(css)

    def _add_line(self, line: str):
        indent = "    " * self.indent_level
        self.generated_code.append(f"{indent}{line}")
