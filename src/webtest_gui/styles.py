from os import path


def path_to_file(filename):
    """Return the absolute path of the file in the assets folder.

    Args:
        filename (str): The filename to find the path for."""

    assets_path = path.join(path.dirname(__file__), "assets")

    return path.abspath(path.join(assets_path, filename))


dark_stylesheet = f"""
QWidget {{
    background-color: #2b2b2b;
    color: #dddddd;
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
}}
QPushButton {{
    background-color: #444;
    border: 1px solid #666;
    padding: 6px;
    border-radius: 4px;
}}
QPushButton:hover {{
    background-color: #555;
}}
QTableWidget {{
    background-color: #3b3b3b;
    gridline-color: #666;
}}
QHeaderView::section {{
    background-color: #444;
    color: #ddd;
    padding: 4px;
    border: 1px solid #555;
}}
QTextEdit {{
    background-color: #1e1e1e;
    color: #eeeeee;
    border: 1px solid #555;
}}
QCheckBox {{
    spacing: 8px;
    color: #ffffff;
}}
QCheckBox::indicator:unchecked {{
    image: url({(path_to_file("circle.svg"))});
}}

QCheckBox::indicator:checked {{
    image: url({(path_to_file("check-circle.svg"))});
}}
"""
