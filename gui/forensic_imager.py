#!/usr/bin/env python3
"""
iDevice Forensic Imager - A GUI tool for forensic imaging of Apple devices
Uses libimobiledevice for device communication

Copyright (c) 2024 libimobiledevice project
Licensed under the GNU Lesser General Public License v2.1
"""

import sys
import os
import subprocess
import json
import threading
import hashlib
import logging
import re
import uuid as uuid_lib
from datetime import datetime
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import tempfile
import shutil

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTreeWidget, QTreeWidgetItem, QLabel, QPushButton, QTextEdit,
    QTabWidget, QSplitter, QFileDialog, QProgressBar, QMessageBox,
    QStatusBar, QToolBar, QGroupBox, QFormLayout, QLineEdit,
    QComboBox, QCheckBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QMenu, QDialog, QDialogButtonBox, QPlainTextEdit, QFrame,
    QSpinBox, QListWidget, QListWidgetItem, QInputDialog, QStyle
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize, QDateTime
from PyQt6.QtGui import QAction, QIcon, QFont, QColor, QPixmap, QImage, QPalette

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


@dataclass
class DeviceInfo:
    """Device information structure"""
    udid: str
    name: str = ""
    product_type: str = ""
    product_version: str = ""
    serial_number: str = ""
    connection_type: str = "USB"
    all_info: Dict[str, Any] = None
    battery_level: int = -1
    battery_charging: bool = False
    is_paired: bool = False
    disk_usage: Dict[str, Any] = field(default_factory=dict)


@dataclass  
class FileInfo:
    """File information structure"""
    name: str
    path: str
    size: int = 0
    is_dir: bool = False
    modified: str = ""
    file_type: str = ""


# Case subdirectories for organized evidence storage
CASE_SUBDIRS = ["backups", "files", "screenshots", "crash_reports", "reports", "logs"]


@dataclass
class ForensicCase:
    """Forensic case information"""
    case_id: str
    case_name: str
    examiner: str
    created_at: str
    notes: str = ""
    device_udid: str = ""
    output_directory: str = ""
    
    @staticmethod
    def generate_case_id() -> str:
        """Generate a unique case ID"""
        return f"CASE-{datetime.now().strftime('%Y%m%d')}-{str(uuid_lib.uuid4())[:8].upper()}"


class CommandRunner:
    """Helper class to run libimobiledevice command-line tools"""
    
    # Cache for tool availability
    _tool_cache: Dict[str, bool] = {}
    
    @staticmethod
    def check_tool_available(tool_name: str) -> bool:
        """Check if a libimobiledevice tool is available"""
        if tool_name in CommandRunner._tool_cache:
            return CommandRunner._tool_cache[tool_name]
        
        # Use shutil.which for cross-platform compatibility
        available = shutil.which(tool_name) is not None
        
        CommandRunner._tool_cache[tool_name] = available
        return available
    
    @staticmethod
    def get_available_tools() -> Dict[str, bool]:
        """Get dictionary of available libimobiledevice tools"""
        tools = [
            "idevice_id", "ideviceinfo", "idevicepair", "idevicename",
            "idevicebackup2", "idevicescreenshot", "idevicesyslog",
            "idevicediagnostics", "idevicecrashreport", "ideviceinstaller",
            "afcclient"
        ]
        return {tool: CommandRunner.check_tool_available(tool) for tool in tools}
    
    @staticmethod
    def run_command(cmd: List[str], timeout: int = 30) -> Tuple[int, str, str]:
        """Run a command and return (return_code, stdout, stderr)"""
        logging.debug(f"Running command: {' '.join(cmd)}")
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            logging.debug(f"Command returned: {result.returncode}")
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            logging.warning(f"Command timed out: {' '.join(cmd)}")
            return -1, "", "Command timed out"
        except FileNotFoundError:
            logging.error(f"Command not found: {cmd[0]}")
            return -1, "", f"Command not found: {cmd[0]}"
        except Exception as e:
            logging.error(f"Command error: {e}")
            return -1, "", str(e)
    
    @staticmethod
    def get_device_list() -> List[DeviceInfo]:
        """Get list of connected devices using idevice_id"""
        devices = []
        
        # Try to get device list
        ret, stdout, stderr = CommandRunner.run_command(["idevice_id", "-l"])
        if ret != 0:
            return devices
        
        udids = [line.strip() for line in stdout.strip().split('\n') if line.strip()]
        
        for udid in udids:
            device = DeviceInfo(udid=udid)
            
            # Get device info
            ret, stdout, stderr = CommandRunner.run_command(
                ["ideviceinfo", "-u", udid, "-x"]
            )
            if ret == 0:
                try:
                    import plistlib
                    info = plistlib.loads(stdout.encode())
                    device.name = info.get("DeviceName", "Unknown")
                    device.product_type = info.get("ProductType", "Unknown")
                    device.product_version = info.get("ProductVersion", "Unknown")
                    device.serial_number = info.get("SerialNumber", "Unknown")
                    device.all_info = info
                except Exception:
                    # Fallback to simple parsing
                    ret, stdout, stderr = CommandRunner.run_command(
                        ["ideviceinfo", "-u", udid]
                    )
                    if ret == 0:
                        device.all_info = {}
                        for line in stdout.split('\n'):
                            if ':' in line:
                                key, _, value = line.partition(':')
                                device.all_info[key.strip()] = value.strip()
                        device.name = device.all_info.get("DeviceName", "Unknown")
                        device.product_type = device.all_info.get("ProductType", "Unknown")
                        device.product_version = device.all_info.get("ProductVersion", "Unknown")
                        device.serial_number = device.all_info.get("SerialNumber", "Unknown")
            
            devices.append(device)
        
        return devices
    
    @staticmethod
    def list_directory(udid: str, path: str, app_id: str = None) -> List[FileInfo]:
        """List directory contents using afcclient"""
        files = []
        
        cmd = ["afcclient", "-u", udid]
        if app_id:
            cmd.extend(["--documents", app_id])
        cmd.extend(["ls", "-l", path])
        
        ret, stdout, stderr = CommandRunner.run_command(cmd, timeout=60)
        
        if ret != 0:
            return files
        
        for line in stdout.strip().split('\n'):
            if not line.strip():
                continue
            
            parts = line.split()
            if len(parts) >= 7:
                # Parse ls -l output
                perms = parts[0]
                size = int(parts[4]) if parts[4].isdigit() else 0
                name = ' '.join(parts[6:])  # Handle filenames with spaces
                
                if name in ['.', '..']:
                    continue
                
                is_dir = perms.startswith('d')
                file_path = f"{path}/{name}" if path != "/" else f"/{name}"
                
                files.append(FileInfo(
                    name=name,
                    path=file_path,
                    size=size,
                    is_dir=is_dir,
                    file_type="directory" if is_dir else "file"
                ))
        
        return files
    
    @staticmethod
    def get_file(udid: str, remote_path: str, local_path: str, 
                 app_id: str = None) -> Tuple[bool, str]:
        """Download file from device"""
        cmd = ["afcclient", "-u", udid]
        if app_id:
            cmd.extend(["--documents", app_id])
        cmd.extend(["get", "-rf", remote_path, local_path])
        
        ret, stdout, stderr = CommandRunner.run_command(cmd, timeout=300)
        
        if ret == 0:
            return True, "File downloaded successfully"
        return False, stderr or "Failed to download file"
    
    @staticmethod
    def get_device_info_detailed(udid: str) -> Dict[str, Any]:
        """Get detailed device information"""
        info = {}
        
        # Get all domains info
        domains = [
            None,  # Global domain
            "com.apple.disk_usage",
            "com.apple.mobile.battery",
            "com.apple.international",
            "com.apple.mobile.backup",
        ]
        
        for domain in domains:
            cmd = ["ideviceinfo", "-u", udid]
            if domain:
                cmd.extend(["-q", domain])
            
            ret, stdout, stderr = CommandRunner.run_command(cmd)
            if ret == 0:
                domain_key = domain or "general"
                info[domain_key] = {}
                for line in stdout.split('\n'):
                    if ':' in line:
                        key, _, value = line.partition(':')
                        info[domain_key][key.strip()] = value.strip()
        
        return info
    
    @staticmethod
    def create_backup(udid: str, backup_dir: str, 
                      callback=None) -> Tuple[bool, str]:
        """Create device backup using idevicebackup2"""
        cmd = ["idevicebackup2", "-u", udid, "backup", backup_dir]
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            output_lines = []
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    output_lines.append(line.strip())
                    if callback:
                        callback(line.strip())
            
            ret = process.wait()
            output = '\n'.join(output_lines)
            
            if ret == 0:
                return True, "Backup completed successfully"
            return False, output or "Backup failed"
            
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def take_screenshot(udid: str, output_path: str) -> Tuple[bool, str]:
        """Take device screenshot"""
        cmd = ["idevicescreenshot", "-u", udid, output_path]
        ret, stdout, stderr = CommandRunner.run_command(cmd, timeout=30)
        
        if ret == 0:
            return True, output_path
        return False, stderr or "Failed to take screenshot"
    
    @staticmethod
    def check_pairing_status(udid: str) -> Tuple[bool, str]:
        """Check if device is paired"""
        if not CommandRunner.check_tool_available("idevicepair"):
            return False, "idevicepair not available"
        
        ret, stdout, stderr = CommandRunner.run_command(
            ["idevicepair", "-u", udid, "validate"]
        )
        
        if ret == 0:
            return True, "Device is paired"
        return False, stderr or stdout or "Device is not paired"
    
    @staticmethod
    def pair_device(udid: str) -> Tuple[bool, str]:
        """Pair with device"""
        if not CommandRunner.check_tool_available("idevicepair"):
            return False, "idevicepair not available"
        
        ret, stdout, stderr = CommandRunner.run_command(
            ["idevicepair", "-u", udid, "pair"]
        )
        
        if ret == 0:
            return True, "Device paired successfully"
        return False, stderr or stdout or "Failed to pair device"
    
    @staticmethod
    def get_battery_info(udid: str) -> Dict[str, Any]:
        """Get device battery information"""
        battery_info = {}
        
        ret, stdout, stderr = CommandRunner.run_command(
            ["ideviceinfo", "-u", udid, "-q", "com.apple.mobile.battery"]
        )
        
        if ret == 0:
            for line in stdout.split('\n'):
                if ':' in line:
                    key, _, value = line.partition(':')
                    battery_info[key.strip()] = value.strip()
        
        return battery_info
    
    @staticmethod
    def get_installed_apps(udid: str) -> List[Dict[str, str]]:
        """Get list of installed apps"""
        apps = []
        
        if not CommandRunner.check_tool_available("ideviceinstaller"):
            logging.warning("ideviceinstaller not available - cannot list apps")
            return apps
        
        ret, stdout, stderr = CommandRunner.run_command(
            ["ideviceinstaller", "-u", udid, "-l"],
            timeout=60
        )
        
        if ret == 0:
            for line in stdout.split('\n'):
                line = line.strip()
                if not line or line.startswith('CFBundleIdentifier') or line.startswith('Total:'):
                    continue
                
                # Parse app info: bundle_id, version, name
                parts = line.split(',')
                if len(parts) >= 1:
                    bundle_id = parts[0].strip()
                    version = parts[1].strip() if len(parts) > 1 else ""
                    name = parts[2].strip().strip('"') if len(parts) > 2 else bundle_id
                    
                    apps.append({
                        'bundle_id': bundle_id,
                        'version': version,
                        'name': name
                    })
        
        return apps
    
    @staticmethod
    def get_crash_reports(udid: str, output_dir: str, 
                          callback=None) -> Tuple[bool, str]:
        """Download crash reports from device"""
        if not CommandRunner.check_tool_available("idevicecrashreport"):
            return False, "idevicecrashreport not available"
        
        cmd = ["idevicecrashreport", "-u", udid, "-e", output_dir]
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            output_lines = []
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    output_lines.append(line.strip())
                    if callback:
                        callback(line.strip())
            
            ret = process.wait()
            
            if ret == 0:
                return True, f"Crash reports saved to {output_dir}"
            return False, '\n'.join(output_lines) or "Failed to get crash reports"
            
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def get_syslog(udid: str, callback=None, stop_event=None) -> None:
        """Stream system log from device"""
        if not CommandRunner.check_tool_available("idevicesyslog"):
            if callback:
                callback("idevicesyslog not available")
            return
        
        cmd = ["idevicesyslog", "-u", udid]
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            while True:
                if stop_event and stop_event.is_set():
                    process.terminate()
                    break
                
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line and callback:
                    callback(line.strip())
                    
        except Exception as e:
            if callback:
                callback(f"Error: {e}")
    
    @staticmethod
    def restart_device(udid: str) -> Tuple[bool, str]:
        """Restart the device"""
        if not CommandRunner.check_tool_available("idevicediagnostics"):
            return False, "idevicediagnostics not available"
        
        ret, stdout, stderr = CommandRunner.run_command(
            ["idevicediagnostics", "-u", udid, "restart"]
        )
        
        if ret == 0:
            return True, "Device restart initiated"
        return False, stderr or "Failed to restart device"
    
    @staticmethod  
    def shutdown_device(udid: str) -> Tuple[bool, str]:
        """Shutdown the device"""
        if not CommandRunner.check_tool_available("idevicediagnostics"):
            return False, "idevicediagnostics not available"
        
        ret, stdout, stderr = CommandRunner.run_command(
            ["idevicediagnostics", "-u", udid, "shutdown"]
        )
        
        if ret == 0:
            return True, "Device shutdown initiated"
        return False, stderr or "Failed to shutdown device"


class DeviceMonitorThread(QThread):
    """Thread to monitor device connections"""
    devices_changed = pyqtSignal(list)
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.last_devices = []
    
    def run(self):
        while self.running:
            devices = CommandRunner.get_device_list()
            
            # Enrich device info with battery and pairing status
            for device in devices:
                # Get battery info
                battery = CommandRunner.get_battery_info(device.udid)
                if 'BatteryCurrentCapacity' in battery:
                    try:
                        device.battery_level = int(battery['BatteryCurrentCapacity'])
                    except ValueError as e:
                        logging.debug(f"Could not parse battery level: {e}")
                if 'BatteryIsCharging' in battery:
                    device.battery_charging = battery['BatteryIsCharging'].lower() == 'true'
                
                # Check pairing status
                paired, _ = CommandRunner.check_pairing_status(device.udid)
                device.is_paired = paired
            
            # Check if device list changed
            current_udids = set(d.udid for d in devices)
            last_udids = set(d.udid for d in self.last_devices)
            
            if current_udids != last_udids:
                self.last_devices = devices
                self.devices_changed.emit(devices)
            
            self.msleep(2000)  # Check every 2 seconds
    
    def stop(self):
        self.running = False


class SyslogThread(QThread):
    """Thread for streaming system log"""
    new_line = pyqtSignal(str)
    
    def __init__(self, udid: str):
        super().__init__()
        self.udid = udid
        self.stop_event = threading.Event()
    
    def run(self):
        CommandRunner.get_syslog(
            self.udid,
            callback=lambda line: self.new_line.emit(line),
            stop_event=self.stop_event
        )
    
    def stop(self):
        self.stop_event.set()


class CrashReportThread(QThread):
    """Thread for downloading crash reports"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, udid: str, output_dir: str):
        super().__init__()
        self.udid = udid
        self.output_dir = output_dir
    
    def run(self):
        success, message = CommandRunner.get_crash_reports(
            self.udid,
            self.output_dir,
            callback=lambda msg: self.progress.emit(msg)
        )
        self.finished.emit(success, message)


class BackupThread(QThread):
    """Thread for running backup operations"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, udid: str, backup_dir: str):
        super().__init__()
        self.udid = udid
        self.backup_dir = backup_dir
    
    def run(self):
        success, message = CommandRunner.create_backup(
            self.udid, 
            self.backup_dir,
            callback=lambda msg: self.progress.emit(msg)
        )
        self.finished.emit(success, message)


class FileDownloadThread(QThread):
    """Thread for downloading files"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, udid: str, remote_path: str, local_path: str, 
                 app_id: str = None):
        super().__init__()
        self.udid = udid
        self.remote_path = remote_path
        self.local_path = local_path
        self.app_id = app_id
    
    def run(self):
        self.progress.emit(f"Downloading: {self.remote_path}")
        success, message = CommandRunner.get_file(
            self.udid, self.remote_path, self.local_path, self.app_id
        )
        self.finished.emit(success, message)


class HashCalculatorThread(QThread):
    """Thread for calculating file hashes"""
    progress = pyqtSignal(str, int)  # filename, percentage
    finished = pyqtSignal(str, dict)  # path, hashes
    
    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
    
    def run(self):
        hashes = {}
        try:
            file_size = os.path.getsize(self.file_path)
            bytes_read = 0
            
            md5 = hashlib.md5()
            sha1 = hashlib.sha1()
            sha256 = hashlib.sha256()
            
            with open(self.file_path, 'rb') as f:
                while chunk := f.read(8192):
                    md5.update(chunk)
                    sha1.update(chunk)
                    sha256.update(chunk)
                    
                    bytes_read += len(chunk)
                    progress = int((bytes_read / file_size) * 100) if file_size > 0 else 100
                    self.progress.emit(self.file_path, progress)
            
            hashes = {
                'MD5': md5.hexdigest(),
                'SHA1': sha1.hexdigest(),
                'SHA256': sha256.hexdigest()
            }
        except Exception as e:
            hashes = {'error': str(e)}
        
        self.finished.emit(self.file_path, hashes)


class DeviceInfoDialog(QDialog):
    """Dialog to show detailed device information"""
    
    def __init__(self, device: DeviceInfo, parent=None):
        super().__init__(parent)
        self.device = device
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle(f"Device Information - {self.device.name}")
        self.setMinimumSize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # Device summary
        summary_group = QGroupBox("Device Summary")
        summary_layout = QFormLayout()
        summary_layout.addRow("UDID:", QLabel(self.device.udid))
        summary_layout.addRow("Name:", QLabel(self.device.name))
        summary_layout.addRow("Model:", QLabel(self.device.product_type))
        summary_layout.addRow("iOS Version:", QLabel(self.device.product_version))
        summary_layout.addRow("Serial:", QLabel(self.device.serial_number))
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        # All info
        info_group = QGroupBox("All Device Properties")
        info_layout = QVBoxLayout()
        
        info_text = QPlainTextEdit()
        info_text.setReadOnly(True)
        info_text.setFont(QFont("Monospace", 9))
        
        if self.device.all_info:
            text = ""
            for key, value in sorted(self.device.all_info.items()):
                text += f"{key}: {value}\n"
            info_text.setPlainText(text)
        
        info_layout.addWidget(info_text)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)


class CaseManagementDialog(QDialog):
    """Dialog for managing forensic cases"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.case: Optional[ForensicCase] = None
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("New Forensic Case")
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Case details
        form_group = QGroupBox("Case Details")
        form_layout = QFormLayout()
        
        self.case_id_edit = QLineEdit()
        self.case_id_edit.setText(ForensicCase.generate_case_id())
        form_layout.addRow("Case ID:", self.case_id_edit)
        
        self.case_name_edit = QLineEdit()
        self.case_name_edit.setPlaceholderText("Enter case name")
        form_layout.addRow("Case Name:", self.case_name_edit)
        
        self.examiner_edit = QLineEdit()
        self.examiner_edit.setPlaceholderText("Examiner name")
        form_layout.addRow("Examiner:", self.examiner_edit)
        
        # Output directory
        dir_layout = QHBoxLayout()
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setPlaceholderText("Select output directory")
        dir_layout.addWidget(self.output_dir_edit)
        
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_output_dir)
        dir_layout.addWidget(browse_btn)
        
        form_layout.addRow("Output Directory:", dir_layout)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Notes
        notes_group = QGroupBox("Case Notes")
        notes_layout = QVBoxLayout()
        
        self.notes_edit = QPlainTextEdit()
        self.notes_edit.setPlaceholderText("Enter any case notes...")
        notes_layout.addWidget(self.notes_edit)
        
        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.create_case)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def browse_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Output Directory", os.path.expanduser("~")
        )
        if dir_path:
            self.output_dir_edit.setText(dir_path)
    
    def create_case(self):
        if not self.case_name_edit.text().strip():
            QMessageBox.warning(self, "Error", "Please enter a case name")
            return
        
        if not self.examiner_edit.text().strip():
            QMessageBox.warning(self, "Error", "Please enter examiner name")
            return
        
        if not self.output_dir_edit.text().strip():
            QMessageBox.warning(self, "Error", "Please select output directory")
            return
        
        self.case = ForensicCase(
            case_id=self.case_id_edit.text(),
            case_name=self.case_name_edit.text(),
            examiner=self.examiner_edit.text(),
            created_at=datetime.now().isoformat(),
            notes=self.notes_edit.toPlainText(),
            output_directory=self.output_dir_edit.text()
        )
        
        # Create case directory structure
        case_dir = os.path.join(self.case.output_directory, self.case.case_id)
        os.makedirs(case_dir, exist_ok=True)
        
        # Create subdirectories using the constant
        for subdir in CASE_SUBDIRS:
            os.makedirs(os.path.join(case_dir, subdir), exist_ok=True)
        
        # Save case info
        case_info_path = os.path.join(case_dir, "case_info.json")
        with open(case_info_path, 'w') as f:
            json.dump({
                'case_id': self.case.case_id,
                'case_name': self.case.case_name,
                'examiner': self.case.examiner,
                'created_at': self.case.created_at,
                'notes': self.case.notes
            }, f, indent=2)
        
        self.accept()


class ToolsStatusDialog(QDialog):
    """Dialog showing available libimobiledevice tools"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("libimobiledevice Tools Status")
        self.setMinimumSize(400, 300)
        
        layout = QVBoxLayout(self)
        
        info_label = QLabel(
            "The following libimobiledevice tools are required for full functionality:"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Tools table
        self.tools_table = QTableWidget()
        self.tools_table.setColumnCount(2)
        self.tools_table.setHorizontalHeaderLabels(["Tool", "Status"])
        self.tools_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tools_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        
        tools = CommandRunner.get_available_tools()
        self.tools_table.setRowCount(len(tools))
        
        for i, (tool, available) in enumerate(sorted(tools.items())):
            self.tools_table.setItem(i, 0, QTableWidgetItem(tool))
            status_item = QTableWidgetItem("✓ Available" if available else "✗ Not Found")
            status_item.setForeground(QColor("green") if available else QColor("red"))
            self.tools_table.setItem(i, 1, status_item)
        
        layout.addWidget(self.tools_table)
        
        # Install instructions
        install_label = QLabel(
            "<b>Installation:</b><br>"
            "<b>Debian/Ubuntu:</b> <code>sudo apt install libimobiledevice-utils</code><br>"
            "<b>Fedora/RHEL:</b> <code>sudo dnf install libimobiledevice-utils</code><br>"
            "<b>macOS:</b> <code>brew install libimobiledevice</code><br>"
            "<b>From source:</b> Build from this repository using ./autogen.sh && make"
        )
        install_label.setWordWrap(True)
        layout.addWidget(install_label)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)


class ExportReportDialog(QDialog):
    """Dialog to export forensic report"""
    
    def __init__(self, device: DeviceInfo, files_info: List[Dict], parent=None):
        super().__init__(parent)
        self.device = device
        self.files_info = files_info
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("Export Forensic Report")
        self.setMinimumSize(400, 200)
        
        layout = QVBoxLayout(self)
        
        # Options
        options_group = QGroupBox("Report Options")
        options_layout = QVBoxLayout()
        
        self.include_hashes = QCheckBox("Include file hashes")
        self.include_hashes.setChecked(True)
        options_layout.addWidget(self.include_hashes)
        
        self.include_timestamps = QCheckBox("Include acquisition timestamps")
        self.include_timestamps.setChecked(True)
        options_layout.addWidget(self.include_timestamps)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.save_report)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def save_report(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Report",
            f"forensic_report_{self.device.udid}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            self.generate_report(file_path)
            self.accept()
    
    def generate_report(self, file_path: str):
        with open(file_path, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("FORENSIC ACQUISITION REPORT\n")
            f.write("=" * 60 + "\n\n")
            
            if self.include_timestamps.isChecked():
                f.write(f"Report Generated: {datetime.now().isoformat()}\n\n")
            
            f.write("DEVICE INFORMATION\n")
            f.write("-" * 40 + "\n")
            f.write(f"UDID: {self.device.udid}\n")
            f.write(f"Name: {self.device.name}\n")
            f.write(f"Model: {self.device.product_type}\n")
            f.write(f"iOS Version: {self.device.product_version}\n")
            f.write(f"Serial Number: {self.device.serial_number}\n\n")
            
            if self.device.all_info:
                f.write("DETAILED PROPERTIES\n")
                f.write("-" * 40 + "\n")
                for key, value in sorted(self.device.all_info.items()):
                    f.write(f"{key}: {value}\n")
                f.write("\n")
            
            if self.files_info:
                f.write("ACQUIRED FILES\n")
                f.write("-" * 40 + "\n")
                for file_info in self.files_info:
                    f.write(f"File: {file_info.get('path', 'Unknown')}\n")
                    f.write(f"  Size: {file_info.get('size', 0)} bytes\n")
                    if self.include_hashes.isChecked() and 'hashes' in file_info:
                        for algo, hash_val in file_info['hashes'].items():
                            f.write(f"  {algo}: {hash_val}\n")
                    f.write("\n")
            
            f.write("=" * 60 + "\n")
            f.write("END OF REPORT\n")


class ForensicImagerWindow(QMainWindow):
    """Main window for the forensic imaging application"""
    
    def __init__(self):
        super().__init__()
        
        self.current_device: Optional[DeviceInfo] = None
        self.devices: List[DeviceInfo] = []
        self.acquired_files: List[Dict] = []
        self.current_case: Optional[ForensicCase] = None
        self.syslog_thread: Optional[SyslogThread] = None
        
        self.setup_ui()
        self.setup_device_monitor()
        
        # Initial device check
        QTimer.singleShot(500, self.refresh_devices)
    
    def setup_ui(self):
        self.setWindowTitle("iDevice Forensic Imager")
        self.setMinimumSize(1200, 800)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        
        # Toolbar
        self.create_toolbar()
        
        # Main content
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Device & Files
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Device selector
        device_group = QGroupBox("Connected Devices")
        device_layout = QVBoxLayout()
        
        self.device_combo = QComboBox()
        self.device_combo.currentIndexChanged.connect(self.on_device_selected)
        device_layout.addWidget(self.device_combo)
        
        # Battery status
        self.battery_label = QLabel("")
        self.battery_label.setStyleSheet("QLabel { color: #666; font-size: 11px; }")
        device_layout.addWidget(self.battery_label)
        
        device_btn_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_devices)
        device_btn_layout.addWidget(self.refresh_btn)
        
        self.device_info_btn = QPushButton("Device Info")
        self.device_info_btn.clicked.connect(self.show_device_info)
        self.device_info_btn.setEnabled(False)
        device_btn_layout.addWidget(self.device_info_btn)
        
        device_layout.addLayout(device_btn_layout)
        device_group.setLayout(device_layout)
        left_layout.addWidget(device_group)
        
        # File browser
        files_group = QGroupBox("Device Filesystem")
        files_layout = QVBoxLayout()
        
        # Path navigation
        path_layout = QHBoxLayout()
        self.path_label = QLabel("Path:")
        path_layout.addWidget(self.path_label)
        self.path_edit = QLineEdit("/")
        self.path_edit.returnPressed.connect(self.navigate_to_path)
        path_layout.addWidget(self.path_edit)
        
        self.go_btn = QPushButton("Go")
        self.go_btn.clicked.connect(self.navigate_to_path)
        path_layout.addWidget(self.go_btn)
        
        self.up_btn = QPushButton("↑ Up")
        self.up_btn.clicked.connect(self.navigate_up)
        path_layout.addWidget(self.up_btn)
        
        files_layout.addLayout(path_layout)
        
        # File tree
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["Name", "Size", "Type"])
        self.file_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.file_tree.customContextMenuRequested.connect(self.show_file_context_menu)
        self.file_tree.itemDoubleClicked.connect(self.on_file_double_clicked)
        self.file_tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        files_layout.addWidget(self.file_tree)
        
        files_group.setLayout(files_layout)
        left_layout.addWidget(files_group)
        
        content_splitter.addWidget(left_panel)
        
        # Right panel - Tabs
        right_panel = QTabWidget()
        
        # Device Info Tab
        info_tab = QWidget()
        info_layout = QVBoxLayout(info_tab)
        
        self.info_table = QTableWidget()
        self.info_table.setColumnCount(2)
        self.info_table.setHorizontalHeaderLabels(["Property", "Value"])
        self.info_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.info_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        info_layout.addWidget(self.info_table)
        
        right_panel.addTab(info_tab, "Device Info")
        
        # Apps Tab
        apps_tab = QWidget()
        apps_layout = QVBoxLayout(apps_tab)
        
        apps_btn_layout = QHBoxLayout()
        self.refresh_apps_btn = QPushButton("Refresh Apps")
        self.refresh_apps_btn.clicked.connect(self.refresh_apps)
        self.refresh_apps_btn.setEnabled(False)
        apps_btn_layout.addWidget(self.refresh_apps_btn)
        apps_btn_layout.addStretch()
        apps_layout.addLayout(apps_btn_layout)
        
        self.apps_table = QTableWidget()
        self.apps_table.setColumnCount(3)
        self.apps_table.setHorizontalHeaderLabels(["Name", "Bundle ID", "Version"])
        self.apps_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.apps_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.apps_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        apps_layout.addWidget(self.apps_table)
        
        right_panel.addTab(apps_tab, "Installed Apps")
        
        # Backup Tab
        backup_tab = QWidget()
        backup_layout = QVBoxLayout(backup_tab)
        
        backup_group = QGroupBox("Forensic Backup/Imaging")
        backup_form = QVBoxLayout()
        
        dest_layout = QHBoxLayout()
        dest_layout.addWidget(QLabel("Destination:"))
        self.backup_dest = QLineEdit()
        self.backup_dest.setPlaceholderText("Select backup destination directory")
        dest_layout.addWidget(self.backup_dest)
        self.browse_backup_btn = QPushButton("Browse")
        self.browse_backup_btn.clicked.connect(self.browse_backup_destination)
        dest_layout.addWidget(self.browse_backup_btn)
        backup_form.addLayout(dest_layout)
        
        self.backup_btn = QPushButton("Start Forensic Backup")
        self.backup_btn.clicked.connect(self.start_backup)
        self.backup_btn.setEnabled(False)
        backup_form.addWidget(self.backup_btn)
        
        backup_group.setLayout(backup_form)
        backup_layout.addWidget(backup_group)
        
        # Backup progress
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout()
        
        self.backup_progress = QProgressBar()
        self.backup_progress.setRange(0, 0)  # Indeterminate
        self.backup_progress.setVisible(False)
        progress_layout.addWidget(self.backup_progress)
        
        self.backup_log = QTextEdit()
        self.backup_log.setReadOnly(True)
        self.backup_log.setFont(QFont("Monospace", 9))
        progress_layout.addWidget(self.backup_log)
        
        progress_group.setLayout(progress_layout)
        backup_layout.addWidget(progress_group)
        
        right_panel.addTab(backup_tab, "Forensic Imaging")
        
        # Screenshot Tab
        screenshot_tab = QWidget()
        screenshot_layout = QVBoxLayout(screenshot_tab)
        
        screenshot_btn_layout = QHBoxLayout()
        self.screenshot_btn = QPushButton("Capture Screenshot")
        self.screenshot_btn.clicked.connect(self.capture_screenshot)
        self.screenshot_btn.setEnabled(False)
        screenshot_btn_layout.addWidget(self.screenshot_btn)
        
        self.save_screenshot_btn = QPushButton("Save Screenshot")
        self.save_screenshot_btn.clicked.connect(self.save_screenshot)
        self.save_screenshot_btn.setEnabled(False)
        screenshot_btn_layout.addWidget(self.save_screenshot_btn)
        screenshot_layout.addLayout(screenshot_btn_layout)
        
        self.screenshot_label = QLabel("No screenshot captured")
        self.screenshot_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.screenshot_label.setMinimumSize(400, 300)
        self.screenshot_label.setStyleSheet("QLabel { background-color: #f0f0f0; border: 1px solid #ccc; }")
        screenshot_layout.addWidget(self.screenshot_label)
        
        right_panel.addTab(screenshot_tab, "Screenshots")
        
        # Acquisition Log Tab
        log_tab = QWidget()
        log_layout = QVBoxLayout(log_tab)
        
        self.acquisition_log = QTextEdit()
        self.acquisition_log.setReadOnly(True)
        self.acquisition_log.setFont(QFont("Monospace", 9))
        log_layout.addWidget(self.acquisition_log)
        
        export_btn = QPushButton("Export Forensic Report")
        export_btn.clicked.connect(self.export_report)
        log_layout.addWidget(export_btn)
        
        right_panel.addTab(log_tab, "Acquisition Log")
        
        content_splitter.addWidget(right_panel)
        content_splitter.setSizes([400, 800])
        
        main_layout.addWidget(content_splitter)
        
        # Status bar
        self.statusBar().showMessage("Ready - No device connected")
        
        # Store screenshot data
        self.current_screenshot_data = None
    
    def create_toolbar(self):
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # Case management
        new_case_action = QAction("New Case", self)
        new_case_action.triggered.connect(self.new_case)
        toolbar.addAction(new_case_action)
        
        toolbar.addSeparator()
        
        # Refresh action
        refresh_action = QAction("Refresh Devices", self)
        refresh_action.triggered.connect(self.refresh_devices)
        toolbar.addAction(refresh_action)
        
        # Pair action
        pair_action = QAction("Pair Device", self)
        pair_action.triggered.connect(self.pair_device)
        toolbar.addAction(pair_action)
        
        toolbar.addSeparator()
        
        # Quick actions
        screenshot_action = QAction("Screenshot", self)
        screenshot_action.triggered.connect(self.capture_screenshot)
        toolbar.addAction(screenshot_action)
        
        backup_action = QAction("Start Backup", self)
        backup_action.triggered.connect(self.start_backup)
        toolbar.addAction(backup_action)
        
        crash_action = QAction("Get Crash Reports", self)
        crash_action.triggered.connect(self.get_crash_reports)
        toolbar.addAction(crash_action)
        
        toolbar.addSeparator()
        
        # Device controls
        restart_action = QAction("Restart Device", self)
        restart_action.triggered.connect(self.restart_device)
        toolbar.addAction(restart_action)
        
        toolbar.addSeparator()
        
        # Tools status
        tools_action = QAction("Check Tools", self)
        tools_action.triggered.connect(self.show_tools_status)
        toolbar.addAction(tools_action)
        
        # Help
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        toolbar.addAction(about_action)
    
    def setup_device_monitor(self):
        self.device_monitor = DeviceMonitorThread()
        self.device_monitor.devices_changed.connect(self.on_devices_changed)
        self.device_monitor.start()
    
    def refresh_devices(self):
        """Manually refresh device list"""
        self.statusBar().showMessage("Scanning for devices...")
        devices = CommandRunner.get_device_list()
        self.on_devices_changed(devices)
    
    def on_devices_changed(self, devices: List[DeviceInfo]):
        """Handle device list changes"""
        self.devices = devices
        
        # Update combo box
        current_udid = self.current_device.udid if self.current_device else None
        
        self.device_combo.clear()
        self.device_combo.addItem("Select a device...", None)
        
        new_index = 0
        for i, device in enumerate(devices):
            display_text = f"{device.name} ({device.product_type} - {device.product_version})"
            self.device_combo.addItem(display_text, device)
            
            if device.udid == current_udid:
                new_index = i + 1
        
        if new_index > 0:
            self.device_combo.setCurrentIndex(new_index)
        
        # Update status
        count = len(devices)
        if count == 0:
            self.statusBar().showMessage("No devices connected")
        elif count == 1:
            self.statusBar().showMessage(f"1 device connected: {devices[0].name}")
        else:
            self.statusBar().showMessage(f"{count} devices connected")
        
        # Log
        self.log_message(f"Device scan: {count} device(s) found")
    
    def on_device_selected(self, index: int):
        """Handle device selection"""
        device = self.device_combo.itemData(index)
        self.current_device = device
        
        # Enable/disable buttons
        has_device = device is not None
        self.device_info_btn.setEnabled(has_device)
        self.backup_btn.setEnabled(has_device and bool(self.backup_dest.text()))
        self.screenshot_btn.setEnabled(has_device)
        self.refresh_apps_btn.setEnabled(has_device)
        
        if has_device:
            self.update_device_info()
            self.update_battery_display()
            self.load_directory("/")
            self.log_message(f"Selected device: {device.name} ({device.udid})")
        else:
            self.info_table.setRowCount(0)
            self.apps_table.setRowCount(0)
            self.file_tree.clear()
            self.battery_label.setText("")
    
    def update_battery_display(self):
        """Update battery status display"""
        if not self.current_device:
            self.battery_label.setText("")
            return
        
        battery_text = ""
        if self.current_device.battery_level >= 0:
            charging = "⚡" if self.current_device.battery_charging else ""
            battery_text = f"🔋 {self.current_device.battery_level}% {charging}"
        
        paired_text = "✓ Paired" if self.current_device.is_paired else "✗ Not Paired"
        
        self.battery_label.setText(f"{battery_text}  |  {paired_text}")
    
    def refresh_apps(self):
        """Refresh installed apps list"""
        if not self.current_device:
            return
        
        self.statusBar().showMessage("Loading installed apps...")
        self.apps_table.setRowCount(0)
        
        apps = CommandRunner.get_installed_apps(self.current_device.udid)
        
        self.apps_table.setRowCount(len(apps))
        for i, app in enumerate(apps):
            self.apps_table.setItem(i, 0, QTableWidgetItem(app.get('name', '')))
            self.apps_table.setItem(i, 1, QTableWidgetItem(app.get('bundle_id', '')))
            self.apps_table.setItem(i, 2, QTableWidgetItem(app.get('version', '')))
        
        self.statusBar().showMessage(f"Found {len(apps)} installed apps")
        self.log_message(f"Found {len(apps)} installed apps")
    
    def update_device_info(self):
        """Update device info table"""
        if not self.current_device:
            return
        
        self.info_table.setRowCount(0)
        
        if self.current_device.all_info:
            info = self.current_device.all_info
            self.info_table.setRowCount(len(info))
            
            for i, (key, value) in enumerate(sorted(info.items())):
                self.info_table.setItem(i, 0, QTableWidgetItem(str(key)))
                self.info_table.setItem(i, 1, QTableWidgetItem(str(value)))
    
    def show_device_info(self):
        """Show detailed device info dialog"""
        if self.current_device:
            dialog = DeviceInfoDialog(self.current_device, self)
            dialog.exec()
    
    def load_directory(self, path: str):
        """Load directory contents"""
        if not self.current_device:
            return
        
        self.statusBar().showMessage(f"Loading: {path}")
        self.path_edit.setText(path)
        
        files = CommandRunner.list_directory(self.current_device.udid, path)
        
        self.file_tree.clear()
        
        for file_info in files:
            item = QTreeWidgetItem()
            item.setText(0, file_info.name)
            item.setText(1, self.format_size(file_info.size) if not file_info.is_dir else "")
            item.setText(2, file_info.file_type)
            item.setData(0, Qt.ItemDataRole.UserRole, file_info)
            
            if file_info.is_dir:
                item.setForeground(0, QColor("#0066cc"))
            
            self.file_tree.addTopLevelItem(item)
        
        self.statusBar().showMessage(f"Loaded {len(files)} items from {path}")
    
    def navigate_to_path(self):
        """Navigate to specified path"""
        path = self.path_edit.text().strip()
        if path:
            self.load_directory(path)
    
    def navigate_up(self):
        """Navigate to parent directory"""
        current = self.path_edit.text().strip()
        if current != "/":
            parent = str(Path(current).parent)
            self.load_directory(parent)
    
    def on_file_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle double-click on file item"""
        file_info = item.data(0, Qt.ItemDataRole.UserRole)
        if file_info and file_info.is_dir:
            self.load_directory(file_info.path)
    
    def show_file_context_menu(self, position):
        """Show context menu for file operations"""
        item = self.file_tree.itemAt(position)
        if not item:
            return
        
        file_info = item.data(0, Qt.ItemDataRole.UserRole)
        if not file_info:
            return
        
        menu = QMenu(self)
        
        download_action = QAction("Download", self)
        download_action.triggered.connect(lambda: self.download_file(file_info))
        menu.addAction(download_action)
        
        if not file_info.is_dir:
            hash_action = QAction("Calculate Hashes", self)
            hash_action.triggered.connect(lambda: self.calculate_hashes(file_info))
            menu.addAction(hash_action)
        
        menu.exec(self.file_tree.viewport().mapToGlobal(position))
    
    def download_file(self, file_info: FileInfo):
        """Download file from device"""
        if not self.current_device:
            return
        
        # Get destination
        if file_info.is_dir:
            dest = QFileDialog.getExistingDirectory(
                self, 
                "Select destination folder",
                os.path.expanduser("~")
            )
            if dest:
                dest = os.path.join(dest, file_info.name)
        else:
            dest, _ = QFileDialog.getSaveFileName(
                self,
                "Save file as",
                os.path.join(os.path.expanduser("~"), file_info.name)
            )
        
        if not dest:
            return
        
        self.statusBar().showMessage(f"Downloading: {file_info.path}")
        
        self.download_thread = FileDownloadThread(
            self.current_device.udid,
            file_info.path,
            dest
        )
        self.download_thread.progress.connect(lambda msg: self.log_message(msg))
        self.download_thread.finished.connect(self.on_download_finished)
        self.download_thread.start()
    
    def on_download_finished(self, success: bool, message: str):
        """Handle download completion"""
        if success:
            self.statusBar().showMessage("Download completed")
            self.log_message(f"Download completed: {message}")
            QMessageBox.information(self, "Success", "File downloaded successfully!")
        else:
            self.statusBar().showMessage("Download failed")
            self.log_message(f"Download failed: {message}")
            QMessageBox.warning(self, "Error", f"Download failed: {message}")
    
    def calculate_hashes(self, file_info: FileInfo):
        """Download and calculate hashes for a file"""
        if file_info.is_dir:
            QMessageBox.warning(self, "Error", "Cannot hash a directory")
            return
        
        # Download to temp file first
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name
        
        self.statusBar().showMessage(f"Downloading for hash calculation: {file_info.path}")
        
        success, message = CommandRunner.get_file(
            self.current_device.udid,
            file_info.path,
            tmp_path
        )
        
        if not success:
            self.log_message(f"Failed to download for hashing: {message}")
            return
        
        # Calculate hashes
        self.hash_thread = HashCalculatorThread(tmp_path)
        self.hash_thread.progress.connect(
            lambda path, pct: self.statusBar().showMessage(f"Calculating hashes: {pct}%")
        )
        self.hash_thread.finished.connect(
            lambda path, hashes: self.on_hash_calculated(file_info, hashes, tmp_path)
        )
        self.hash_thread.start()
    
    def on_hash_calculated(self, file_info: FileInfo, hashes: Dict, tmp_path: str):
        """Handle hash calculation completion"""
        # Clean up temp file
        try:
            os.unlink(tmp_path)
        except Exception:
            pass
        
        if 'error' in hashes:
            self.log_message(f"Hash calculation failed: {hashes['error']}")
            return
        
        # Log results
        self.log_message(f"\nFile: {file_info.path}")
        self.log_message(f"  Size: {file_info.size} bytes")
        for algo, hash_val in hashes.items():
            self.log_message(f"  {algo}: {hash_val}")
        
        # Store for report
        self.acquired_files.append({
            'path': file_info.path,
            'size': file_info.size,
            'hashes': hashes,
            'timestamp': datetime.now().isoformat()
        })
        
        self.statusBar().showMessage("Hash calculation completed")
        
        # Show results
        msg = f"File: {file_info.name}\n\n"
        for algo, hash_val in hashes.items():
            msg += f"{algo}: {hash_val}\n"
        
        QMessageBox.information(self, "Hash Results", msg)
    
    def browse_backup_destination(self):
        """Browse for backup destination"""
        dest = QFileDialog.getExistingDirectory(
            self,
            "Select backup destination",
            os.path.expanduser("~")
        )
        if dest:
            self.backup_dest.setText(dest)
            self.backup_btn.setEnabled(self.current_device is not None)
    
    def start_backup(self):
        """Start forensic backup"""
        if not self.current_device:
            QMessageBox.warning(self, "Error", "No device selected")
            return
        
        dest = self.backup_dest.text().strip()
        if not dest:
            QMessageBox.warning(self, "Error", "Please select a backup destination")
            return
        
        # Confirm
        reply = QMessageBox.question(
            self,
            "Confirm Backup",
            f"Start forensic backup of {self.current_device.name}?\n\n"
            f"Destination: {dest}\n\n"
            "This may take a significant amount of time.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        self.backup_log.clear()
        self.backup_progress.setVisible(True)
        self.backup_btn.setEnabled(False)
        
        self.log_message(f"Starting forensic backup: {self.current_device.name}")
        self.log_message(f"UDID: {self.current_device.udid}")
        self.log_message(f"Destination: {dest}")
        self.log_message(f"Started: {datetime.now().isoformat()}")
        
        self.backup_thread = BackupThread(self.current_device.udid, dest)
        self.backup_thread.progress.connect(self.on_backup_progress)
        self.backup_thread.finished.connect(self.on_backup_finished)
        self.backup_thread.start()
    
    def on_backup_progress(self, message: str):
        """Handle backup progress updates"""
        self.backup_log.append(message)
        # Auto-scroll
        scrollbar = self.backup_log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def on_backup_finished(self, success: bool, message: str):
        """Handle backup completion"""
        self.backup_progress.setVisible(False)
        self.backup_btn.setEnabled(True)
        
        if success:
            self.log_message(f"Backup completed: {datetime.now().isoformat()}")
            QMessageBox.information(self, "Success", "Forensic backup completed successfully!")
        else:
            self.log_message(f"Backup failed: {message}")
            QMessageBox.warning(self, "Error", f"Backup failed: {message}")
    
    def capture_screenshot(self):
        """Capture device screenshot"""
        if not self.current_device:
            QMessageBox.warning(self, "Error", "No device selected")
            return
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            tmp_path = tmp.name
        
        self.statusBar().showMessage("Capturing screenshot...")
        
        success, result = CommandRunner.take_screenshot(
            self.current_device.udid,
            tmp_path
        )
        
        if success:
            # Load and display image
            try:
                pixmap = QPixmap(tmp_path)
                if not pixmap.isNull():
                    # Scale to fit label
                    scaled = pixmap.scaled(
                        self.screenshot_label.size(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.screenshot_label.setPixmap(scaled)
                    
                    # Store original data
                    with open(tmp_path, 'rb') as f:
                        self.current_screenshot_data = f.read()
                    
                    self.save_screenshot_btn.setEnabled(True)
                    self.statusBar().showMessage("Screenshot captured")
                    self.log_message(f"Screenshot captured: {datetime.now().isoformat()}")
                else:
                    self.statusBar().showMessage("Failed to load screenshot image")
            except Exception as e:
                self.statusBar().showMessage(f"Error loading screenshot: {e}")
            
            # Clean up temp file
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
        else:
            self.statusBar().showMessage(f"Screenshot failed: {result}")
            QMessageBox.warning(
                self, 
                "Error", 
                f"Failed to capture screenshot.\n\n{result}\n\n"
                "Note: Screenshot requires a mounted developer disk image."
            )
    
    def save_screenshot(self):
        """Save captured screenshot"""
        if not self.current_screenshot_data:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Screenshot",
            f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
            "PNG Images (*.png);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'wb') as f:
                    f.write(self.current_screenshot_data)
                self.log_message(f"Screenshot saved: {file_path}")
                QMessageBox.information(self, "Success", f"Screenshot saved to:\n{file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save screenshot: {e}")
    
    def log_message(self, message: str):
        """Add message to acquisition log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.acquisition_log.append(f"[{timestamp}] {message}")
    
    def export_report(self):
        """Export forensic report"""
        if not self.current_device:
            QMessageBox.warning(self, "Error", "No device selected")
            return
        
        dialog = ExportReportDialog(
            self.current_device,
            self.acquired_files,
            self
        )
        dialog.exec()
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About iDevice Forensic Imager",
            "<h3>iDevice Forensic Imager</h3>"
            "<p>A GUI tool for forensic imaging of Apple iOS devices.</p>"
            "<p>Uses <b>libimobiledevice</b> for device communication.</p>"
            "<h4>Features:</h4>"
            "<ul>"
            "<li>Device detection and information gathering</li>"
            "<li>Filesystem browsing and file acquisition</li>"
            "<li>Full device backup (forensic imaging)</li>"
            "<li>Screenshot capture</li>"
            "<li>Hash calculation (MD5, SHA1, SHA256)</li>"
            "<li>Crash report acquisition</li>"
            "<li>Case management</li>"
            "<li>Forensic report generation</li>"
            "</ul>"
            "<p><small>Licensed under LGPL v2.1</small></p>"
        )
    
    def new_case(self):
        """Create a new forensic case"""
        dialog = CaseManagementDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.case:
            self.current_case = dialog.case
            self.log_message(f"New case created: {self.current_case.case_id}")
            self.log_message(f"Case name: {self.current_case.case_name}")
            self.log_message(f"Examiner: {self.current_case.examiner}")
            self.log_message(f"Output directory: {self.current_case.output_directory}")
            self.statusBar().showMessage(f"Case: {self.current_case.case_name}")
            
            # Update backup destination to case directory
            case_dir = os.path.join(
                self.current_case.output_directory, 
                self.current_case.case_id,
                "backups"
            )
            self.backup_dest.setText(case_dir)
            self.backup_btn.setEnabled(self.current_device is not None)
    
    def pair_device(self):
        """Pair with the selected device"""
        if not self.current_device:
            QMessageBox.warning(self, "Error", "No device selected")
            return
        
        self.statusBar().showMessage("Pairing with device...")
        success, message = CommandRunner.pair_device(self.current_device.udid)
        
        if success:
            self.log_message(f"Device paired successfully: {self.current_device.name}")
            QMessageBox.information(self, "Success", "Device paired successfully!")
            self.refresh_devices()
        else:
            self.log_message(f"Pairing failed: {message}")
            QMessageBox.warning(
                self, 
                "Pairing Failed", 
                f"Failed to pair with device.\n\n{message}\n\n"
                "Please unlock the device and tap 'Trust' when prompted."
            )
    
    def get_crash_reports(self):
        """Download crash reports from device"""
        if not self.current_device:
            QMessageBox.warning(self, "Error", "No device selected")
            return
        
        # Determine output directory
        if self.current_case:
            output_dir = os.path.join(
                self.current_case.output_directory,
                self.current_case.case_id,
                "crash_reports"
            )
        else:
            output_dir = QFileDialog.getExistingDirectory(
                self,
                "Select directory for crash reports",
                os.path.expanduser("~")
            )
        
        if not output_dir:
            return
        
        self.log_message(f"Downloading crash reports to: {output_dir}")
        self.statusBar().showMessage("Downloading crash reports...")
        
        self.crash_thread = CrashReportThread(self.current_device.udid, output_dir)
        self.crash_thread.progress.connect(lambda msg: self.log_message(msg))
        self.crash_thread.finished.connect(self.on_crash_reports_finished)
        self.crash_thread.start()
    
    def on_crash_reports_finished(self, success: bool, message: str):
        """Handle crash report download completion"""
        if success:
            self.log_message(f"Crash reports downloaded successfully")
            self.statusBar().showMessage("Crash reports downloaded")
            QMessageBox.information(self, "Success", message)
        else:
            self.log_message(f"Failed to download crash reports: {message}")
            self.statusBar().showMessage("Failed to download crash reports")
            QMessageBox.warning(self, "Error", f"Failed to download crash reports:\n{message}")
    
    def restart_device(self):
        """Restart the connected device"""
        if not self.current_device:
            QMessageBox.warning(self, "Error", "No device selected")
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm Restart",
            f"Are you sure you want to restart {self.current_device.name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        success, message = CommandRunner.restart_device(self.current_device.udid)
        
        if success:
            self.log_message(f"Device restart initiated: {self.current_device.name}")
            QMessageBox.information(self, "Success", "Device restart initiated")
        else:
            self.log_message(f"Failed to restart device: {message}")
            QMessageBox.warning(self, "Error", f"Failed to restart device:\n{message}")
    
    def show_tools_status(self):
        """Show libimobiledevice tools status dialog"""
        dialog = ToolsStatusDialog(self)
        dialog.exec()
    
    @staticmethod
    def format_size(size: int) -> str:
        """Format file size for display"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"
    
    def closeEvent(self, event):
        """Handle window close"""
        # Stop device monitor
        self.device_monitor.stop()
        self.device_monitor.wait()
        
        # Stop syslog thread if running
        if self.syslog_thread and self.syslog_thread.isRunning():
            self.syslog_thread.stop()
            self.syslog_thread.wait()
        
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("iDevice Forensic Imager")
    app.setOrganizationName("libimobiledevice")
    
    # Set application style
    app.setStyle("Fusion")
    
    window = ForensicImagerWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
