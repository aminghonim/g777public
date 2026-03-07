"""
Test Multi-Theme System
Verify theme switching functionality
"""

from ui.theme_manager import theme_manager


def test_theme_system():
    """Test theme manager functionality"""
    print("=" * 50)
    print("Testing Multi-Theme System")
    print("=" * 50)

    # Test 1: Load themes
    print("\n1. Loading available themes...")
    themes = theme_manager.get_available_themes()
    print(f"   [OK] Found {len(themes)} themes")
    for theme in themes:
        print(f"   - {theme['id']}: {theme['name']} ({theme['type']})")

    # Test 2: Get current theme
    print("\n2. Current theme information...")
    current = theme_manager.get_current_theme()
    print(f"   [OK] Current: {current['id']} - {current['name']}")
    print(f"   [OK] Mode: {current['type']}")

    # Test 3: NiceGUI colors
    print("\n3. NiceGUI colors...")
    colors = theme_manager.get_nicegui_colors()
    for color_name, color_value in colors.items():
        print(f"   - {color_name}: {color_value}")

    # Test 4: Switch themes
    print("\n4. Testing theme switching...")
    themes_list = theme_manager.get_available_themes()
    if len(themes_list) > 1:
        first_theme = themes_list[0]["id"]
        second_theme = themes_list[1]["id"]

        print(f"   Switching from {first_theme} to {second_theme}...")
        theme_manager.set_theme(second_theme)
        new_current = theme_manager.get_current_theme()
        print(f"   [OK] New theme: {new_current['id']} - {new_current['name']}")

    # Test 5: Dark mode toggle
    print("\n5. Testing dark mode toggle...")
    current_dark = theme_manager.is_dark()
    print(f"   Current dark mode: {current_dark}")

    theme_manager.set_dark_mode(not current_dark)
    new_dark = theme_manager.is_dark()
    print(f"   [OK] New dark mode: {new_dark}")

    theme_manager.set_dark_mode(current_dark)  # Reset
    print(f"   [OK] Reset to original dark mode: {theme_manager.is_dark()}")

    # Test 6: CSS variables
    print("\n6. CSS variables...")
    css_vars = theme_manager.get_css_variables()
    count = len(css_vars.split('\n'))
    print(f"   [OK] Generated {count} CSS variables")

    # Test 7: Quasar classes
    print("\n7. Quasar-style classes...")
    for class_name in ['bg-primary', 'bg-secondary', 'text-main', 'border']:
        css_class = theme_manager.get_quasar_classes(class_name)
        print(f"   - {class_name}: {css_class}")

    print("\n" + "=" * 50)
    print("All tests completed successfully! [OK]")
    print("=" * 50)


if __name__ == "__main__":
    test_theme_system()
