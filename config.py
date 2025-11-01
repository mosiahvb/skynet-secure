# config.py - Project Settings for Encrypted Telemetry Dashboard

# Network Settings
HOST = 'localhost'  # Computer address (localhost = this computer)
PORT = 6000         # Network port number (like a phone extension)

# Encryption Settings
# This is your secret key - keep it secret in real projects!
# Must be 16 bytes long for this example
ENCRYPTION_KEY = b'MySecretKey12345'

# Drone Simulation Settings
UPDATE_INTERVAL = 1.0  # Send data every 1 second
INITIAL_BATTERY = 100  # Start with full battery (100%)
INITIAL_LATITUDE = 34.0522   # Starting position (Los Angeles)
INITIAL_LONGITUDE = -118.2437
INITIAL_ALTITUDE = 0

# Dashboard Settings
MAX_DATA_POINTS = 50  # How many data points to keep in history
