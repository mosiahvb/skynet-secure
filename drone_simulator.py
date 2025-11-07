"""
Drone Simulator Module
Generates simulated drone telemetry data with autonomous flight patterns.
"""

import asyncio
import time
import random
from websockets.asyncio.client import connect
from encryption import SecureTransmission


class DroneSimulator:
    """Simulates a drone with autonomous flight and telemetry generation."""

    def __init__(self):
        """Initialize the drone with default parameters."""
        # Starting position (center of a 100x100 grid)
        self.latitude = 50.0
        self.longitude = 50.0

        # Drone parameters
        self.speed = 15.0  # meters per second
        self.battery_level = 100.0  # percentage
        self.altitude = 25.0  # meters
        self.heading = 0.0  # degrees (0=North, 90=East, 180=South, 270=West)

        # Flight parameters
        self.move_speed = 0.5  # units per update
        self.battery_drain_rate = 0.03  # percentage per second
        self.altitude_variation = 2.0  # meters

        # Encryption handler
        self.encryption = SecureTransmission()

        # Connection state
        self.running = True

        # Flight pattern
        self.flight_time = 0

    def update_autonomous_flight(self):
        """Update drone position with autonomous flight pattern."""
        if self.battery_level <= 0:
            self.speed = 0
            return

        # Circular flight pattern
        self.flight_time += 0.1

        # Calculate new position in a circular pattern
        radius = 20
        center_lat = 50.0
        center_lon = 50.0

        self.latitude = center_lat + radius * random.uniform(0.8, 1.2) * \
                       (1 + 0.3 * random.random()) * \
                       (1 if random.random() > 0.5 else -1) * \
                       self.move_speed
        self.longitude = center_lon + radius * random.uniform(0.8, 1.2) * \
                        (1 + 0.3 * random.random()) * \
                        (1 if random.random() > 0.5 else -1) * \
                        self.move_speed

        # Keep within bounds
        self.latitude = max(10, min(90, self.latitude))
        self.longitude = max(10, min(90, self.longitude))

        # Update heading based on movement
        self.heading = (self.heading + random.uniform(-15, 15)) % 360

        # Vary altitude slightly
        self.altitude += random.uniform(-self.altitude_variation, self.altitude_variation)
        self.altitude = max(10, min(50, self.altitude))

        # Vary speed
        self.speed = random.uniform(10, 25)

    def generate_telemetry(self) -> dict:
        """
        Generate current telemetry data.

        Returns:
            Dictionary containing drone telemetry
        """
        # Update autonomous flight
        self.update_autonomous_flight()

        # Simulate battery drain
        if self.battery_level > 0:
            self.battery_level -= self.battery_drain_rate
            self.battery_level = max(0, self.battery_level)

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

    async def run(self, server_url="ws://localhost:8000/ws/drone"):
        """
        Main loop for the drone simulator.

        Args:
            server_url: WebSocket URL of the dashboard server
        """
        print("=" * 60)
        print("Starting Autonomous Drone Simulator")
        print("=" * 60)
        print(f"Initial position: ({self.latitude:.2f}, {self.longitude:.2f})")
        print(f"Connecting to dashboard at {server_url}...")
        print("=" * 60)

        while self.running:
            try:
                async with connect(server_url) as websocket:
                    print("🔌 Connected to dashboard WebSocket")

                    # ===== MUTUAL AUTHENTICATION HANDSHAKE =====

                    # Step 1: Send drone authentication token
                    drone_auth_token = self.encryption.generate_auth_token("drone")
                    await websocket.send(drone_auth_token)
                    print("🔑 Sent drone authentication token")

                    # Step 2: Receive and process challenge
                    challenge_msg = await websocket.recv()
                    if challenge_msg == "AUTH_FAILED":
                        print("❌ Authentication FAILED - API rejected drone token")
                        await websocket.close()
                        return

                    if not challenge_msg.startswith("CHALLENGE:"):
                        print("❌ Authentication FAILED - Invalid response from API")
                        await websocket.close()
                        return

                    challenge = challenge_msg.split(":", 1)[1]
                    print("🎯 Received challenge from API")

                    # Step 3: Send challenge response
                    challenge_response = self.encryption.generate_challenge_response(challenge, "drone")
                    await websocket.send(challenge_response)
                    print("✓ Sent challenge response")

                    # Step 4: Receive API authentication token
                    api_token_msg = await websocket.recv()
                    if api_token_msg == "AUTH_FAILED":
                        print("❌ Authentication FAILED - Challenge response rejected")
                        await websocket.close()
                        return

                    if not api_token_msg.startswith("API_TOKEN:"):
                        print("❌ Authentication FAILED - Invalid API response")
                        await websocket.close()
                        return

                    api_auth_token = api_token_msg.split(":", 1)[1]
                    print("🔑 Received API authentication token")

                    # Step 5: Verify API identity
                    if not self.encryption.verify_auth_token(api_auth_token, "api", timeout=30):
                        print("❌ Authentication FAILED - Invalid API token")
                        await websocket.send("AUTH_FAILED")
                        await websocket.close()
                        return

                    print("✓ API identity verified")

                    # Step 6: Confirm authentication success
                    await websocket.send("AUTH_SUCCESS")
                    print("✓ Sent authentication confirmation")

                    # Step 7: Wait for final confirmation
                    final_confirmation = await websocket.recv()
                    if final_confirmation != "AUTH_SUCCESS":
                        print("❌ Authentication FAILED - No final confirmation")
                        await websocket.close()
                        return

                    print("=" * 60)
                    print("🔒 MUTUAL AUTHENTICATION SUCCESSFUL")
                    print("=" * 60)
                    print("Transmitting encrypted telemetry data...\n")

                    # ===== AUTHENTICATED - BEGIN TELEMETRY TRANSMISSION =====

                    while self.running:
                        try:
                            # Generate and encrypt telemetry
                            telemetry = self.generate_telemetry()
                            encrypted_telemetry = self.encryption.encrypt_data(telemetry)

                            # Send encrypted telemetry
                            await websocket.send(encrypted_telemetry)

                            # Log telemetry transmission
                            print(f"📡 Telemetry sent - Pos: ({telemetry['latitude']:.2f}, {telemetry['longitude']:.2f}), "
                                  f"Alt: {telemetry['altitude']:.1f}m, "
                                  f"Speed: {telemetry['speed']:.1f}m/s, "
                                  f"Battery: {telemetry['battery_level']:.1f}%")

                            # Delay between updates
                            await asyncio.sleep(1.0)

                        except Exception as e:
                            print(f"❌ Error in communication loop: {e}")
                            break

            except Exception as e:
                print(f"❌ Connection failed: {e}")
                print("⏳ Retrying in 3 seconds...")
                await asyncio.sleep(3)

    def stop(self):
        """Stop the drone simulator."""
        self.running = False
        print("\n" + "=" * 60)
        print("Drone simulator stopped.")
        print("=" * 60)


async def main():
    """Main entry point for the drone simulator."""
    drone = DroneSimulator()

    try:
        await drone.run()
    except KeyboardInterrupt:
        print("\n\nShutting down drone simulator...")
        drone.stop()


if __name__ == "__main__":
    asyncio.run(main())
