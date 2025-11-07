# 🚁 Secure Drone Telemetry Dashboard

A real-time telemetry monitoring system demonstrating secure network data transmission using Python, FastAPI, and WebSockets. This project features an autonomous drone simulator that transmits encrypted telemetry data to a professional web-based dashboard for live monitoring and analysis.

## 🎯 Overview

This project showcases:
- **Mutual authentication** between drone and API using HMAC-SHA256
- **End-to-end encryption** of telemetry data during transmission
- **Real-time data streaming** via WebSocket protocol
- **Professional dashboard** interface for monitoring drone metrics
- **Autonomous flight simulation** with realistic telemetry generation

Perfect for demonstrating network telemetry concepts, secure data transmission, authentication protocols, and real-time monitoring systems.

## ✨ Features

### Security
- **Mutual Authentication**: HMAC-SHA256 based authentication ensuring drone and API verify each other's identity
- **Challenge-Response Protocol**: Prevents replay attacks using time-based tokens and random challenges
- **Fernet Symmetric Encryption**: All telemetry data is encrypted before transmission (AES-128)
- **Secure Key Management**: Automatic encryption and authentication key generation
- **Protected Data Flow**: No plaintext telemetry transmitted over the network
- **Separate Key Files**: Distinct keys for encryption (`secret.key`) and authentication (`auth.key`)

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
┌─────────────────┐                            ┌──────────────────┐
│                 │   1. Mutual Auth           │                  │
│  Drone Simulator│───────────────────────────>│  FastAPI Server  │
│                 │   (HMAC-SHA256)            │   (Dashboard)    │
│                 │                             │                  │
│                 │   2. Encrypted Telemetry   │                  │
│                 │───────────────────────────>│                  │
│  (Autonomous)   │   (Fernet/AES-128)         │                  │
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

1. **`encryption.py`** - Encryption & Authentication Module
   - Implements Fernet symmetric encryption (AES-128)
   - Implements HMAC-SHA256 authentication with challenge-response
   - Manages encryption and authentication keys (auto-generates on first run)
   - Generates and verifies authentication tokens with timestamps
   - Prevents replay attacks through time-based validation
   - Encrypts/decrypts telemetry data

2. **`drone_simulator.py`** - Autonomous Drone Simulator
   - Performs mutual authentication with API before transmitting data
   - Verifies API identity using authentication tokens
   - Simulates realistic drone flight patterns
   - Generates telemetry data (GPS, altitude, speed, battery, heading)
   - Encrypts telemetry before transmission
   - Maintains authenticated WebSocket connection to dashboard
   - Simulates battery drain over time

3. **`dashboard.py`** - FastAPI Server
   - Authenticates drone connections using HMAC-SHA256
   - Implements challenge-response protocol for mutual verification
   - Serves web dashboard interface
   - Manages WebSocket connections (authenticated drone and web clients)
   - Decrypts incoming telemetry from authenticated drone
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

### Mutual Authentication Flow

Before any telemetry is transmitted, the drone and API perform a mutual authentication handshake:

```
Step 1: Drone → API
  Sends authentication token (HMAC-SHA256 signed with timestamp)

Step 2: API → Drone
  Verifies drone token, sends random challenge

Step 3: Drone → API
  Responds to challenge (HMAC-SHA256 of challenge + identity)

Step 4: API → Drone
  Verifies challenge response, sends API authentication token

Step 5: Drone → API
  Verifies API token, sends confirmation

Step 6: API → Drone
  Sends final confirmation

Result: Both parties verified, connection authenticated ✓
```

**Authentication Features:**
- **HMAC-SHA256 Signatures**: Cryptographically secure message authentication
- **Time-based Tokens**: Prevents replay attacks (30-second validity window)
- **Challenge-Response**: Proves both parties possess the shared authentication key
- **Mutual Verification**: Both drone AND API verify each other's identity
- **Separate Auth Key**: Authentication uses `auth.key`, distinct from encryption key

### Encryption Flow

1. **Key Generation** (First Run):
   ```
   - System generates Fernet encryption key → secret.key
   - System generates authentication key → auth.key
   - Both drone and dashboard use same keys
   ```

2. **Telemetry Transmission** (After Authentication):
   ```
   Drone → Encrypt telemetry → Send via WebSocket → Dashboard receives
   ```

3. **Data Decryption**:
   ```
   Dashboard → Decrypt telemetry → Broadcast to web clients → Display
   ```

### Security Features

- **Mutual Authentication**: Both drone and API verify each other before data exchange
- **HMAC-SHA256**: Cryptographic authentication preventing token forgery
- **Replay Attack Protection**: Time-based tokens with 30-second validity
- **AES-128 Encryption**: Industry-standard symmetric encryption for telemetry
- **Dual Key System**: Separate keys for authentication and encryption
- **Challenge-Response**: Prevents man-in-the-middle attacks
- **Data Integrity**: Encryption prevents tampering during transmission
- **Automatic Key Management**: No manual configuration required

## 📁 Project Structure

```
telemetry_dashboard/
├── dashboard.py              # FastAPI server with authentication
├── drone_simulator.py        # Autonomous drone with authentication
├── encryption.py             # Encryption & authentication module
├── requirements.txt          # Python dependencies
├── secret.key               # Encryption key (auto-generated, gitignored)
├── auth.key                 # Authentication key (auto-generated, gitignored)
├── .gitignore               # Git ignore rules
├── static/
│   └── index.html           # Professional dashboard interface
└── README.md                # This file
```

## 🛠️ Technology Stack

- **Backend**: Python 3.8+
- **Web Framework**: FastAPI
- **WebSocket**: Real-time bidirectional communication
- **Authentication**: HMAC-SHA256 with challenge-response protocol
- **Encryption**: Cryptography library (Fernet/AES-128)
- **Server**: Uvicorn ASGI server
- **Frontend**: HTML5, CSS3 (Grayscale theme), Vanilla JavaScript

## 🧪 Testing & Verification

### Verify Mutual Authentication

Watch the terminal outputs to confirm the authentication handshake:

**Dashboard Terminal**:
```
🔌 Drone attempting to connect...
🔑 Received drone authentication token
✓ Drone identity verified
🎯 Challenge sent to drone
✓ Drone challenge response verified
🔑 API authentication token sent to drone
============================================================
🔒 MUTUAL AUTHENTICATION SUCCESSFUL
============================================================
```

**Drone Simulator Terminal**:
```
🔌 Connected to dashboard WebSocket
🔑 Sent drone authentication token
🎯 Received challenge from API
✓ Sent challenge response
🔑 Received API authentication token
✓ API identity verified
✓ Sent authentication confirmation
============================================================
🔒 MUTUAL AUTHENTICATION SUCCESSFUL
============================================================
```

### Verify Encrypted Transmission

After authentication, watch the telemetry flow:

**Dashboard Terminal**:
```
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

1. **Mutual Authentication**: HMAC-based authentication ensuring both parties verify each other
2. **Challenge-Response Protocol**: Preventing replay attacks and verifying identity
3. **Network Telemetry**: Real-world pattern for transmitting sensor data
4. **Encryption in Transit**: Protecting data during network transmission (Fernet/AES-128)
5. **WebSocket Protocol**: Efficient real-time bidirectional communication
6. **Asynchronous Programming**: Python async/await patterns for concurrent operations
7. **Cryptographic Security**: HMAC-SHA256 signatures and time-based token validation
8. **Client-Server Architecture**: Clean separation of concerns with security layers
9. **Real-time Visualization**: Live data display techniques
10. **Professional UI/UX**: Modern dashboard design patterns

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
