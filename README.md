# 🚁 Encrypted Telemetry Dashboard

A beginner-friendly Python project that simulates a drone sending encrypted telemetry data to a dashboard with live visualizations.

## 🎯 What This Project Does

This project creates a complete encrypted communication system between a simulated drone and a dashboard:
- **Drone Simulator**: Generates fake sensor data (GPS, altitude, speed, battery)
- **Encryption Layer**: Secures all data with AES-256 encryption
- **Dashboard**: Displays live graphs and maps of the telemetry data

## 🛠️ Installation

### 1. Install Python
Make sure you have Python 3.8 or newer installed:
```bash
python --version
```

### 2. Install Required Libraries
Open your terminal and run:
```bash
pip install cryptography matplotlib numpy
```

### 3. Download the Project Files
Make sure you have all these files in the same folder:
- `config.py`
- `encryption.py`
- `drone_simulator.py`
- `dashboard.py`
- `README.md` (this file)

## 🚀 How to Run

You'll need **TWO terminal windows** open:

### Terminal 1 - Start the Dashboard First
```bash
python dashboard.py
```
You should see:
```
====================================================
ENCRYPTED TELEMETRY - DASHBOARD
====================================================

📊 Dashboard initialized
👂 Listening on localhost:5000...
✓ Dashboard ready! Waiting for drone to connect...
```

### Terminal 2 - Start the Drone Simulator
```bash
python drone_simulator.py
```
You should see:
```
====================================================
ENCRYPTED TELEMETRY - DRONE SIMULATOR
====================================================

🚁 Drone Simulator initialized
   Starting position: 34.0522, -118.2437
   Battery: 100%

🔌 Connecting to dashboard at localhost:5000...
✓ Connected to dashboard!

🚁 Starting flight simulation...
   (Press Ctrl+C to stop)
```

A window will pop up showing live graphs!

## 📊 What You'll See

The dashboard displays four panels:

1. **Flight Path Map** (Top Left): Shows the drone's circular patrol route
2. **Altitude Graph** (Top Right): Shows altitude changing over time
3. **Speed Graph** (Bottom Left): Shows speed variations
4. **Battery Gauge** (Bottom Right): Shows remaining battery with status

## 🔧 Troubleshooting

### "Port already in use" Error
- Close any other programs using port 5000
- Or change `PORT` in `config.py` to a different number

### "Connection refused" Error
- Make sure you start `dashboard.py` BEFORE `drone_simulator.py`

### "Module not found" Error
- Install the missing library: `pip install <library-name>`

### No graph appears
- Make sure matplotlib is installed: `pip install matplotlib`

## 🎓 How It Works

### The Journey of Data (Step-by-Step):

1. **Drone generates data**: Simulates GPS, altitude, speed, battery readings
2. **Data converted to JSON**: Formats data into text: `{"altitude": 65, "speed": 14.5, ...}`
3. **Encryption applied**: Scrambles JSON into encrypted bytes using AES-256
4. **Data transmitted**: Sends encrypted data over network socket
5. **Dashboard receives**: Gets encrypted data from network
6. **Decryption**: Unscrambles data back to readable JSON
7. **Visualization**: Updates all graphs with new data

### Security Features:

- **AES-256 Encryption**: Military-grade encryption algorithm
- **Fernet Implementation**: Uses the cryptography library's Fernet symmetric encryption
- **Secret Key**: Both drone and dashboard use the same key to encrypt/decrypt

## 🔐 Understanding the Code

### `config.py`
Settings for the entire project. Change these to customize behavior:
- `HOST` and `PORT`: Network address
- `ENCRYPTION_KEY`: Secret password (16 bytes)
- `UPDATE_INTERVAL`: How often to send data (seconds)

### `encryption.py`
The `SecureChannel` class handles all encryption:
- `encrypt()`: Scrambles data into secret code
- `decrypt()`: Unscrambles code back to readable text

### `drone_simulator.py`
The `DroneSimulator` class simulates a flying drone:
- `update_position()`: Calculates new position/altitude/speed
- `get_telemetry()`: Packages all sensor data
- `send_telemetry()`: Encrypts and sends data

### `dashboard.py`
The `TelemetryDashboard` class displays data:
- `receive_telemetry()`: Gets and decrypts incoming data
- `update_plots()`: Refreshes all graphs
- Runs in two threads: one for network, one for display

## 🚀 Next Steps & Improvements

### Easy Improvements (Week 1-2):
- Add more sensors (temperature, wind, compass)
- Save data to a log file
- Add low battery warnings
- Change dashboard colors

### Medium Improvements (Week 3-4):
- Add two-way communication (send commands to drone)
- Create a web-based dashboard with Flask
- Simulate multiple drones
- Add message authentication codes (MAC)

### Advanced Improvements (Week 5-8):
- Connect to a real drone (DJI Tello)
- Implement frequency-hopping simulation
- Add GPS spoofing detection
- Use machine learning for anomaly detection

## 📚 Learning Resources

### Python Networking:
- [Real Python Socket Programming Guide](https://realpython.com/python-sockets/)
- [Python Socket Documentation](https://docs.python.org/3/library/socket.html)

### Cryptography:
- [Cryptography.io Documentation](https://cryptography.io/)
- [Practical Cryptography with Python](https://inventwithpython.com/cracking/)

### Data Visualization:
- [Matplotlib Tutorials](https://matplotlib.org/stable/tutorials/index.html)
- [Python Graph Gallery](https://python-graph-gallery.com/)

## 🎯 Portfolio Tips

To showcase this project:

1. **Create a GitHub Repository**: Upload all files with good commit messages
2. **Record a Demo Video**: Show the system running with explanation
3. **Write a Blog Post**: Explain what you learned and challenges faced
4. **Take Screenshots**: Capture the dashboard with annotations
5. **Document Improvements**: Show any enhancements you added

## 📝 License

This is an educational project - feel free to use, modify, and learn from it!

## 🙋 Questions?

If something doesn't work:
1. Check the Troubleshooting section above
2. Make sure all libraries are installed
3. Verify you're running dashboard.py first
4. Check that ENCRYPTION_KEY is the same in both files

## 🌟 What's Next?

Once you have this working, try:
- Reading the "Secure Telemetry Networks" report for more project ideas
- Building Project 2: RF Spectrum Analyzer
- Implementing additional security features
- Connecting to a real drone or IoT device

Good luck and have fun building! 🚁✨
