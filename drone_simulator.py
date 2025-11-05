"""
Drone Simulator Module
Generates simulated drone telemetry data and responds to control commands.
"""

import asyncio
import json
import time
import random
from websockets.asyncio.client import connect
from encryption import SecureTransmission


class DroneSimulator:
    """Simulates a drone with telemetry data and control capabilities."""

    def __init__(self):
        """Initialize the drone with default parameters."""
        # Starting position (center of a 100x100 grid)
        self.latitude = 50.0
        self.longitude = 50.0

        # Drone parameters
        self.speed = 0.0  # meters per second
        self.battery_level = 100.0  # percentage
        self.altitude = 10.0  # meters
        self.heading = 0.0  # degrees (0=North, 90=East, 180=South, 270=West)

        # Movement parameters
        self.move_speed = 2.0  # units per command
        self.battery_drain_rate = 0.05  # percentage per second

        # Encryption handler
        self.encryption = SecureTransmission()

        # Connection state
        self.running = True

    def generate_telemetry(self) -> dict:
        """
        Generate current telemetry data.

        Returns:
            Dictionary containing drone telemetry
        """
        # Simulate battery drain
        if self.battery_level > 0:
            self.battery_level -= self.battery_drain_rate
            self.battery_level = max(0, self.battery_level)

        # Calculate speed based on recent movement
        telemetry = {
            "timestamp": time.time(),
            "latitude": round(self.latitude, 6),
            "longitude": round(self.longitude, 6),
            "altitude": round(self.altitude, 2),
            "speed": round(self.speed, 2),
            "battery_level": round(self.battery_level, 2),
            "heading": round(self.heading, 2),
            "status": "active" if self.battery_level > 0 else "battery_depleted"
        }

        return telemetry

    def process_command(self, command: str):
        """
        Process control command and update drone position.

        Args:
            command: Control command ('up', 'down', 'left', 'right', 'recharge')
        """
        if self.battery_level <= 0 and command != "recharge":
            print(f"Battery depleted! Cannot execute command: {command}")
            return

        if command == "up":
            self.latitude += self.move_speed
            self.heading = 0.0
            self.speed = self.move_speed * 10
            print(f"Moving UP - New position: ({self.latitude:.2f}, {self.longitude:.2f})")

        elif command == "down":
            self.latitude -= self.move_speed
            self.heading = 180.0
            self.speed = self.move_speed * 10
            print(f"Moving DOWN - New position: ({self.latitude:.2f}, {self.longitude:.2f})")

        elif command == "left":
            self.longitude -= self.move_speed
            self.heading = 270.0
            self.speed = self.move_speed * 10
            print(f"Moving LEFT - New position: ({self.latitude:.2f}, {self.longitude:.2f})")

        elif command == "right":
            self.longitude += self.move_speed
            self.heading = 90.0
            self.speed = self.move_speed * 10
            print(f"Moving RIGHT - New position: ({self.latitude:.2f}, {self.longitude:.2f})")

        elif command == "recharge":
            self.battery_level = 100.0
            self.speed = 0.0
            print("Battery recharged to 100%")

        else:
            print(f"Unknown command: {command}")
            return

        # Keep drone within bounds (0-100 for both coordinates)
        self.latitude = max(0, min(100, self.latitude))
        self.longitude = max(0, min(100, self.longitude))

    async def run(self, server_url="ws://localhost:8000/ws/drone"):
        """
        Main loop for the drone simulator.

        Args:
            server_url: WebSocket URL of the dashboard server
        """
        print("Starting Drone Simulator...")
        print(f"Initial position: ({self.latitude:.2f}, {self.longitude:.2f})")
        print(f"Connecting to dashboard at {server_url}...")

        while self.running:
            try:
                async with connect(server_url) as websocket:
                    print("Connected to dashboard!")

                    while self.running:
                        try:
                            # Generate and encrypt telemetry
                            telemetry = self.generate_telemetry()
                            encrypted_telemetry = self.encryption.encrypt_data(telemetry)

                            # Send encrypted telemetry
                            await websocket.send(encrypted_telemetry)

                            # Wait for commands with timeout
                            try:
                                encrypted_command = await asyncio.wait_for(
                                    websocket.recv(),
                                    timeout=1.0
                                )

                                # Decrypt and process command
                                command = self.encryption.decrypt_command(encrypted_command)
                                self.process_command(command)

                                # Immediately send updated telemetry
                                telemetry = self.generate_telemetry()
                                encrypted_telemetry = self.encryption.encrypt_data(telemetry)
                                await websocket.send(encrypted_telemetry)

                            except asyncio.TimeoutError:
                                # No command received, just continue sending telemetry
                                pass

                            # Small delay between updates
                            await asyncio.sleep(0.5)

                        except Exception as e:
                            print(f"Error in communication loop: {e}")
                            break

            except Exception as e:
                print(f"Connection failed: {e}")
                print("Retrying in 3 seconds...")
                await asyncio.sleep(3)

    def stop(self):
        """Stop the drone simulator."""
        self.running = False
        print("Drone simulator stopped.")


async def main():
    """Main entry point for the drone simulator."""
    drone = DroneSimulator()

    try:
        await drone.run()
    except KeyboardInterrupt:
        print("\nShutting down drone simulator...")
        drone.stop()


if __name__ == "__main__":
    asyncio.run(main())
