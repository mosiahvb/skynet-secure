"""
FastAPI Dashboard Server
Receives encrypted telemetry data from drone and provides web interface.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import json
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
    Receives encrypted telemetry and forwards decrypted data to clients.
    """
    global drone_connection

    await websocket.accept()
    drone_connection = websocket
    print("Drone connected!")

    try:
        while True:
            # Receive encrypted telemetry from drone
            encrypted_data = await websocket.receive_bytes()

            # Decrypt telemetry
            try:
                telemetry = encryption.decrypt_data(encrypted_data)
                print(f"Telemetry received - Position: ({telemetry['latitude']:.2f}, {telemetry['longitude']:.2f}), "
                      f"Battery: {telemetry['battery_level']:.1f}%")

                # Forward decrypted telemetry to all connected clients
                disconnected_clients = []
                for client in client_connections:
                    try:
                        await client.send_json(telemetry)
                    except Exception as e:
                        print(f"Error sending to client: {e}")
                        disconnected_clients.append(client)

                # Remove disconnected clients
                for client in disconnected_clients:
                    client_connections.remove(client)

            except Exception as e:
                print(f"Error decrypting telemetry: {e}")

    except WebSocketDisconnect:
        print("Drone disconnected")
        drone_connection = None
    except Exception as e:
        print(f"Drone connection error: {e}")
        drone_connection = None


@app.websocket("/ws/client")
async def client_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for web client connection.
    Receives commands from client and forwards encrypted commands to drone.
    """
    await websocket.accept()
    client_connections.append(websocket)
    print(f"Client connected! Total clients: {len(client_connections)}")

    try:
        while True:
            # Receive command from client
            data = await websocket.receive_json()
            command = data.get("command")

            if command and drone_connection:
                print(f"Command received from client: {command}")

                # Encrypt command
                encrypted_command = encryption.encrypt_command(command)

                # Send encrypted command to drone
                try:
                    await drone_connection.send_bytes(encrypted_command)
                    print(f"Encrypted command sent to drone: {command}")
                except Exception as e:
                    print(f"Error sending command to drone: {e}")
                    await websocket.send_json({
                        "error": "Failed to send command to drone"
                    })
            elif not drone_connection:
                await websocket.send_json({
                    "error": "Drone not connected"
                })

    except WebSocketDisconnect:
        print("Client disconnected")
        client_connections.remove(websocket)
    except Exception as e:
        print(f"Client connection error: {e}")
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
    print("=" * 60)
    print("Secure Drone Telemetry Dashboard")
    print("=" * 60)
    print("Server starting...")
    print("Dashboard URL: http://localhost:8000")
    print("Waiting for drone connection on ws://localhost:8000/ws/drone")
    print("=" * 60)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
