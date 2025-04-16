# -*- coding: UTF-8 -*-

import sys
import threading
from styles import dark_stylesheet
from pathlib import Path
from os import path
import pytest

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QTextEdit,
    QLabel,
    QFileDialog,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QHBoxLayout,
    QCheckBox,
    QSplitter,
)
from PySide6.QtCore import Signal, QObject, Qt, QSize
from PySide6.QtGui import QIcon


class SignalEmitter(QObject):
    log_signal = Signal(str)
    update_status_signal = Signal(str, str)  # test_name, status


class TestApp(QWidget):
    def __init__(self):
        """Initialize the main application window, set up the layout and connect signals."""
        super().__init__()

        self.setWindowTitle("Website Testing Tracker")
        self.test_directory = Path("tests")

        self.layout = QVBoxLayout()

        self.status_label = QLabel("Status: Idle")
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)

        self.test_table = QTableWidget()
        self.test_table.setColumnCount(4)
        self.test_table.setHorizontalHeaderLabels(
            ["Run", "Test File", "Test Function", "Status"]
        )

        self.test_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeToContents
        )
        self.test_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.test_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.test_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.run_button = QPushButton("Run Selected Tests")
        self.change_dir_button = QPushButton(" Change Test Directory")
        self.run_button.setIcon(QIcon(self.path_to_file("assets/play.svg")))
        self.run_button.setIconSize(QSize(25, 25))
        self.change_dir_button.setIcon(QIcon(self.path_to_file("assets/folder.svg")))
        self.change_dir_button.setIconSize(QSize(25, 25))

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.run_button)
        button_layout.addWidget(self.change_dir_button)

        self.layout.addWidget(self.status_label)

        # Splitter to allow resizing between test table and log output
        splitter = QSplitter(Qt.Vertical)

        # Top widget: test table + buttons
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.addWidget(self.test_table)
        top_layout.addLayout(button_layout)
        top_layout.setContentsMargins(0, 0, 0, 0)

        # Bottom widget: text output
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        bottom_layout.addWidget(self.text_area)
        bottom_layout.setContentsMargins(0, 0, 0, 0)

        # Add both to splitter
        splitter.addWidget(top_widget)
        splitter.addWidget(bottom_widget)
        splitter.setSizes([400, 200])  # Initial sizes

        self.layout.addWidget(splitter)

        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)

        self.setLayout(self.layout)

        self.run_button.clicked.connect(self.run_selected_tests)
        self.change_dir_button.clicked.connect(self.change_test_directory)

        self.signals = SignalEmitter()
        self.signals.log_signal.connect(self.log_output)
        self.signals.update_status_signal.connect(self.update_test_status)

        self.scan_test_directory()

    def path_to_file(self, filename):
        """Return the absolute path of the file in the assets folder.

        Args:
            filename (str): The filename to find the path for."""
        return path.abspath(path.join(path.dirname(__file__), filename))

    def log_output(self, text):
        """Append log messages to the text display area.

        Args:
            text (str): The message to display in the text area.
        """
        self.text_area.append(text)

    def update_test_status(self, test_name, status):
        """Update the status column of the given test in the table.

        Args:
            test_name (str): The name of the test file.
            status (str): 'Passed' or 'Failed'
        """
        for row in range(self.test_table.rowCount()):
            row_text = self.test_table.item(row, 1).text() + "::"
            row_text += self.test_table.item(row, 2).text()
            if row_text == test_name:
                self.test_table.setItem(row, 3, QTableWidgetItem(status))
                break

    def change_test_directory(self):
        """Open a file dialog to let the user select a new test directory,
        then scan it for test files.
        """
        dir_path = QFileDialog.getExistingDirectory(self, "Select Test Directory")
        if dir_path:
            self.test_directory = Path(dir_path)
            self.scan_test_directory()

    def scan_test_directory(self):
        """Scan the current test directory for Python test files and list them in the GUI."""
        self.test_table.setRowCount(0)
        if not self.test_directory.exists():
            self.signals.log_signal.emit(
                f"Test directory not found: {self.test_directory}"
            )
            return

        import ast

        for file in self.test_directory.glob("test_*.py"):
            with open(file, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=file.name)

            for node in tree.body:
                if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                    test_name = f"{file.name}::{node.name}"
                    row_pos = self.test_table.rowCount()
                    self.test_table.insertRow(row_pos)

                    checkbox = QCheckBox()
                    checkbox.setChecked(True)
                    checkbox.setStyleSheet(
                        "QCheckBox { margin-left:auto; margin-right:auto; }"
                    )
                    checkbox_container = QWidget()
                    layout = QHBoxLayout(checkbox_container)
                    layout.addWidget(checkbox)
                    layout.setAlignment(Qt.AlignCenter)
                    layout.setContentsMargins(8, 0, 0, 0)
                    self.test_table.setCellWidget(row_pos, 0, checkbox_container)

                    file_name, func_name = test_name.split("::")
                    self.test_table.setItem(row_pos, 1, QTableWidgetItem(file_name))
                    self.test_table.setItem(row_pos, 2, QTableWidgetItem(func_name))
                    self.test_table.setItem(row_pos, 3, QTableWidgetItem("Untested"))

            self.test_table.setAlternatingRowColors(True)
            tab_sty = """QTableWidget { alternate-background-color: #333; background-color: #2b2b2b; }"""
            self.test_table.setStyleSheet(tab_sty)

    def run_selected_tests(self):
        """Run all selected test files in a background thread."""
        selected_tests = []
        for row in range(self.test_table.rowCount()):
            checkbox_widget = self.test_table.cellWidget(row, 0)
            checkbox = checkbox_widget.findChild(QCheckBox)
            if checkbox and checkbox.isChecked():
                test_file = self.test_table.item(row, 1).text()
                test_file += "::"
                test_file += self.test_table.item(row, 2).text()
                selected_tests.append(test_file)

        if not selected_tests:
            self.signals.log_signal.emit("No tests selected.")
            return

        self.status_label.setText("Status: Running tests...")
        threading.Thread(target=self._execute_tests, args=(selected_tests,)).start()

    def run_pytest(test_args: list[str]) -> int:
        """Run pytest with the given arguments and return the exit code."""
        return pytest.main(test_args)

    def _execute_tests(self, test_files):
        """Execute each test file using pytest and stream output to the GUI."""
        for test_file in test_files:
            # file_path = self.test_directory / test_file
            self.signals.log_signal.emit(f"\nRunning {test_file}...")

            test_py, test_mod = str(test_file).split("::")
            test_py = path.abspath(path.join(self.test_directory, test_py))

            # Run pytest directly
            result = pytest.main([test_py, "-k", test_mod], plugins=[])

            if result == 0:
                self.signals.update_status_signal.emit(test_file, "✅ Passed")
            else:
                self.signals.update_status_signal.emit(test_file, "❌ Failed")

        self.signals.log_signal.emit("\nAll selected tests completed.")
        self.status_label.setText("Status: Idle")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(dark_stylesheet)
    window = TestApp()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())
