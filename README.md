# 🚁 Secure Drone Telemetry Dashboard

An interactive drone pilot simulator demonstrating secure network telemetry in real-time using Python, FastAPI, and WebSockets. This project showcases encrypted bidirectional communication between a simulated drone and a web-based control dashboard.

## 🎯 Features

- **Real-time Telemetry Transmission**: Live drone data streaming with sub-second latency
- **End-to-End Encryption**: All telemetry data and control commands are encrypted using Fernet symmetric encryption
- **Interactive 2D Visualization**: Visual representation of drone position on a 100x100 grid
- **Keyboard Controls**: Control the drone using arrow keys (Up, Down, Left, Right)
- **Live Data Display**: Real-time display of speed, battery level, altitude, heading, and GPS coordinates
- **Battery Simulation**: Realistic battery drain with recharge capability
- **WebSocket Communication**: Efficient bidirectional communication between drone and dashboard

## 🏗️ Architecture

### Components

1. **Encryption Module** (`encryption.py`)
   - Handles symmetric encryption/decryption using Fernet
   - Manages encryption keys
   - Secures both telemetry data and control commands

2. **Drone Simulator** (`drone_simulator.py`)
   - Simulates drone telemetry (position, speed, battery, altitude, heading)
   - Processes control commands and updates drone state
   - Encrypts telemetry before transmission
   - Maintains WebSocket connection to dashboard

3. **FastAPI Dashboard** (`dashboard.py`)
   - Serves web interface
   - Manages WebSocket connections from drone and web clients
   - Decrypts incoming telemetry
   - Encrypts and forwards control commands to drone

4. **Web Interface** (`static/index.html`)
   - Real-time 2D visualization of drone position
   - Live telemetry display panel
   - Keyboard input capture for drone control
   - Responsive design with gradient styling

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd telemetry_dashboard
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

You need to run two separate processes:

#### Terminal 1: Start the Dashboard Server

```bash
python dashboard.py
```

The dashboard will start on `http://localhost:8000`

#### Terminal 2: Start the Drone Simulator

```bash
python drone_simulator.py
```

The drone simulator will connect to the dashboard automatically.

#### Access the Dashboard

Open your web browser and navigate to:
```
http://localhost:8000
```

## 🎮 Controls

Once both the dashboard and drone simulator are running:

- **↑ (Up Arrow)**: Move drone north (increase latitude)
- **↓ (Down Arrow)**: Move drone south (decrease latitude)
- **← (Left Arrow)**: Move drone west (decrease longitude)
- **→ (Right Arrow)**: Move drone east (increase longitude)
- **R**: Recharge battery to 100%

## 📊 Dashboard Features

### Telemetry Display

The dashboard shows the following real-time information:

- **Status**: Current drone operational status
- **Position**: GPS coordinates (latitude, longitude)
- **Speed**: Current speed in meters per second
- **Altitude**: Height above ground in meters
- **Heading**: Direction in degrees (0° = North, 90° = East, 180° = South, 270° = West)
- **Battery Level**: Visual battery indicator with percentage

### Visual Elements

- **2D Grid**: 10x10 grid representing the flight area (0-100 coordinates)
- **Drone Icon**: Green circle (active) or red circle (low battery)
- **Direction Indicator**: Triangle pointing in the drone's heading direction
- **Trail Effect**: Visual trail showing recent movement path
- **Position Label**: Coordinates displayed next to drone

## 🔒 Security Features

### Encryption

All data transmission between the drone and dashboard is encrypted using **Fernet symmetric encryption**:

- **Telemetry Data**: Encrypted before transmission from drone
- **Control Commands**: Encrypted before transmission to drone
- **Key Management**: Automatic key generation and persistence
- **Shared Secret**: Both drone and dashboard use the same encryption key stored in `secret.key`

### Data Flow

1. Drone encrypts telemetry → Sends to dashboard
2. Dashboard decrypts telemetry → Displays to user
3. User sends command → Dashboard encrypts command
4. Encrypted command sent to drone → Drone decrypts and executes

## 📁 Project Structure

```
telemetry_dashboard/
├── dashboard.py              # FastAPI server
├── drone_simulator.py        # Drone simulation
├── encryption.py             # Encryption module
├── requirements.txt          # Python dependencies
├── secret.key               # Encryption key (auto-generated)
├── static/
│   └── index.html           # Web interface
└── README.md                # This file
```

## 🛠️ Technology Stack

- **Backend**: Python 3.8+, FastAPI
- **WebSockets**: Real-time bidirectional communication
- **Encryption**: Cryptography library (Fernet)
- **Frontend**: HTML5, CSS3, JavaScript (Canvas API)
- **Server**: Uvicorn ASGI server

## 🧪 Testing

### Verify Encrypted Communication

Watch the terminal output to see encrypted data transmission:

**Dashboard Terminal**:
```
Telemetry received - Position: (52.00, 48.00), Battery: 98.5%
Command received from client: right
Encrypted command sent to drone: right
```

**Drone Simulator Terminal**:
```
Moving RIGHT - New position: (52.00, 50.00)
```

### Battery Simulation

The battery drains at 0.05% per second. When it reaches 0%, the drone cannot move until recharged with the 'R' key.

## 🎓 Educational Value

This project demonstrates:

1. **Network Telemetry**: Real-time data transmission over networks
2. **Encryption in Transit**: Securing data during transmission
3. **WebSocket Protocol**: Bidirectional communication
4. **Real-time Visualization**: Canvas-based graphics rendering
5. **Event-driven Architecture**: Asynchronous programming patterns
6. **Client-Server Architecture**: Separation of concerns

## 📝 Future Enhancements

Potential improvements:

- [ ] Add multiple drone support
- [ ] Implement flight path recording and replay
- [ ] Add authentication for dashboard access
- [ ] Include 3D visualization
- [ ] Add obstacle detection and avoidance
- [ ] Implement GPS waypoint navigation
- [ ] Add telemetry data logging to database
- [ ] Create mobile-friendly touch controls

## 🤝 Contributing

This is a portfolio project, but suggestions and feedback are welcome!

## 📄 License

This project is open source and available for educational purposes.

## 👤 Author

Created as a demonstration of secure network telemetry and real-time communication systems.

---

**Note**: This is a simulation for educational and demonstration purposes. The encryption implementation is suitable for learning but should be reviewed and hardened for production use.
