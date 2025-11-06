# 🚁 Secure Drone Telemetry Dashboard

A real-time telemetry monitoring system demonstrating secure network data transmission using Python, FastAPI, and WebSockets. This project features an autonomous drone simulator that transmits encrypted telemetry data to a professional web-based dashboard for live monitoring and analysis.

## 🎯 Overview

This project showcases:
- **End-to-end encryption** of telemetry data during transmission
- **Real-time data streaming** via WebSocket protocol
- **Professional dashboard** interface for monitoring drone metrics
- **Autonomous flight simulation** with realistic telemetry generation

Perfect for demonstrating network telemetry concepts, secure data transmission, and real-time monitoring systems.

## ✨ Features

### Security
- **Fernet Symmetric Encryption**: All telemetry data is encrypted before transmission
- **Secure Key Management**: Automatic encryption key generation and storage
- **Protected Data Flow**: No plaintext telemetry transmitted over the network

### Real-time Monitoring
- **Live Telemetry Display**: Updates every second with current drone data
- **Connection Status**: Visual indicators for system connectivity
- **Update Rate Tracking**: Monitor data transmission frequency
- **Packet Counting**: Track total telemetry packets received

### Telemetry Data
- **GPS Coordinates**: Latitude and longitude positioning
- **Flight Metrics**: Altitude, speed, and heading
- **Battery Monitoring**: Real-time battery level with visual indicators
- **System Status**: Operational status monitoring
- **Compass Direction**: Cardinal direction display (N, S, E, W, etc.)

## 🏗️ Architecture

### System Components

```
┌─────────────────┐         Encrypted          ┌──────────────────┐
│                 │        Telemetry           │                  │
│  Drone Simulator│──────────────────────────>│  FastAPI Server  │
│  (Autonomous)   │      WebSocket             │   (Dashboard)    │
│                 │                             │                  │
└─────────────────┘                             └────────┬─────────┘
                                                         │
                                                         │ Decrypted
                                                         │ Telemetry
                                                         ▼
                                                ┌─────────────────┐
                                                │  Web Dashboard  │
                                                │   (Browser)     │
                                                └─────────────────┘
```

### Module Breakdown

1. **`encryption.py`** - Encryption Module
   - Implements Fernet symmetric encryption
   - Manages encryption keys (auto-generates on first run)
   - Encrypts outgoing telemetry data
   - Decrypts incoming telemetry data

2. **`drone_simulator.py`** - Autonomous Drone Simulator
   - Simulates realistic drone flight patterns
   - Generates telemetry data (GPS, altitude, speed, battery, heading)
   - Encrypts telemetry before transmission
   - Maintains WebSocket connection to dashboard
   - Simulates battery drain over time

3. **`dashboard.py`** - FastAPI Server
   - Serves web dashboard interface
   - Manages WebSocket connections (drone and web clients)
   - Decrypts incoming telemetry from drone
   - Broadcasts telemetry to connected web clients
   - Provides health check endpoint

4. **`static/index.html`** - Web Dashboard Interface
   - Professional responsive design
   - Real-time telemetry visualization
   - Connection status monitoring
   - Session statistics (update rate, packet count)
   - Mobile-friendly layout

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Navigate to the project directory**:
   ```bash
   cd telemetry_dashboard
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Running the System

You need **two separate terminal windows**:

#### Terminal 1: Start the Dashboard Server

```bash
python dashboard.py
```

You should see:
```
============================================================
🚁 SECURE DRONE TELEMETRY DASHBOARD
============================================================
📡 Server starting...
🌐 Dashboard URL: http://localhost:8000
🔌 Drone WebSocket: ws://localhost:8000/ws/drone
🔒 Using encrypted telemetry transmission
============================================================
```

#### Terminal 2: Start the Drone Simulator

```bash
python drone_simulator.py
```

You should see:
```
============================================================
Starting Autonomous Drone Simulator
============================================================
Initial position: (50.00, 50.00)
Connecting to dashboard at ws://localhost:8000/ws/drone...
============================================================
✓ Connected to dashboard!
Transmitting encrypted telemetry data...

📡 Telemetry sent - Pos: (52.34, 48.56), Alt: 27.3m, Speed: 18.2m/s, Battery: 99.9%
```

#### Access the Dashboard

Open your web browser and navigate to:
```
http://localhost:8000
```

## 📊 Dashboard Panels

### 📊 System Status
- **Drone Status**: Current operational state (ACTIVE/BATTERY_DEPLETED)
- **Battery Level**: Visual battery indicator with color coding
  - Green: > 50%
  - Orange: 20-50%
  - Red: < 20%

### 📍 Location Data
- **Latitude**: GPS latitude coordinate (decimal degrees)
- **Longitude**: GPS longitude coordinate (decimal degrees)

### ✈️ Flight Data
- **Altitude**: Current height above ground (meters)
- **Speed**: Current velocity (meters per second)

### 🧭 Navigation
- **Heading**: Direction in degrees (0-360°)
- **Direction**: Cardinal compass direction (N, NE, E, SE, S, SW, W, NW)

### ℹ️ Session Information
- **Connection Type**: WebSocket (Encrypted)
- **Encryption Protocol**: Fernet (AES-128)
- **Update Rate**: Telemetry updates per second (Hz)
- **Data Packets Received**: Total packet count
- **Last Update**: Timestamp of most recent data

## 🔒 Security Implementation

### Encryption Flow

1. **Key Generation** (First Run):
   ```
   - System generates Fernet encryption key
   - Key saved to secret.key file
   - Both drone and dashboard use same key
   ```

2. **Telemetry Transmission**:
   ```
   Drone → Encrypt telemetry → Send via WebSocket → Dashboard receives
   ```

3. **Data Decryption**:
   ```
   Dashboard → Decrypt telemetry → Broadcast to web clients → Display
   ```

### Security Features

- **AES-128 Encryption**: Industry-standard symmetric encryption
- **Shared Secret**: Both components use the same encryption key
- **Data Integrity**: Encryption prevents tampering during transmission
- **Automatic Key Management**: No manual configuration required

## 📁 Project Structure

```
telemetry_dashboard/
├── dashboard.py              # FastAPI server & WebSocket manager
├── drone_simulator.py        # Autonomous drone with telemetry generation
├── encryption.py             # Fernet encryption implementation
├── requirements.txt          # Python dependencies
├── secret.key               # Encryption key (auto-generated, gitignored)
├── .gitignore               # Git ignore rules
├── static/
│   └── index.html           # Professional dashboard interface
└── README.md                # This file
```

## 🛠️ Technology Stack

- **Backend**: Python 3.8+
- **Web Framework**: FastAPI
- **WebSocket**: Real-time bidirectional communication
- **Encryption**: Cryptography library (Fernet/AES-128)
- **Server**: Uvicorn ASGI server
- **Frontend**: HTML5, CSS3 (Glass morphism design), Vanilla JavaScript

## 🧪 Testing & Verification

### Verify Encrypted Transmission

Watch the terminal outputs to confirm encryption:

**Dashboard Terminal**:
```
✓ Drone connected!
📊 Telemetry - Pos: (52.00, 48.00), Alt: 25.3m, Battery: 98.5%
```

**Drone Simulator Terminal**:
```
📡 Telemetry sent - Pos: (52.00, 48.00), Alt: 25.3m, Speed: 15.2m/s, Battery: 98.5%
```

### Health Check Endpoint

Check system status programmatically:
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "drone_connected": true,
  "active_clients": 1
}
```

### Battery Simulation

The drone's battery drains at **0.03% per second**:
- Starts at 100%
- Depletes over approximately 55 minutes
- When battery reaches 0%, status changes to "BATTERY_DEPLETED"
- Speed drops to 0 when depleted

## 🎓 Educational Value

This project demonstrates key concepts in:

1. **Network Telemetry**: Real-world pattern for transmitting sensor data
2. **Encryption in Transit**: Protecting data during network transmission
3. **WebSocket Protocol**: Efficient real-time communication
4. **Asynchronous Programming**: Python async/await patterns
5. **Client-Server Architecture**: Clean separation of concerns
6. **Real-time Visualization**: Live data display techniques
7. **Professional UI/UX**: Modern dashboard design patterns

## 🎯 Use Cases

- **Educational**: Learn about secure network communication
- **Portfolio**: Demonstrate full-stack development skills
- **Prototype**: Foundation for IoT monitoring systems
- **Training**: Practice WebSocket and encryption concepts
- **Demo**: Showcase real-time data transmission

## 🔧 Troubleshooting

### Connection Issues

**Problem**: Drone can't connect to dashboard
- **Solution**: Ensure dashboard is running first, then start drone

**Problem**: Web dashboard shows "Disconnected"
- **Solution**: Check that both dashboard and drone are running
- **Solution**: Refresh browser page

### Port Conflicts

**Problem**: Port 8000 already in use
- **Solution**: Stop other services using port 8000
- **Solution**: Modify `dashboard.py` to use different port:
  ```python
  uvicorn.run(app, host="0.0.0.0", port=8001)
  ```

### Encryption Errors

**Problem**: "Error decrypting telemetry"
- **Solution**: Delete `secret.key` and restart both components
- Both drone and dashboard must use the same key

## 📝 Future Enhancements

Potential improvements for extended functionality:

- [ ] Multiple drone support with unique identifiers
- [ ] Telemetry data logging to database (SQLite/PostgreSQL)
- [ ] Historical data visualization with charts
- [ ] Alert system for low battery or anomalies
- [ ] Export telemetry data (CSV, JSON)
- [ ] Authentication for dashboard access
- [ ] HTTPS/WSS support for production deployment
- [ ] Configurable flight patterns
- [ ] 3D visualization of drone position
- [ ] REST API for programmatic access

## 🤝 Contributing

This is a portfolio/educational project. Feedback and suggestions are welcome!

## 📄 License

This project is open source and available for educational purposes.

## 👤 Author

Created to demonstrate secure network telemetry, real-time data transmission, and professional dashboard development.

---

**Note**: This is a simulation for educational and demonstration purposes. The encryption implementation is suitable for learning but should be reviewed and hardened for production use cases.
