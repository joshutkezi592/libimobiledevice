# iDevice Forensic Imager

A graphical user interface (GUI) tool for forensic imaging of Apple iOS devices. This tool provides a user-friendly interface to the powerful libimobiledevice library, focused on forensic acquisition and analysis of iOS devices.

## Features

- **Device Detection & Management**
  - Automatic detection of connected iOS devices
  - Real-time device connection monitoring
  - Detailed device information display (UDID, model, iOS version, serial number, etc.)

- **Filesystem Browser**
  - Browse device filesystem via AFC (Apple File Connection)
  - Navigate directories with familiar path-based navigation
  - View file properties including size and type
  - Download files and directories from device
  - Context menu for quick actions

- **Forensic Imaging**
  - Full device backup using idevicebackup2
  - Progress monitoring with detailed logs
  - Backup verification

- **Hash Verification**
  - Calculate MD5, SHA1, and SHA256 hashes for acquired files
  - Essential for forensic chain of custody documentation

- **Screenshot Capture**
  - Capture device screen (requires mounted developer disk image)
  - Save screenshots in PNG format
  - Useful for documenting device state

- **Report Generation**
  - Export detailed forensic reports
  - Include device information, acquired files, and hash values
  - Timestamped acquisition logs

## Requirements

### System Requirements
- Linux or macOS operating system
- Python 3.8 or later
- PyQt6

### libimobiledevice Requirements
The following libimobiledevice tools must be installed and accessible in PATH:
- `idevice_id` - Device detection
- `ideviceinfo` - Device information
- `afcclient` - Filesystem access
- `idevicebackup2` - Device backup
- `idevicescreenshot` - Screenshot capture (requires developer disk image)

## Installation

### 1. Install libimobiledevice

#### On Debian/Ubuntu:
```bash
sudo apt-get install \
    libimobiledevice6 \
    libimobiledevice-utils \
    usbmuxd
```

#### On macOS (with Homebrew):
```bash
brew install libimobiledevice
```

#### From Source (this repository):
```bash
cd /path/to/libimobiledevice
./autogen.sh
make
sudo make install
```

### 2. Install Python Dependencies

```bash
cd gui
pip install -r requirements.txt
```

Or install PyQt6 directly:
```bash
pip install PyQt6
```

### 3. Run the Application

```bash
python3 forensic_imager.py
```

## Usage Guide

### Connecting a Device

1. Connect your iOS device via USB
2. Trust the computer on the device if prompted
3. The device should appear automatically in the "Connected Devices" dropdown
4. Select your device to begin working with it

### Browsing the Filesystem

1. With a device selected, the filesystem browser will show the root directory
2. Double-click directories to navigate into them
3. Use the "↑ Up" button to go to the parent directory
4. Enter a path directly in the path field and click "Go"

### Downloading Files

1. Right-click on a file or directory in the file browser
2. Select "Download" from the context menu
3. Choose a destination on your local machine
4. The file will be downloaded with progress indication

### Calculating Hashes

1. Right-click on a file in the file browser
2. Select "Calculate Hashes"
3. The file will be downloaded temporarily and hashes computed
4. Results will be displayed and logged

### Creating a Forensic Backup

1. Go to the "Forensic Imaging" tab
2. Click "Browse" to select a backup destination directory
3. Click "Start Forensic Backup"
4. Monitor progress in the log window
5. Wait for completion - this may take considerable time

### Capturing Screenshots

1. Go to the "Screenshots" tab
2. Click "Capture Screenshot"
3. The screenshot will be displayed in the preview area
4. Click "Save Screenshot" to save to disk

**Note:** Screenshot functionality requires a mounted developer disk image on the device.

### Generating Reports

1. Go to the "Acquisition Log" tab
2. Click "Export Forensic Report"
3. Select report options (include hashes, timestamps)
4. Choose a destination for the report file
5. The report will include all device information and acquisition details

## Forensic Best Practices

When using this tool for forensic purposes:

1. **Document Everything**: Take screenshots of device information and keep detailed logs
2. **Verify Hashes**: Always calculate and document hashes of acquired evidence
3. **Maintain Chain of Custody**: Use the report generation feature to create audit trails
4. **Write-Block When Possible**: Consider using write-blocking techniques where applicable
5. **Multiple Acquisitions**: Consider performing multiple backup acquisitions for verification

## Limitations

- Screenshot capture requires a mounted developer disk image
- Network device support is limited
- Some device features may require the device to be unlocked/trusted
- Encrypted backups require password entry on the device

## Troubleshooting

### Device Not Detected
- Ensure usbmuxd service is running: `sudo systemctl start usbmuxd`
- Check USB connection
- Trust the computer on the device
- Try running `idevice_id -l` to verify libimobiledevice can see the device

### Permission Denied
- Add user to plugdev group: `sudo usermod -a -G plugdev $USER`
- Log out and back in
- Check udev rules for iOS devices

### Screenshot Fails
- Mount the developer disk image using Xcode or ideviceimagemounter
- Ensure the device is unlocked

## License

This tool is part of the libimobiledevice project and is licensed under the GNU Lesser General Public License v2.1.

## Contributing

Contributions are welcome! Please see the main libimobiledevice repository for contribution guidelines.
