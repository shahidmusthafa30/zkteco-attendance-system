# ZKTeco Attendance System

A Python-based attendance management system for ZKTeco biometric devices. This application provides a user-friendly GUI to retrieve and manage attendance records from ZKTeco devices.

## Features

- Connect to ZKTeco devices over network
- View attendance records with user names
- Group check-in and check-out times
- Calculate duration between check-in and check-out
- Filter records by date range
- Export records to CSV format
- Standalone Windows executable available

## Screenshots

(Screenshots will be added here)

## Requirements

### For Development
- Python 3.8 or higher
- Required Python packages (install using `pip install -r requirements.txt`):
  - pandas
  - zklib
  - tkcalendar
  - babel

### For End Users
- Windows operating system
- Network access to ZKTeco device
- No additional software required (standalone executable)

## Installation

### For End Users
1. Download the latest release from the [Releases](https://github.com/shahidmusthafa30/zkteco-attendance-system/releases) page
2. Extract the ZIP file
3. Run `ZKTeco Attendance System.exe`

### For Developers
1. Clone the repository:
   ```bash
   git clone https://github.com/shahidmusthafa30/zkteco-attendance-system.git
   cd zkteco-attendance-system
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python attendance_gui.py
   ```

## Usage

1. Launch the application
2. Enter the IP address and port of your ZKTeco device
3. Click "Connect" to establish connection
4. Select date range for attendance records
5. Click "Retrieve Records" to view attendance data
6. Use "Export to CSV" to save records to a file

### Common Issues and Solutions

1. **Connection Failed**
   - Verify the device IP address and port
   - Ensure the device is powered on and connected to the network
   - Check if any firewall is blocking the connection

2. **No Records Found**
   - Verify the date range selection
   - Ensure the device has attendance records for the selected period
   - Check if the device's date and time are set correctly

3. **Export Issues**
   - Ensure you have write permissions in the target directory
   - Check if the file is not open in another application

## Building from Source

To create a standalone executable:

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Build the executable:
   ```bash
   pyinstaller --clean attendance_system.spec
   ```

The executable will be created in the `dist` folder.

## Project Structure

```
zkteco-attendance-system/
├── attendance_gui.py      # Main GUI application
├── attendance_system.py   # Core attendance system logic
├── requirements.txt       # Python package dependencies
├── attendance_system.spec # PyInstaller specification file
└── README.md             # This file
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [zklib](https://github.com/fananimi/pyzk) - Python library for ZKTeco devices
- [tkcalendar](https://github.com/j4321/tkcalendar) - Calendar widget for tkinter
- [pandas](https://pandas.pydata.org/) - Data manipulation library

## Contact

Project Link: [https://github.com/shahidmusthafa30/zkteco-attendance-system](https://github.com/shahidmusthafa30/zkteco-attendance-system) 