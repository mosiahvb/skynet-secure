"""
FastAPI Dashboard Server
Receives encrypted telemetry data from drone and provides web interface.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import Optional
from encryption import SecureTransmission


app = FastAPI(title="Secure Drone Telemetry Dashboard")

# Encryption handler
encryption = SecureTransmission()

# Connection managers
drone_connection: Optional[WebSocket] = None
client_connections: list[WebSocket] = []


@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Serve the dashboard HTML interface."""
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read())


@app.websocket("/ws/drone")
async def drone_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for drone connection.
    Performs mutual authentication before accepting telemetry.
    """
    global drone_connection

    await websocket.accept()
    print("🔌 Drone attempting to connect...")

    try:
        # ===== MUTUAL AUTHENTICATION HANDSHAKE =====

        # Step 1: Receive drone authentication token
        drone_auth_token = await websocket.receive_text()
        print("🔑 Received drone authentication token")

        # Step 2: Verify drone identity
        if not encryption.verify_auth_token(drone_auth_token, "drone", timeout=30):
            print("❌ Drone authentication FAILED - Invalid token")
            await websocket.send_text("AUTH_FAILED")
            await websocket.close()
            return

        print("✓ Drone identity verified")

        # Step 3: Send challenge to drone
        challenge = encryption.generate_challenge()
        await websocket.send_text(f"CHALLENGE:{challenge}")
        print("🎯 Challenge sent to drone")

        # Step 4: Receive challenge response from drone
        challenge_response = await websocket.receive_text()

        # Step 5: Verify challenge response
        if not encryption.verify_challenge_response(challenge, challenge_response, "drone"):
            print("❌ Drone authentication FAILED - Invalid challenge response")
            await websocket.send_text("AUTH_FAILED")
            await websocket.close()
            return

        print("✓ Drone challenge response verified")

        # Step 6: Send API authentication token to drone
        api_auth_token = encryption.generate_auth_token("api")
        await websocket.send_text(f"API_TOKEN:{api_auth_token}")
        print("🔑 API authentication token sent to drone")

        # Step 7: Wait for drone to verify API and confirm
        confirmation = await websocket.receive_text()
        if confirmation != "AUTH_SUCCESS":
            print("❌ Mutual authentication FAILED - Drone rejected API")
            await websocket.close()
            return

        # Step 8: Confirm authentication success
        await websocket.send_text("AUTH_SUCCESS")

        print("=" * 60)
        print("🔒 MUTUAL AUTHENTICATION SUCCESSFUL")
        print("=" * 60)

        drone_connection = websocket

        # ===== AUTHENTICATED - BEGIN TELEMETRY TRANSMISSION =====

        while True:
            # Receive encrypted telemetry from drone
            encrypted_data = await websocket.receive_bytes()

            # Decrypt telemetry
            try:
                telemetry = encryption.decrypt_data(encrypted_data)
                print(f"📊 Telemetry - Pos: ({telemetry['latitude']:.2f}, {telemetry['longitude']:.2f}), "
                      f"Alt: {telemetry['altitude']:.1f}m, "
                      f"Battery: {telemetry['battery_level']:.1f}%")

                # Forward decrypted telemetry to all connected clients
                disconnected_clients = []
                for client in client_connections:
                    try:
                        await client.send_json(telemetry)
                    except Exception as e:
                        print(f"❌ Error sending to client: {e}")
                        disconnected_clients.append(client)

                # Remove disconnected clients
                for client in disconnected_clients:
                    client_connections.remove(client)

            except Exception as e:
                print(f"❌ Error decrypting telemetry: {e}")

    except WebSocketDisconnect:
        print("⚠️  Drone disconnected")
        drone_connection = None
    except Exception as e:
        print(f"❌ Drone connection error: {e}")
        drone_connection = None


@app.websocket("/ws/client")
async def client_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for web client connection.
    Streams telemetry data to connected web clients.
    """
    await websocket.accept()
    client_connections.append(websocket)
    print(f"✓ Web client connected! Total clients: {len(client_connections)}")

    try:
        # Keep connection alive and wait for disconnect
        while True:
            # Just receive any messages but don't process them
            # This keeps the WebSocket connection alive
            await websocket.receive_text()

    except WebSocketDisconnect:
        print(f"⚠️  Web client disconnected. Remaining clients: {len(client_connections) - 1}")
        if websocket in client_connections:
            client_connections.remove(websocket)
    except Exception as e:
        print(f"❌ Client connection error: {e}")
        if websocket in client_connections:
            client_connections.remove(websocket)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "drone_connected": drone_connection is not None,
        "active_clients": len(client_connections)
    }


@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    print("\n" + "=" * 60)
    print("🚁 SECURE DRONE TELEMETRY DASHBOARD")
    print("=" * 60)
    print("📡 Server starting...")
    print(f"🌐 Dashboard URL: http://localhost:8000")
    print(f"🔌 Drone WebSocket: ws://localhost:8000/ws/drone")
    print(f"🔒 Encryption: Fernet (AES-128)")
    print(f"🔐 Authentication: HMAC-SHA256 mutual auth")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
