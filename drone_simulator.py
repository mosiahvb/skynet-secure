# drone_simulator.py - Simulates a flying drone sending telemetry data

import socket
import json
import time
import random
import math
from encryption import SecureChannel
from config import *

class DroneSimulator:
    """
    Simulates a drone flying in a circular pattern and sending telemetry.
    
    This is like a toy drone that:
    - Flies in circles (patrol pattern)
    - Goes up and down in altitude
    - Has a battery that drains
    - Sends all this data to the dashboard
    """
    
    def __init__(self):
        """Initialize the drone with starting values."""
        # Position data
        self.latitude = INITIAL_LATITUDE
        self.longitude = INITIAL_LONGITUDE
        self.altitude = INITIAL_ALTITUDE
        
        # Movement data
        self.speed = 0
        self.heading = 0  # Direction in degrees (0 = North)
        
        # Status data
        self.battery = INITIAL_BATTERY
        self.status = "OK"
        
        # Internal counters
        self.time_step = 0
        self.mission_time = 0
        
        # Set up encryption
        self.secure_channel = SecureChannel(ENCRYPTION_KEY)
        
        print("🚁 Drone Simulator initialized")
        print(f"   Starting position: {self.latitude:.4f}, {self.longitude:.4f}")
        print(f"   Battery: {self.battery}%")
    
    def update_position(self):
        """
        Update the drone's position and status.
        This simulates the drone flying in a circular patrol pattern.
        """
        self.time_step += 0.1
        self.mission_time += UPDATE_INTERVAL
        
        # Move in a circle (like patrolling an area)
        radius = 0.001  # Size of the circle (in degrees)
        self.latitude = INITIAL_LATITUDE + radius * math.cos(self.time_step)
        self.longitude = INITIAL_LONGITUDE + radius * math.sin(self.time_step)
        
        # Calculate heading (direction of movement)
        self.heading = (math.degrees(self.time_step) % 360)
        
        # Altitude goes up and down smoothly
        self.altitude = 50 + 30 * math.sin(self.time_step * 0.5)
        
        # Speed varies slightly (realistic fluctuation)
        self.speed = 15 + random.uniform(-2, 2)
        
        # Battery drains slowly
        self.battery -= 0.1
        if self.battery < 0:
            self.battery = 0
            self.status = "CRITICAL - Battery Empty!"
        elif self.battery < 20:
            self.status = "WARNING - Low Battery"
        else:
            self.status = "OK"
    
    def get_telemetry(self):
        """
        Get current telemetry data as a dictionary.
        
        Returns:
            dict: All current sensor data
        """
        return {
            "latitude": round(self.latitude, 6),
            "longitude": round(self.longitude, 6),
            "altitude": round(self.altitude, 2),
            "speed": round(self.speed, 2),
            "heading": round(self.heading, 1),
            "battery": round(self.battery, 1),
            "status": self.status,
            "mission_time": round(self.mission_time, 1),
            "timestamp": time.time()
        }
    
    def send_telemetry(self, sock):
        """
        Send encrypted telemetry data through the socket.
        
        Args:
            sock: Network socket connected to the dashboard
        """
        # Get current telemetry
        telemetry = self.get_telemetry()
        
        # Convert to JSON (text format)
        json_data = json.dumps(telemetry)
        
        # Encrypt the data
        encrypted_data = self.secure_channel.encrypt(json_data)
        
        # Send the encrypted data
        # We add the length first so the receiver knows how much data to expect
        message_length = len(encrypted_data)
        sock.sendall(message_length.to_bytes(4, byteorder='big'))
        sock.sendall(encrypted_data)
        
        # Print status (so you can see it's working)
        print(f"📡 Sent: Altitude={telemetry['altitude']:.1f}m, "
              f"Battery={telemetry['battery']:.1f}%, "
              f"Status={telemetry['status']}")
    
    def run(self):
        """
        Main loop: Connect to dashboard and send telemetry continuously.
        """
        print(f"\n🔌 Connecting to dashboard at {HOST}:{PORT}...")
        
        try:
            # Create a socket (network connection)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((HOST, PORT))
            print("✓ Connected to dashboard!")
            print("\n🚁 Starting flight simulation...")
            print("   (Press Ctrl+C to stop)\n")
            
            # Main loop - keep sending data until stopped
            while self.battery > 0:
                # Update drone position
                self.update_position()
                
                # Send telemetry to dashboard
                self.send_telemetry(sock)
                
                # Wait before next update
                time.sleep(UPDATE_INTERVAL)
            
            print("\n🔋 Battery depleted - Mission ended")
            
        except ConnectionRefusedError:
            print("✗ Error: Could not connect to dashboard!")
            print("  Make sure dashboard.py is running first.")
        except KeyboardInterrupt:
            print("\n\n⏹️  Flight simulation stopped by user")
        except Exception as e:
            print(f"\n✗ Error: {e}")
        finally:
            sock.close()
            print("🔌 Connection closed")

if __name__ == "__main__":
    print("=" * 60)
    print("ENCRYPTED TELEMETRY - DRONE SIMULATOR")
    print("=" * 60)
    print()
    
    # Create and run the drone simulator
    drone = DroneSimulator()
    drone.run()
