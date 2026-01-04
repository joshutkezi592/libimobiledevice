#!/usr/bin/env python3
"""iOS Forensic Imager - Professional Edition"""
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt6.QtCore import Qt

class ForensicImagerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('iOS Forensic Imager - Professional')
        self.setMinimumSize(1400, 900)
        label = QLabel('New Professional GUI - Under Construction')
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(label)

def main():
    app = QApplication(sys.argv)
    window = ForensicImagerWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
