#!/usr/bin/env python3
"""
iDevice Manager - A PyQt6 GUI for libimobiledevice
"""

import sys
import subprocess
import os
import shutil
import tempfile
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget, QTextEdit, QTabWidget,
    QTreeWidget, QTreeWidgetItem, QMessageBox, QFileDialog,
    QStatusBar, QToolBar, QSplitter, QGroupBox,
    QListWidgetItem, QProgressDialog
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QSize
from PyQt6.QtGui import QAction, QFont, QPalette, QColor, QPixmap


class DeviceScanner(QThread):
    """Background thread for scanning devices"""
    devices_found = pyqtSignal(list)
    
    def run(self):
        """Scan for connected devices"""
        try:
            result = subprocess.run(
                ['idevice_id', '-l'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                devices = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
                self.devices_found.emit(devices)
            else:
                self.devices_found.emit([])
        except Exception as e:
            print(f"Error scanning devices: {e}")
            self.devices_found.emit([])


class DeviceInfoWorker(QThread):
    """Background thread for fetching device information"""
    info_ready = pyqtSignal(str)
    
    def __init__(self, udid):
        super().__init__()
        self.udid = udid
    
    def run(self):
        """Fetch device information"""
        try:
            result = subprocess.run(
                ['ideviceinfo', '-u', self.udid],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                self.info_ready.emit(result.stdout)
            else:
                self.info_ready.emit(f"Error: {result.stderr}")
        except Exception as e:
            self.info_ready.emit(f"Error fetching device info: {e}")


class SyslogWorker(QThread):
    """Background thread for syslog monitoring"""
    log_line = pyqtSignal(str)
    
    def __init__(self, udid):
        super().__init__()
        self.udid = udid
        self.running = False
        self.process = None
    
    def run(self):
        """Monitor device syslog"""
        self.running = True
        try:
            self.process = subprocess.Popen(
                ['idevicesyslog', '-u', self.udid],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            while self.running and self.process.poll() is None:
                line = self.process.stdout.readline()
                if line:
                    self.log_line.emit(line.rstrip())
        except Exception as e:
            self.log_line.emit(f"Error: {e}")
    
    def stop(self):
        """Stop syslog monitoring"""
        self.running = False
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()


class iDeviceManagerGUI(QMainWindow):
    """Main GUI window for iDevice Manager"""
    
    def __init__(self):
        super().__init__()
        self.current_device = None
        self.syslog_worker = None
        self.init_ui()
        self.scan_devices()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("iDevice Manager")
        self.setGeometry(100, 100, 1200, 800)
        
        # Set modern styling
        self.set_modern_style()
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Left panel - Device list
        self.create_device_panel(main_layout)
        
        # Right panel - Tab widget for different functions
        self.create_function_panel(main_layout)
        
        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")
        
    def set_modern_style(self):
        """Apply modern styling to the application"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0051D5;
            }
            QPushButton:pressed {
                background-color: #003C9E;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QListWidget {
                background-color: white;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 4px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 3px;
            }
            QListWidget::item:selected {
                background-color: #007AFF;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #e8f4ff;
            }
            QTextEdit, QTreeWidget {
                background-color: white;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 4px;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #d0d0d0;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QTabWidget::pane {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border: 1px solid #d0d0d0;
                border-bottom-color: white;
            }
            QTabBar::tab:hover {
                background-color: #f0f0f0;
            }
            QToolBar {
                background-color: white;
                border-bottom: 1px solid #d0d0d0;
                spacing: 8px;
                padding: 4px;
            }
        """)
        
    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        refresh_action = QAction('Refresh Devices', self)
        refresh_action.setShortcut('F5')
        refresh_action.triggered.connect(self.scan_devices)
        file_menu.addAction(refresh_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Device menu
        device_menu = menubar.addMenu('Device')
        
        pair_action = QAction('Pair Device', self)
        pair_action.triggered.connect(self.pair_device)
        device_menu.addAction(pair_action)
        
        unpair_action = QAction('Unpair Device', self)
        unpair_action.triggered.connect(self.unpair_device)
        device_menu.addAction(unpair_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_toolbar(self):
        """Create the toolbar"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # Refresh button
        refresh_btn = QAction('Refresh', self)
        refresh_btn.triggered.connect(self.scan_devices)
        toolbar.addAction(refresh_btn)
        
        toolbar.addSeparator()
        
        # Screenshot button
        screenshot_btn = QAction('Screenshot', self)
        screenshot_btn.triggered.connect(self.take_screenshot)
        toolbar.addAction(screenshot_btn)
        
        # Reboot button
        reboot_btn = QAction('Reboot', self)
        reboot_btn.triggered.connect(self.reboot_device)
        toolbar.addAction(reboot_btn)
        
    def create_device_panel(self, parent_layout):
        """Create the device list panel"""
        device_group = QGroupBox("Connected Devices")
        device_layout = QVBoxLayout()
        
        self.device_list = QListWidget()
        self.device_list.itemClicked.connect(self.on_device_selected)
        device_layout.addWidget(self.device_list)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Devices")
        refresh_btn.clicked.connect(self.scan_devices)
        device_layout.addWidget(refresh_btn)
        
        device_group.setLayout(device_layout)
        device_group.setMaximumWidth(300)
        parent_layout.addWidget(device_group)
        
    def create_function_panel(self, parent_layout):
        """Create the function tabs panel"""
        self.tabs = QTabWidget()
        
        # Device Info Tab
        self.info_tab = self.create_info_tab()
        self.tabs.addTab(self.info_tab, "Device Info")
        
        # Screenshot Tab
        self.screenshot_tab = self.create_screenshot_tab()
        self.tabs.addTab(self.screenshot_tab, "Screenshot")
        
        # Syslog Tab
        self.syslog_tab = self.create_syslog_tab()
        self.tabs.addTab(self.syslog_tab, "Syslog")
        
        # Apps Tab
        self.apps_tab = self.create_apps_tab()
        self.tabs.addTab(self.apps_tab, "Apps")
        
        # File Browser Tab
        self.files_tab = self.create_files_tab()
        self.tabs.addTab(self.files_tab, "Files")
        
        parent_layout.addWidget(self.tabs)
        
    def create_info_tab(self):
        """Create device information tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setFont(QFont("Courier", 10))
        layout.addWidget(self.info_text)
        
        button_layout = QHBoxLayout()
        
        get_info_btn = QPushButton("Get Device Info")
        get_info_btn.clicked.connect(self.get_device_info)
        button_layout.addWidget(get_info_btn)
        
        copy_btn = QPushButton("Copy to Clipboard")
        copy_btn.clicked.connect(self.copy_info_to_clipboard)
        button_layout.addWidget(copy_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        tab.setLayout(layout)
        return tab
        
    def create_screenshot_tab(self):
        """Create screenshot tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Screenshot display
        self.screenshot_label = QLabel("No screenshot taken yet")
        self.screenshot_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.screenshot_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #d0d0d0;")
        self.screenshot_label.setMinimumHeight(400)
        layout.addWidget(self.screenshot_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        take_screenshot_btn = QPushButton("Take Screenshot")
        take_screenshot_btn.clicked.connect(self.take_screenshot)
        button_layout.addWidget(take_screenshot_btn)
        
        save_screenshot_btn = QPushButton("Save Screenshot")
        save_screenshot_btn.clicked.connect(self.save_screenshot)
        button_layout.addWidget(save_screenshot_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        tab.setLayout(layout)
        return tab
        
    def create_syslog_tab(self):
        """Create syslog monitoring tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        self.syslog_text = QTextEdit()
        self.syslog_text.setReadOnly(True)
        self.syslog_text.setFont(QFont("Courier", 9))
        layout.addWidget(self.syslog_text)
        
        button_layout = QHBoxLayout()
        
        self.start_syslog_btn = QPushButton("Start Syslog")
        self.start_syslog_btn.clicked.connect(self.start_syslog)
        button_layout.addWidget(self.start_syslog_btn)
        
        self.stop_syslog_btn = QPushButton("Stop Syslog")
        self.stop_syslog_btn.clicked.connect(self.stop_syslog)
        self.stop_syslog_btn.setEnabled(False)
        button_layout.addWidget(self.stop_syslog_btn)
        
        clear_btn = QPushButton("Clear Log")
        clear_btn.clicked.connect(self.syslog_text.clear)
        button_layout.addWidget(clear_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        tab.setLayout(layout)
        return tab
        
    def create_apps_tab(self):
        """Create apps management tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        self.apps_list = QListWidget()
        layout.addWidget(self.apps_list)
        
        button_layout = QHBoxLayout()
        
        list_apps_btn = QPushButton("List Apps")
        list_apps_btn.clicked.connect(self.list_apps)
        button_layout.addWidget(list_apps_btn)
        
        refresh_apps_btn = QPushButton("Refresh")
        refresh_apps_btn.clicked.connect(self.list_apps)
        button_layout.addWidget(refresh_apps_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        tab.setLayout(layout)
        return tab
        
    def create_files_tab(self):
        """Create file browser tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        info_label = QLabel("File browser functionality")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)
        
        self.files_tree = QTreeWidget()
        self.files_tree.setHeaderLabels(["Name", "Type", "Size"])
        layout.addWidget(self.files_tree)
        
        button_layout = QHBoxLayout()
        
        browse_btn = QPushButton("Browse AFC")
        browse_btn.clicked.connect(self.browse_files)
        button_layout.addWidget(browse_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        tab.setLayout(layout)
        return tab
        
    def scan_devices(self):
        """Scan for connected devices"""
        self.statusBar.showMessage("Scanning for devices...")
        self.device_list.clear()
        
        scanner = DeviceScanner()
        scanner.devices_found.connect(self.on_devices_scanned)
        scanner.finished.connect(scanner.deleteLater)
        scanner.start()
        
    def on_devices_scanned(self, devices):
        """Handle scanned devices"""
        if devices:
            for device in devices:
                item = QListWidgetItem(device)
                self.device_list.addItem(item)
            self.statusBar.showMessage(f"Found {len(devices)} device(s)")
        else:
            self.statusBar.showMessage("No devices found")
            
    def on_device_selected(self, item):
        """Handle device selection"""
        self.current_device = item.text()
        self.statusBar.showMessage(f"Selected device: {self.current_device}")
        
    def get_device_info(self):
        """Get information about the selected device"""
        if not self.current_device:
            QMessageBox.warning(self, "No Device", "Please select a device first")
            return
            
        self.info_text.clear()
        self.info_text.append("Fetching device information...\n")
        
        worker = DeviceInfoWorker(self.current_device)
        worker.info_ready.connect(self.display_device_info)
        worker.finished.connect(worker.deleteLater)
        worker.start()
        
    def display_device_info(self, info):
        """Display device information"""
        self.info_text.clear()
        self.info_text.append(info)
        
    def copy_info_to_clipboard(self):
        """Copy device info to clipboard"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.info_text.toPlainText())
        self.statusBar.showMessage("Copied to clipboard", 3000)
        
    def take_screenshot(self):
        """Take a screenshot from the device"""
        if not self.current_device:
            QMessageBox.warning(self, "No Device", "Please select a device first")
            return
            
        try:
            self.statusBar.showMessage("Taking screenshot...")
            
            # Create temp directory if it doesn't exist
            temp_dir = os.path.join(tempfile.gettempdir(), "idevice_screenshots")
            os.makedirs(temp_dir, exist_ok=True)
            
            screenshot_path = f"{temp_dir}/screenshot_{self.current_device}.png"
            
            result = subprocess.run(
                ['idevicescreenshot', '-u', self.current_device, screenshot_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and os.path.exists(screenshot_path):
                # Load and display screenshot
                pixmap = QPixmap(screenshot_path)
                scaled_pixmap = pixmap.scaled(
                    self.screenshot_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.screenshot_label.setPixmap(scaled_pixmap)
                self.current_screenshot = screenshot_path
                self.statusBar.showMessage("Screenshot taken successfully", 3000)
                
                # Switch to screenshot tab
                self.tabs.setCurrentWidget(self.screenshot_tab)
            else:
                QMessageBox.warning(self, "Error", f"Failed to take screenshot: {result.stderr}")
                self.statusBar.showMessage("Screenshot failed")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Screenshot error: {str(e)}")
            self.statusBar.showMessage("Screenshot failed")
            
    def save_screenshot(self):
        """Save the current screenshot"""
        if not hasattr(self, 'current_screenshot') or not os.path.exists(self.current_screenshot):
            QMessageBox.warning(self, "No Screenshot", "Please take a screenshot first")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Screenshot",
            f"screenshot_{self.current_device}.png",
            "PNG Images (*.png)"
        )
        
        if file_path:
            try:
                shutil.copy(self.current_screenshot, file_path)
                self.statusBar.showMessage(f"Screenshot saved to {file_path}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save screenshot: {str(e)}")
                
    def start_syslog(self):
        """Start monitoring device syslog"""
        if not self.current_device:
            QMessageBox.warning(self, "No Device", "Please select a device first")
            return
            
        if self.syslog_worker and self.syslog_worker.isRunning():
            return
            
        self.syslog_text.clear()
        self.syslog_worker = SyslogWorker(self.current_device)
        self.syslog_worker.log_line.connect(self.append_syslog_line)
        self.syslog_worker.start()
        
        self.start_syslog_btn.setEnabled(False)
        self.stop_syslog_btn.setEnabled(True)
        self.statusBar.showMessage("Syslog monitoring started")
        
    def stop_syslog(self):
        """Stop monitoring device syslog"""
        if self.syslog_worker:
            self.syslog_worker.stop()
            self.syslog_worker = None
            
        self.start_syslog_btn.setEnabled(True)
        self.stop_syslog_btn.setEnabled(False)
        self.statusBar.showMessage("Syslog monitoring stopped")
        
    def append_syslog_line(self, line):
        """Append a line to the syslog display"""
        self.syslog_text.append(line)
        # Auto-scroll to bottom
        scrollbar = self.syslog_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def list_apps(self):
        """List installed applications"""
        if not self.current_device:
            QMessageBox.warning(self, "No Device", "Please select a device first")
            return
            
        self.apps_list.clear()
        self.apps_list.addItem("Fetching app list...")
        
        try:
            # This is a placeholder - actual implementation would use installation_proxy
            result = subprocess.run(
                ['ideviceinfo', '-u', self.current_device, '-k', 'ProductName'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            self.apps_list.clear()
            if result.returncode == 0:
                self.apps_list.addItem("App listing feature requires additional implementation")
                self.apps_list.addItem(f"Device: {result.stdout.strip()}")
            else:
                self.apps_list.addItem("Unable to fetch app list")
        except Exception as e:
            self.apps_list.clear()
            self.apps_list.addItem(f"Error: {str(e)}")
            
    def browse_files(self):
        """Browse device files via AFC"""
        if not self.current_device:
            QMessageBox.warning(self, "No Device", "Please select a device first")
            return
            
        self.files_tree.clear()
        item = QTreeWidgetItem(["File browser requires AFC implementation", "", ""])
        self.files_tree.addTopLevelItem(item)
        
    def pair_device(self):
        """Pair with the selected device"""
        if not self.current_device:
            QMessageBox.warning(self, "No Device", "Please select a device first")
            return
            
        try:
            result = subprocess.run(
                ['idevicepair', '-u', self.current_device, 'pair'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                QMessageBox.information(self, "Success", "Device paired successfully")
            else:
                QMessageBox.warning(self, "Error", f"Failed to pair device:\n{result.stderr}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Pairing error: {str(e)}")
            
    def unpair_device(self):
        """Unpair the selected device"""
        if not self.current_device:
            QMessageBox.warning(self, "No Device", "Please select a device first")
            return
            
        reply = QMessageBox.question(
            self,
            "Confirm Unpair",
            "Are you sure you want to unpair this device?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                result = subprocess.run(
                    ['idevicepair', '-u', self.current_device, 'unpair'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    QMessageBox.information(self, "Success", "Device unpaired successfully")
                else:
                    QMessageBox.warning(self, "Error", f"Failed to unpair device:\n{result.stderr}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Unpairing error: {str(e)}")
                
    def reboot_device(self):
        """Reboot the selected device"""
        if not self.current_device:
            QMessageBox.warning(self, "No Device", "Please select a device first")
            return
            
        reply = QMessageBox.question(
            self,
            "Confirm Reboot",
            "Are you sure you want to reboot this device?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                result = subprocess.run(
                    ['idevicediagnostics', '-u', self.current_device, 'restart'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    QMessageBox.information(self, "Success", "Device reboot initiated")
                else:
                    QMessageBox.warning(self, "Error", f"Failed to reboot device:\n{result.stderr}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Reboot error: {str(e)}")
                
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About iDevice Manager",
            "<h2>iDevice Manager</h2>"
            "<p>A modern PyQt6 GUI for libimobiledevice</p>"
            "<p>Version 1.0</p>"
            "<p>Provides a user-friendly interface for managing iOS devices</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Device detection and information</li>"
            "<li>Screenshot capture</li>"
            "<li>Syslog monitoring</li>"
            "<li>App management</li>"
            "<li>File browsing</li>"
            "</ul>"
        )
        
    def closeEvent(self, event):
        """Handle window close event"""
        # Stop syslog if running
        if self.syslog_worker:
            self.syslog_worker.stop()
            
        event.accept()


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("iDevice Manager")
    
    # Check if required tools are available
    required_tools = ['idevice_id', 'ideviceinfo', 'idevicescreenshot']
    missing_tools = []
    
    for tool in required_tools:
        try:
            subprocess.run([tool, '--help'], capture_output=True, timeout=2)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            missing_tools.append(tool)
    
    if missing_tools:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Missing Tools")
        msg.setText("Some libimobiledevice tools are not available:")
        msg.setInformativeText("\n".join(missing_tools))
        msg.setDetailedText(
            "Please install libimobiledevice tools:\n"
            "Ubuntu/Debian: sudo apt-get install libimobiledevice-utils\n"
            "macOS: brew install libimobiledevice\n"
            "Or build from source: https://github.com/libimobiledevice/libimobiledevice"
        )
        msg.exec()
    
    window = iDeviceManagerGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
