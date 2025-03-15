from typing import Tuple, Dict, Any
import re

def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        r = int(hex_color[0] + hex_color[0], 16)
        g = int(hex_color[1] + hex_color[1], 16)
        b = int(hex_color[2] + hex_color[2], 16)
    else:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
    return (r, g, b)

def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    r, g, b = rgb
    return f"#{r:02x}{g:02x}{b:02x}"

def darken_color(hex_color: str, factor: float = 0.2) -> str:
    r, g, b = hex_to_rgb(hex_color)
    r = max(0, int(r * (1 - factor)))
    g = max(0, int(g * (1 - factor)))
    b = max(0, int(b * (1 - factor)))
    return rgb_to_hex((r, g, b))

def lighten_color(hex_color: str, factor: float = 0.2) -> str:
    r, g, b = hex_to_rgb(hex_color)
    r = min(255, int(r + (255 - r) * factor))
    g = min(255, int(g + (255 - g) * factor))
    b = min(255, int(b + (255 - b) * factor))
    return rgb_to_hex((r, g, b))

def generate_color_palette(primary_color: str) -> Dict[str, str]:
    palette = {
        "primary": primary_color,
        "primary-light": lighten_color(primary_color, 0.3),
        "primary-dark": darken_color(primary_color, 0.3),
    }
    r, g, b = hex_to_rgb(primary_color)
    complementary = rgb_to_hex((255 - r, 255 - g, 255 - b))
    palette["complementary"] = complementary
    return palette

def validate_hex_color(color: str) -> bool:
    pattern = r'^#(?:[0-9a-fA-F]{3}){1,2}$'
    return bool(re.match(pattern, color))

def generate_css_variables(design_system: Dict[str, Any]) -> str:
    css = ":root {\n"
    for key, value in design_system["colors"].items():
        css += f"  --color-{key}: {value};\n"
    for key, value in design_system["dark_mode"].items():
        css += f"  --dark-{key}: {value};\n"
    for key, value in design_system["typography"].items():
        css += f"  --typography-{key.replace('_', '-')}: {value};\n"
    for key, value in design_system["spacing"].items():
        css += f"  --spacing-{key.replace('_', '-')}: {value};\n"
    for key, value in design_system["border_radius"].items():
        css += f"  --radius-{key}: {value};\n"
    css += "}\n"
    css += "\n@media (prefers-color-scheme: dark) {\n"
    css += "  :root {\n"
    css += f"    --color-background: {design_system['dark_mode']['background']};\n"
    css += f"    --color-text: {design_system['dark_mode']['text']};\n"
    css += f"    --color-primary: {design_system['dark_mode']['primary']};\n"
    css += "  }\n"
    css += "}\n"
    return css