import sys
import threading
import os
from pathlib import Path
import subprocess

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
)
from PySide6.QtCore import Signal, QObject, Qt
from PySide6.QtGui import QIcon


class SignalEmitter(QObject):
    log_signal = Signal(str)
    update_status_signal = Signal(str, str)  # test_name, status


class TestApp(QWidget):
    def __init__(self):
        """Initialize the main application window, set up the layout and connect signals."""
        super().__init__()
        self.setWindowTitle("Website Testing Tracker")
        self.setWindowIcon(QIcon("app_icon.png"))  # Set application icon for dock

        self.test_directory = Path("tests")

        self.layout = QVBoxLayout()

        self.status_label = QLabel("Status: Idle")
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)

        self.test_table = QTableWidget()
        self.test_table.setColumnCount(3)
        self.test_table.setHorizontalHeaderLabels(["Run", "Test File", "Status"])
        self.test_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeToContents
        )
        self.test_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.test_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.test_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.run_button = QPushButton("Run Selected Tests")
        self.change_dir_button = QPushButton("Change Test Directory")

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.run_button)
        button_layout.addWidget(self.change_dir_button)

        self.layout.addWidget(self.status_label)
        self.layout.addWidget(self.test_table)
        self.layout.addLayout(button_layout)
        self.layout.addWidget(self.text_area)

        self.setLayout(self.layout)

        self.run_button.clicked.connect(self.run_selected_tests)
        self.change_dir_button.clicked.connect(self.change_test_directory)

        self.signals = SignalEmitter()
        self.signals.log_signal.connect(self.log_output)
        self.signals.update_status_signal.connect(self.update_test_status)

        self.scan_test_directory()

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
            if self.test_table.item(row, 1).text() == test_name:
                self.test_table.setItem(row, 2, QTableWidgetItem(status))
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
        for file in self.test_directory.glob("test_*.py"):
            row_pos = self.test_table.rowCount()
            self.test_table.insertRow(row_pos)

            checkbox = QCheckBox()
            checkbox.setChecked(True)
            checkbox_widget = QWidget()
            layout = QHBoxLayout(checkbox_widget)
            layout.addWidget(checkbox)
            layout.setAlignment(Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            self.test_table.setCellWidget(row_pos, 0, checkbox_widget)

            self.test_table.setItem(row_pos, 1, QTableWidgetItem(file.name))
            self.test_table.setItem(row_pos, 2, QTableWidgetItem("Untested"))

    def run_selected_tests(self):
        """Run all selected test files in a background thread."""
        selected_tests = []
        for row in range(self.test_table.rowCount()):
            checkbox_widget = self.test_table.cellWidget(row, 0)
            checkbox = checkbox_widget.findChild(QCheckBox)
            if checkbox and checkbox.isChecked():
                test_file = self.test_table.item(row, 1).text()
                selected_tests.append(test_file)

        if not selected_tests:
            self.signals.log_signal.emit("No tests selected.")
            return

        self.status_label.setText("Status: Running tests...")
        threading.Thread(target=self._execute_tests, args=(selected_tests,)).start()

    def _execute_tests(self, test_files):
        """Execute each test file using pytest and stream output to the GUI."""
        for test_file in test_files:
            file_path = self.test_directory / test_file
            self.signals.log_signal.emit(f"\nRunning {test_file}...")

            # Run pytest and capture all output
            process = subprocess.Popen(
                ["pytest", str(file_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )

            output, _ = process.communicate()
            for line in output.splitlines():
                self.signals.log_signal.emit(line.strip())

            if process.returncode == 0:
                self.signals.update_status_signal.emit(test_file, "Passed")
            else:
                self.signals.update_status_signal.emit(test_file, "Failed")

        self.signals.log_signal.emit("\nAll selected tests completed.")
        self.status_label.setText("Status: Idle")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("app_icon.png"))
    window = TestApp()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())
