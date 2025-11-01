# dashboard.py - Displays drone telemetry data with live visualizations

import socket
import json
import threading
from collections import deque
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from encryption import SecureChannel
from config import *

class TelemetryDashboard:
    """
    Receives encrypted telemetry and displays it with cool graphs.
    
    This is like your mission control center that shows:
    - Live map of drone's flight path
    - Battery gauge
    - Altitude and speed graphs
    - Current status information
    """
    
    def __init__(self):
        """Initialize the dashboard."""
        # Set up encryption
        self.secure_channel = SecureChannel(ENCRYPTION_KEY)
        
        # Storage for telemetry data (using deque for automatic size limit)
        self.timestamps = deque(maxlen=MAX_DATA_POINTS)
        self.altitudes = deque(maxlen=MAX_DATA_POINTS)
        self.speeds = deque(maxlen=MAX_DATA_POINTS)
        self.batteries = deque(maxlen=MAX_DATA_POINTS)
        self.latitudes = deque(maxlen=MAX_DATA_POINTS)
        self.longitudes = deque(maxlen=MAX_DATA_POINTS)
        
        # Current telemetry (most recent data)
        self.current_data = None
        
        # Control flags
        self.running = True
        self.data_received = False
        
        print("📊 Dashboard initialized")
    
    def receive_telemetry(self, sock):
        """
        Receive encrypted telemetry from the socket.
        
        Args:
            sock: Network socket connected to the drone
            
        Returns:
            dict: Decrypted telemetry data
        """
        # First, receive the message length (4 bytes)
        length_bytes = sock.recv(4)
        if not length_bytes:
            return None
        
        message_length = int.from_bytes(length_bytes, byteorder='big')
        
        # Now receive the encrypted data
        encrypted_data = b''
        while len(encrypted_data) < message_length:
            chunk = sock.recv(message_length - len(encrypted_data))
            if not chunk:
                return None
            encrypted_data += chunk
        
        # Decrypt the data
        decrypted_json = self.secure_channel.decrypt(encrypted_data)
        
        # Parse JSON back into a dictionary
        telemetry = json.loads(decrypted_json)
        
        return telemetry
    
    def update_data(self, telemetry):
        """
        Update the data storage with new telemetry.
        
        Args:
            telemetry: Dictionary of telemetry data
        """
        self.current_data = telemetry
        self.data_received = True
        
        # Add to history
        self.timestamps.append(telemetry['mission_time'])
        self.altitudes.append(telemetry['altitude'])
        self.speeds.append(telemetry['speed'])
        self.batteries.append(telemetry['battery'])
        self.latitudes.append(telemetry['latitude'])
        self.longitudes.append(telemetry['longitude'])
        
        # Print to console
        print(f"📡 Received: Alt={telemetry['altitude']:.1f}m, "
              f"Speed={telemetry['speed']:.1f}m/s, "
              f"Battery={telemetry['battery']:.1f}%, "
              f"Status={telemetry['status']}")
    
    def listen_for_data(self):
        """
        Listen for incoming telemetry data (runs in separate thread).
        """
        print(f"👂 Listening on {HOST}:{PORT}...")
        
        try:
            # Create a socket and bind it to our port
            server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_sock.bind((HOST, PORT))
            server_sock.listen(1)
            
            print("✓ Dashboard ready! Waiting for drone to connect...")
            
            # Accept connection from drone
            conn, addr = server_sock.accept()
            print(f"✓ Drone connected from {addr}")
            print("\n📊 Receiving telemetry data...\n")
            
            # Keep receiving data while running
            while self.running:
                telemetry = self.receive_telemetry(conn)
                if telemetry:
                    self.update_data(telemetry)
                else:
                    break
            
            conn.close()
            server_sock.close()
            
        except Exception as e:
            print(f"✗ Error in data listener: {e}")
    
    def update_plots(self, frame):
        """
        Update all the plots with new data (called automatically by matplotlib).
        
        Args:
            frame: Frame number (provided by matplotlib animation)
        """
        if not self.data_received or not self.current_data:
            return
        
        # Clear all subplots
        for ax in self.axes:
            ax.clear()
        
        # Plot 1: Flight Path Map
        ax1 = self.axes[0]
        if len(self.latitudes) > 0:
            ax1.plot(list(self.longitudes), list(self.latitudes), 'b-', linewidth=2, label='Flight Path')
            ax1.plot(self.longitudes[-1], self.latitudes[-1], 'ro', markersize=10, label='Current Position')
            ax1.set_xlabel('Longitude')
            ax1.set_ylabel('Latitude')
            ax1.set_title('🗺️  Drone Flight Path', fontsize=12, fontweight='bold')
            ax1.grid(True, alpha=0.3)
            ax1.legend()
        
        # Plot 2: Altitude Over Time
        ax2 = self.axes[1]
        if len(self.timestamps) > 0:
            ax2.plot(list(self.timestamps), list(self.altitudes), 'g-', linewidth=2)
            ax2.fill_between(list(self.timestamps), list(self.altitudes), alpha=0.3, color='green')
            ax2.set_xlabel('Mission Time (s)')
            ax2.set_ylabel('Altitude (m)')
            ax2.set_title('📈 Altitude', fontsize=12, fontweight='bold')
            ax2.grid(True, alpha=0.3)
        
        # Plot 3: Speed Over Time
        ax3 = self.axes[2]
        if len(self.timestamps) > 0:
            ax3.plot(list(self.timestamps), list(self.speeds), 'orange', linewidth=2)
            ax3.fill_between(list(self.timestamps), list(self.speeds), alpha=0.3, color='orange')
            ax3.set_xlabel('Mission Time (s)')
            ax3.set_ylabel('Speed (m/s)')
            ax3.set_title('⚡ Speed', fontsize=12, fontweight='bold')
            ax3.grid(True, alpha=0.3)
        
        # Plot 4: Battery Level
        ax4 = self.axes[3]
        battery = self.current_data['battery']
        
        # Color based on battery level
        if battery > 50:
            color = 'green'
        elif battery > 20:
            color = 'orange'
        else:
            color = 'red'
        
        # Draw battery bar
        ax4.barh([0], [battery], color=color, height=0.5)
        ax4.set_xlim(0, 100)
        ax4.set_ylim(-0.5, 0.5)
        ax4.set_xlabel('Battery Level (%)')
        ax4.set_title(f'🔋 Battery: {battery:.1f}%', fontsize=12, fontweight='bold')
        ax4.set_yticks([])
        ax4.grid(True, alpha=0.3, axis='x')
        
        # Add status text to battery plot
        status_text = f"Status: {self.current_data['status']}\n"
        status_text += f"Heading: {self.current_data['heading']:.1f}°"
        ax4.text(50, 0, status_text, ha='center', va='center', fontsize=10, 
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
    
    def run(self):
        """
        Main function: Start listening for data and show the dashboard.
        """
        # Start listening thread
        listener_thread = threading.Thread(target=self.listen_for_data)
        listener_thread.daemon = True
        listener_thread.start()
        
        # Set up the plot window
        self.fig, self.axes = plt.subplots(2, 2, figsize=(12, 8))
        self.axes = self.axes.flatten()
        
        # Set window title
        self.fig.canvas.manager.set_window_title('🚁 Encrypted Telemetry Dashboard')
        
        # Set up animation (updates plots automatically)
        ani = animation.FuncAnimation(
            self.fig, 
            self.update_plots, 
            interval=1000,  # Update every 1000ms (1 second)
            cache_frame_data=False
        )
        
        print("\n📊 Dashboard window opened!")
        print("   (Close the window to stop)\n")
        
        try:
            # Show the plot window (this blocks until window is closed)
            plt.show()
        except KeyboardInterrupt:
            print("\n⏹️  Dashboard stopped")
        finally:
            self.running = False

if __name__ == "__main__":
    print("=" * 60)
    print("ENCRYPTED TELEMETRY - DASHBOARD")
    print("=" * 60)
    print()
    
    # Create and run the dashboard
    dashboard = TelemetryDashboard()
    dashboard.run()
