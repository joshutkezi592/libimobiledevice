# iDevice Manager - PyQt6 GUI

A modern, responsive GUI application for managing iOS devices using libimobiledevice.

## Features

- **Device Detection**: Automatically scan and list connected iOS devices
- **Device Information**: View detailed device information (model, iOS version, serial number, etc.)
- **Screenshot Capture**: Take and save screenshots from connected devices
- **Syslog Monitoring**: Real-time syslog viewing with auto-scrolling
- **App Management**: List installed applications (placeholder for future implementation)
- **File Browser**: Browse device files via AFC protocol (placeholder for future implementation)
- **Device Pairing**: Pair and unpair devices
- **Device Control**: Reboot devices remotely

## Prerequisites

### 1. Install libimobiledevice tools

**macOS:**
```bash
brew install libimobiledevice
```

**Ubuntu/Debian:**
```bash
sudo apt-get install libimobiledevice-utils
```

**Build from source:**
See the main [README.md](../README.md) for detailed build instructions.

### 2. Install Python dependencies

**Quick install (recommended):**
```bash
cd gui
./install.sh
```

**Manual install:**
```bash
cd gui
pip install -r requirements.txt
```

Or install PyQt6 directly:
```bash
pip install PyQt6
```

## Running the GUI

```bash
cd gui
python3 idevice_manager.py
```

Or make it executable:
```bash
chmod +x idevice_manager.py
./idevice_manager.py
```

## Usage

1. **Connect your iOS device** via USB or WiFi (if WiFi sync is enabled)
2. **Launch the application**
3. **Click "Refresh Devices"** to scan for connected devices
4. **Select a device** from the list on the left
5. **Use the tabs** to access different features:
   - **Device Info**: View detailed device information
   - **Screenshot**: Capture and save screenshots
   - **Syslog**: Monitor device logs in real-time
   - **Apps**: View installed applications
   - **Files**: Browse device filesystem

## Keyboard Shortcuts

- **F5**: Refresh device list
- **Ctrl+Q**: Quit application

## GUI Design

The GUI features a modern, responsive design with:

- **Clean, intuitive layout** with left sidebar for device selection
- **Tab-based interface** for different functions
- **Responsive buttons** with hover effects
- **Real-time updates** for syslog monitoring
- **Snappy performance** using background threads for long operations
- **macOS-optimized** using PyQt6 for best compatibility

## Troubleshooting

### "No devices found"
- Ensure your device is connected and unlocked
- Make sure you have trusted this computer on your device
- Try refreshing the device list

### "Missing Tools" warning
- Install libimobiledevice tools (see Prerequisites above)
- Ensure the tools are in your system PATH

### Screenshot fails
- Make sure the device is unlocked
- For some iOS versions, you may need to mount the developer disk image first

## Future Enhancements

- Full app installation/removal support
- Complete file browser with upload/download
- Backup and restore functionality
- Advanced diagnostics
- Device location simulation
- Custom icon support

## License

This GUI application follows the same license as libimobiledevice (LGPL v2.1).
