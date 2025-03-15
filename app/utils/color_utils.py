from typing import Tuple, Dict, Any
import re

def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color code to RGB tuple"""
    # Remove # if present
    hex_color = hex_color.lstrip('#')
    
    # Parse hex values
    if len(hex_color) == 3:
        # Handle shorthand hex (#RGB)
        r = int(hex_color[0] + hex_color[0], 16)
        g = int(hex_color[1] + hex_color[1], 16)
        b = int(hex_color[2] + hex_color[2], 16)
    else:
        # Handle full hex (#RRGGBB)
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
    
    return (r, g, b)

def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """Convert RGB tuple to hex color code"""
    r, g, b = rgb
    return f"#{r:02x}{g:02x}{b:02x}"

def darken_color(hex_color: str, factor: float = 0.2) -> str:
    """Darken a color by the given factor (0-1)"""
    r, g, b = hex_to_rgb(hex_color)
    r = max(0, int(r * (1 - factor)))
    g = max(0, int(g * (1 - factor)))
    b = max(0, int(b * (1 - factor)))
    return rgb_to_hex((r, g, b))

def lighten_color(hex_color: str, factor: float = 0.2) -> str:
    """Lighten a color by the given factor (0-1)"""
    r, g, b = hex_to_rgb(hex_color)
    r = min(255, int(r + (255 - r) * factor))
    g = min(255, int(g + (255 - g) * factor))
    b = min(255, int(b + (255 - b) * factor))
    return rgb_to_hex((r, g, b))

def generate_color_palette(primary_color: str) -> Dict[str, str]:
    """
    Generate a color palette based on a primary color
    Returns primary, primary-light, primary-dark, and complementary colors
    """
    palette = {
        "primary": primary_color,
        "primary-light": lighten_color(primary_color, 0.3),
        "primary-dark": darken_color(primary_color, 0.3),
    }
    
    # Generate complementary color (opposite on the color wheel)
    r, g, b = hex_to_rgb(primary_color)
    complementary = rgb_to_hex((255 - r, 255 - g, 255 - b))
    palette["complementary"] = complementary
    
    return palette

def validate_hex_color(color: str) -> bool:
    """Validate if string is a proper hex color code"""
    pattern = r'^#(?:[0-9a-fA-F]{3}){1,2}$'
    return bool(re.match(pattern, color))

def generate_css_variables(design_system: Dict[str, Any]) -> str:
    """Generate CSS variables from a design system configuration"""
    css = ":root {\n"
    
    # Color variables
    for key, value in design_system["colors"].items():
        css += f"  --color-{key}: {value};\n"
    
    # Dark mode variables
    for key, value in design_system["dark_mode"].items():
        css += f"  --dark-{key}: {value};\n"
    
    # Typography variables
    for key, value in design_system["typography"].items():
        css += f"  --typography-{key.replace('_', '-')}: {value};\n"
    
    # Spacing variables
    for key, value in design_system["spacing"].items():
        css += f"  --spacing-{key.replace('_', '-')}: {value};\n"
    
    # Border radius variables
    for key, value in design_system["border_radius"].items():
        css += f"  --radius-{key}: {value};\n"
    
    css += "}\n"
    
    # Add dark mode
    css += "\n@media (prefers-color-scheme: dark) {\n"
    css += "  :root {\n"
    css += f"    --color-background: {design_system['dark_mode']['background']};\n"
    css += f"    --color-text: {design_system['dark_mode']['text']};\n"
    css += f"    --color-primary: {design_system['dark_mode']['primary']};\n"
    css += "  }\n"
    css += "}\n"
    
    return css