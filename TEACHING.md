# Teaching Guide: Secure Drone Telemetry System

## 📚 Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Authentication Deep Dive](#authentication-deep-dive)
4. [Encryption Implementation](#encryption-implementation)
5. [WebSocket Communication](#websocket-communication)
6. [Drone Simulator Internals](#drone-simulator-internals)
7. [Dashboard Server Architecture](#dashboard-server-architecture)
8. [Frontend Implementation](#frontend-implementation)
9. [Security Best Practices](#security-best-practices)
10. [Code Walkthroughs](#code-walkthroughs)
11. [Learning Exercises](#learning-exercises)

---

## Project Overview

### What Are We Building?

This project implements a **secure, real-time telemetry monitoring system** that demonstrates how to:

1. **Authenticate** two systems to ensure they are who they claim to be
2. **Encrypt** sensitive data during transmission
3. **Stream** real-time data efficiently using WebSockets
4. **Visualize** live data in a professional dashboard

### Real-World Context

Imagine a drone flying a mission. It needs to:
- Send its position, battery, and speed back to a control center
- Ensure that only the legitimate control center receives this data
- Verify that commands actually come from the real control center
- Do all this in real-time (not delayed)

This is exactly what our system demonstrates!

### The Three Layers of Security

```
┌─────────────────────────────────────────────────────┐
│  Layer 1: MUTUAL AUTHENTICATION                     │
│  "Prove you are who you say you are"                │
│  - Both drone and API verify each other's identity  │
│  - Uses HMAC-SHA256 cryptographic signatures        │
│  - Prevents imposters from connecting               │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  Layer 2: ENCRYPTED TRANSMISSION                    │
│  "No one can read our messages"                     │
│  - All telemetry data encrypted with AES-128        │
│  - Even if intercepted, data is unreadable          │
│  - Uses Fernet symmetric encryption                 │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  Layer 3: REAL-TIME COMMUNICATION                   │
│  "Send data instantly, both directions"             │
│  - WebSocket protocol for bidirectional streaming   │
│  - Sub-second latency                               │
│  - Efficient for continuous updates                 │
└─────────────────────────────────────────────────────┘
```

---

## System Architecture

### The Big Picture

Our system has **three main components**:

```
    ┌──────────────────────┐
    │   Drone Simulator    │
    │  (drone_simulator.py)│
    │                      │
    │  - Generates flight  │
    │    telemetry data    │
    │  - Encrypts data     │
    │  - Authenticates     │
    └──────────┬───────────┘
               │
               │ WebSocket
               │ (Authenticated & Encrypted)
               │
               ↓
    ┌──────────────────────┐
    │   Dashboard API      │
    │   (dashboard.py)     │
    │                      │
    │  - Authenticates     │
    │    connections       │
    │  - Decrypts data     │
    │  - Routes to clients │
    └──────────┬───────────┘
               │
               │ WebSocket
               │ (Decrypted telemetry)
               │
               ↓
    ┌──────────────────────┐
    │   Web Dashboard      │
    │  (static/index.html) │
    │                      │
    │  - Displays data     │
    │  - Updates UI        │
    │  - No auth needed    │
    └──────────────────────┘
```

### Why This Architecture?

**Question:** Why separate the drone from the web dashboard?

**Answer:** Security and separation of concerns!

1. **The drone** has the secret authentication key and can prove its identity
2. **The API** acts as a security gateway, verifying the drone and decrypting data
3. **The web dashboard** just displays data - it doesn't need to know the secrets

This is called **defense in depth**: multiple layers of protection.

### Data Flow: From Flight to Display

Let's trace a single telemetry packet through the system:

```
Step 1: Drone measures position
├─ GPS: lat=50.123456, lon=-122.678901
├─ Battery: 87.3%
├─ Speed: 15.2 m/s
└─ Altitude: 25.8 m

Step 2: Drone creates JSON
{
  "latitude": 50.123456,
  "longitude": -122.678901,
  "battery_level": 87.3,
  "speed": 15.2,
  "altitude": 25.8,
  "heading": 45.0,
  "status": "active"
}

Step 3: Drone encrypts with AES-128
gAAAAABl... [random-looking encrypted bytes]

Step 4: Drone sends via WebSocket
→ Travels over network (could be intercepted, but it's encrypted!)

Step 5: API receives and decrypts
← Back to readable JSON

Step 6: API forwards to web clients
→ Sent to all connected browsers

Step 7: Browser updates display
✓ Position coordinates
✓ Battery bar updated
✓ Speed displayed
```

**Total time:** Less than 1 second!

---

## Authentication Deep Dive

### Why Authentication Matters

**Scenario without authentication:**
```
Attacker's Fake Drone: "Hi! I'm the real drone at position (0, 0)!"
Dashboard: "OK, I believe you!" ❌
Result: Dashboard shows wrong position
```

**Scenario with authentication:**
```
Attacker's Fake Drone: "Hi! I'm the real drone!"
Dashboard: "Prove it. What's the response to this challenge?"
Attacker: "Uh... 42?"
Dashboard: "Wrong. Connection rejected." ✓
Result: Only real drone can connect
```

### What Is HMAC-SHA256?

**HMAC** = Hash-based Message Authentication Code
**SHA256** = Secure Hash Algorithm, 256-bit output

Think of it like a **tamper-proof signature**:

1. You have a message: `"drone:1762474261"`
2. You have a secret key: `[random 32-byte key]`
3. HMAC combines them in a special way: `HMAC(key, message) = signature`

**Key properties:**
- Without the key, you can't create a valid signature
- Changing even 1 bit of the message completely changes the signature
- Can't reverse-engineer the key from the signature

### The 8-Step Authentication Handshake

Let's walk through each step with **actual code and data**:

#### Step 1: Drone Sends Authentication Token

**Drone code** (drone_simulator.py:129-131):
```python
drone_auth_token = self.encryption.generate_auth_token("drone")
await websocket.send(drone_auth_token)
print("🔑 Sent drone authentication token")
```

**What happens inside `generate_auth_token()`** (encryption.py:119-124):
```python
def generate_auth_token(self, identity: str) -> str:
    # 1. Get current timestamp (prevents replay attacks)
    timestamp = str(int(time.time())).encode()  # Example: b'1762474261'

    # 2. Create message: identity + timestamp
    message = identity.encode() + b':' + timestamp
    # Result: b'drone:1762474261'

    # 3. Sign the message with our secret key
    signature = hmac.new(self.auth_key, message, hashlib.sha256).digest()
    # Result: 32 bytes of cryptographic signature

    # 4. Encode as hex and combine with pipe separator
    token = message.hex() + '|' + signature.hex()
    # Result: "64726f6e653a31373632343734323631|5806eb1742f3933c..."

    return token
```

**Example token:**
```
64726f6e653a31373632343734323631|5806eb1742f3933c8a1b2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a
│                                │
│                                └─ HMAC-SHA256 signature (64 hex chars = 32 bytes)
└─ Message "drone:1762474261" in hex
```

**Why timestamp?** If someone captures this token, it will expire in 30 seconds, preventing replay attacks.

#### Step 2: API Verifies Token and Sends Challenge

**API code** (dashboard.py:44-59):
```python
# Receive token
drone_auth_token = await websocket.receive_text()
print("🔑 Received drone authentication token")

# Verify the drone's identity
if not encryption.verify_auth_token(drone_auth_token, "drone", timeout=30):
    print("❌ Drone authentication FAILED - Invalid token")
    await websocket.send_text("AUTH_FAILED")
    await websocket.close()
    return

print("✓ Drone identity verified")

# Generate a random challenge
challenge = encryption.generate_challenge()  # Returns 32 random bytes in hex
await websocket.send_text(f"CHALLENGE:{challenge}")
print("🎯 Challenge sent to drone")
```

**What happens in `verify_auth_token()`** (encryption.py:138-172):
```python
def verify_auth_token(self, token: str, expected_identity: str, timeout: int = 30) -> bool:
    try:
        # 1. Split token into message and signature
        parts = token.split('|')
        if len(parts) != 2:
            return False  # Invalid format

        message_hex = parts[0]
        signature_hex = parts[1]

        # 2. Convert from hex back to bytes
        message = bytes.fromhex(message_hex)
        received_signature = bytes.fromhex(signature_hex)

        # 3. Recompute the signature with our key
        expected_signature = hmac.new(self.auth_key, message, hashlib.sha256).digest()

        # 4. Compare signatures in constant time (prevents timing attacks)
        if not hmac.compare_digest(received_signature, expected_signature):
            return False  # Signature doesn't match = fake token!

        # 5. Parse the message
        message_str = message.decode()  # "drone:1762474261"
        identity, timestamp_str = message_str.split(':')

        # 6. Check identity matches
        if identity != expected_identity:
            return False  # Token is for wrong identity

        # 7. Check timestamp isn't too old (prevents replay attacks)
        timestamp = int(timestamp_str)
        current_time = int(time.time())
        if abs(current_time - timestamp) > timeout:
            return False  # Token expired!

        return True  # All checks passed! ✓

    except Exception:
        return False  # Any error = invalid token
```

**Why this works:**
- Only someone with the `auth_key` can create a valid signature
- The timestamp ensures the token is recent
- The signature verification proves the sender has the key

**The Challenge:**
```python
challenge = secrets.token_bytes(32).hex()
# Example: "a7f3c9e2d4b8f1a6c3e5d7b9f0a2c4e6..."
```

This is a random 32-byte value that the drone must sign to prove it has the key.

#### Step 3: Drone Responds to Challenge

**Drone code** (drone_simulator.py:145-151):
```python
# Extract the challenge
challenge = challenge_msg.split(":", 1)[1]
print("🎯 Received challenge from API")

# Generate response
challenge_response = self.encryption.generate_challenge_response(challenge, "drone")
await websocket.send(challenge_response)
print("✓ Sent challenge response")
```

**What happens in `generate_challenge_response()`** (encryption.py:182-196):
```python
def generate_challenge_response(self, challenge: str, identity: str) -> str:
    # 1. Convert challenge from hex to bytes
    challenge_bytes = bytes.fromhex(challenge)

    # 2. Combine challenge with identity
    message = challenge_bytes + identity.encode()
    # Example: [random 32 bytes] + b'drone'

    # 3. Sign with our secret key
    response = hmac.new(self.auth_key, message, hashlib.sha256).digest()

    # 4. Return as hex
    return response.hex()
```

**Why challenge-response?**
- The challenge is random and different every time
- Even if an attacker captured a previous response, it won't work for a new challenge
- This proves the drone has the key **right now**, not just in the past

#### Step 4: API Verifies Challenge Response

**API code** (dashboard.py:62-70):
```python
# Receive the response
challenge_response = await websocket.receive_text()

# Verify it matches what we expect
if not encryption.verify_challenge_response(challenge, challenge_response, "drone"):
    print("❌ Drone authentication FAILED - Invalid challenge response")
    await websocket.send_text("AUTH_FAILED")
    await websocket.close()
    return

print("✓ Drone challenge response verified")
```

**Verification** (encryption.py:198-214):
```python
def verify_challenge_response(self, challenge: str, response: str, expected_identity: str) -> bool:
    try:
        # Recompute what the response should be
        expected_response = self.generate_challenge_response(challenge, expected_identity)

        # Compare in constant time (prevents timing attacks)
        return hmac.compare_digest(response, expected_response)
    except Exception:
        return False
```

**At this point:** The API knows the drone is legitimate! ✓

#### Step 5-8: API Authenticates to Drone

Now the roles reverse - the drone verifies the API:

**Step 5: API sends its token** (dashboard.py:73-76)
**Step 6: Drone verifies API token** (drone_simulator.py:169-174)
**Step 7: Drone confirms** (drone_simulator.py:177-179)
**Step 8: API confirms** (dashboard.py:85-86)

**Result:** Both sides have proven their identity! 🔒

### Replay Attack Prevention

**Without timestamps:**
```
Day 1: Attacker captures token "abc123"
Day 30: Attacker replays token "abc123" - it still works! ❌
```

**With timestamps (our implementation):**
```
12:00:00 - Token generated with timestamp "1762474261"
12:00:15 - Attacker captures token
12:00:45 - Attacker replays token (timestamp is now 45 seconds old)
         - API rejects: "Token expired!" ✓
```

**Code check** (encryption.py:163-165):
```python
if abs(current_time - timestamp) > timeout:  # timeout = 30 seconds
    return False  # Token is too old!
```

---

## Encryption Implementation

### Why Fernet/AES-128?

**Fernet** is a specification that uses:
- **AES-128** in CBC mode for encryption
- **HMAC** for authentication of ciphertext
- **Timestamp** to detect old messages

It's a **symmetric encryption** scheme: the same key encrypts and decrypts.

### Symmetric vs Asymmetric Encryption

**Symmetric (what we use):**
```
Key: [secret]
Plaintext: "Hello" + Key → Encryption → Ciphertext: "x7f3a..."
Ciphertext: "x7f3a..." + Key → Decryption → Plaintext: "Hello"
```
- ✓ Fast
- ✓ Good for bulk data
- ✗ Both sides need the same secret key

**Asymmetric (like RSA):**
```
Public Key: [anyone can have]
Private Key: [only one person has]
```
- ✓ Don't need to share secret key
- ✗ Much slower
- Best for key exchange, not bulk data

**Our choice:** Symmetric is perfect because both drone and API are controlled by the same organization and can share a key securely.

### How Encryption Works in Our Code

#### Key Generation (First Run)

**Code** (encryption.py:33-42):
```python
def _load_or_generate_key(self):
    """Load existing encryption key or generate a new one."""
    if os.path.exists(self.key_file):
        # Key exists, load it
        with open(self.key_file, 'rb') as f:
            return f.read()
    else:
        # Generate new random key
        key = Fernet.generate_key()
        # Example: b'A8fT3xZ...' (44 characters base64)

        # Save for future use
        with open(self.key_file, 'wb') as f:
            f.write(key)
        return key
```

**Important:** Both drone and dashboard run this code, so they both get the same key file.

#### Encrypting Telemetry

**Drone code** (drone_simulator.py:198-199):
```python
telemetry = self.generate_telemetry()  # Python dict
encrypted_telemetry = self.encryption.encrypt_data(telemetry)
await websocket.send(encrypted_telemetry)
```

**Encryption function** (encryption.py:56-67):
```python
def encrypt_data(self, data: dict) -> bytes:
    # 1. Convert dict to JSON string
    json_data = json.dumps(data)
    # Example: '{"latitude": 50.123, "longitude": -122.678, ...}'

    # 2. Encrypt with Fernet
    encrypted = self.cipher.encrypt(json_data.encode())
    # Result: b'gAAAAABl...' (random-looking bytes)

    return encrypted
```

**What Fernet does internally:**
1. Generates a random IV (initialization vector)
2. Encrypts data with AES-128-CBC
3. Computes HMAC of ciphertext
4. Packages it all together with a timestamp
5. Encodes as base64

**Example transformation:**
```
Original: {"latitude": 50.123, "battery": 87.3}
↓
Encrypted: gAAAAABl3xZ7c9f2a1b4e6d8c0f3a5e7b9d1c3e5f7a9b1d3e5f7c9a1b3d5e7f9...
```

Even if someone intercepts this, without the key, it's just random noise!

#### Decrypting Telemetry

**API code** (dashboard.py:100-108):
```python
# Receive encrypted bytes
encrypted_data = await websocket.receive_bytes()

# Decrypt
try:
    telemetry = encryption.decrypt_data(encrypted_data)
    # Back to dict: {"latitude": 50.123, ...}

    print(f"📊 Telemetry - Pos: ({telemetry['latitude']:.2f}, ...)")
except Exception as e:
    print(f"❌ Error decrypting telemetry: {e}")
```

**Decryption function** (encryption.py:69-80):
```python
def decrypt_data(self, encrypted_data: bytes) -> dict:
    # 1. Decrypt with Fernet
    decrypted = self.cipher.decrypt(encrypted_data)
    # Result: b'{"latitude": 50.123, ...}'

    # 2. Convert JSON string back to dict
    return json.loads(decrypted.decode())
```

### Why Separate Keys for Auth and Encryption?

**Two keys:**
- `secret.key` - For encrypting telemetry data
- `auth.key` - For authentication signatures

**Benefit: Key separation principle**
```
If auth key is compromised:
  ✗ Attacker can authenticate
  ✓ But can't decrypt past telemetry data

If encryption key is compromised:
  ✗ Attacker can decrypt telemetry
  ✓ But can't authenticate as drone
```

This is called **defense in depth** - multiple independent security layers.

---

## WebSocket Communication

### Why WebSockets Instead of HTTP?

**HTTP (Traditional):**
```
Client: "Give me data" (request)
Server: "Here's data" (response)
[Connection closes]

[1 second later]
Client: "Give me data again" (new request)
Server: "Here's new data" (response)
[Connection closes]
```

**Problems:**
- Must constantly open/close connections (overhead!)
- Server can't push data; client must ask
- Higher latency

**WebSocket (What We Use):**
```
Client: "Let's open a persistent connection"
Server: "OK!"
[Connection stays open]

Server: "Here's data" (pushed anytime)
Client: "Got it!"
Server: "Here's more data"
Client: "Got it!"
Client: "Here's a command"
Server: "Received!"
```

**Benefits:**
- ✓ Connection stays open
- ✓ Bidirectional: both sides can send anytime
- ✓ Lower latency
- ✓ Less overhead

### WebSocket Lifecycle

```
┌─────────────────────────────────────────────┐
│ 1. HANDSHAKE (Upgrade from HTTP)           │
│    Client: "Upgrade: websocket"             │
│    Server: "101 Switching Protocols"        │
└─────────────────┬───────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────┐
│ 2. CONNECTED (Bidirectional messages)       │
│    ├─ Text messages (JSON, strings)         │
│    └─ Binary messages (encrypted data)      │
└─────────────────┬───────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────┐
│ 3. CLOSING (Graceful shutdown)              │
│    Client/Server: "Close frame"             │
│    Other side: "Close frame ACK"            │
└─────────────────────────────────────────────┘
```

### How Our Code Uses WebSockets

#### Server Side (Dashboard)

**Setting up WebSocket endpoint** (dashboard.py:29-30):
```python
@app.websocket("/ws/drone")
async def drone_websocket(websocket: WebSocket):
```

The `@app.websocket` decorator tells FastAPI: "This function handles WebSocket connections at this URL."

**Accepting connection** (dashboard.py:37):
```python
await websocket.accept()
```

This completes the WebSocket handshake.

**Receiving data** (dashboard.py:44, 98):
```python
# Text message (for authentication)
message = await websocket.receive_text()

# Binary data (for encrypted telemetry)
data = await websocket.receive_bytes()
```

**Sending data** (dashboard.py:50, 58):
```python
# Text message
await websocket.send_text("CHALLENGE:abc123")

# Binary data
await websocket.send_bytes(encrypted_data)
```

#### Client Side (Drone)

**Connecting** (drone_simulator.py:123):
```python
from websockets.asyncio.client import connect

async with connect(server_url) as websocket:
    # websocket is now connected
```

The `async with` ensures the connection is properly closed even if errors occur.

**Sending/Receiving** (drone_simulator.py:130, 134):
```python
await websocket.send(auth_token)
response = await websocket.recv()
```

### Error Handling and Reconnection

**Drone reconnection logic** (drone_simulator.py:121-168):
```python
while self.running:
    try:
        async with connect(server_url) as websocket:
            # ... authentication and telemetry ...

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("⏳ Retrying in 3 seconds...")
        await asyncio.sleep(3)
```

**Why this matters:**
- Network issues happen!
- Server might restart
- This ensures the drone automatically reconnects

### Async/Await Explained

**Synchronous (Blocking) Code:**
```python
data = websocket.receive()  # Program stops here until data arrives
process(data)                # This waits for receive() to finish
```

**Asynchronous (Non-blocking) Code:**
```python
data = await websocket.receive()  # Program can do other things while waiting
process(data)                      # Runs after data arrives
```

**Benefits:**
- Can handle multiple connections simultaneously
- Better resource utilization
- Responsive to other events while waiting

**In our code:**
```python
async def drone_websocket(websocket: WebSocket):
    while True:
        # This waits for data but doesn't block the entire server
        encrypted_data = await websocket.receive_bytes()
        # Process it...
```

While waiting for drone data, the server can still:
- Handle web client connections
- Respond to health checks
- Process other drones (if we had multiple)

---

## Drone Simulator Internals

### Autonomous Flight Pattern

**Goal:** Make the drone move realistically without user input.

**Code** (drone_simulator.py:42-77):
```python
def update_autonomous_flight(self):
    if self.battery_level <= 0:
        self.speed = 0
        return

    # Add randomness to simulate realistic flight
    self.latitude = center_lat + radius * random.uniform(0.8, 1.2) * \
                   (1 + 0.3 * random.random()) * \
                   (1 if random.random() > 0.5 else -1) * \
                   self.move_speed
```

**How it works:**
1. **Base position:** Center at (50, 50)
2. **Radius:** Fly within 20 units of center
3. **Randomness:**
   - `random.uniform(0.8, 1.2)` - Vary distance
   - `random.random()` - Add noise
   - Random sign - Move in any direction

**Result:** The drone wanders around the center in a semi-random pattern.

**Bounds checking** (drone_simulator.py:66-67):
```python
self.latitude = max(10, min(90, self.latitude))
self.longitude = max(10, min(90, self.longitude))
```

This keeps the drone on the "map" (between 10 and 90 for both coordinates).

### Telemetry Data Generation

**Code** (drone_simulator.py:79-105):
```python
def generate_telemetry(self) -> dict:
    # Update position first
    self.update_autonomous_flight()

    # Drain battery
    if self.battery_level > 0:
        self.battery_level -= self.battery_drain_rate
        self.battery_level = max(0, self.battery_level)

    # Package all data
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
```

**Why round the values?**
- GPS precision: 6 decimals = ~11cm accuracy (realistic)
- Altitude: 2 decimals = 1cm (good enough)
- Battery: 2 decimals = 0.01% precision

**Battery simulation** (drone_simulator.py:90-92):
```python
self.battery_level -= self.battery_drain_rate  # 0.03% per second
```

At this rate: 100% / 0.03% = ~3333 seconds = ~55 minutes of flight time.

### Main Loop

**Code** (drone_simulator.py:195-216):
```python
while self.running:
    try:
        # 1. Generate telemetry
        telemetry = self.generate_telemetry()
        encrypted_telemetry = self.encryption.encrypt_data(telemetry)

        # 2. Send it
        await websocket.send(encrypted_telemetry)

        # 3. Log it
        print(f"📡 Telemetry sent - Pos: ({telemetry['latitude']:.2f}, ...)")

        # 4. Wait before next update
        await asyncio.sleep(1.0)

    except Exception as e:
        print(f"❌ Error in communication loop: {e}")
        break
```

**Update rate:** 1 update per second (1 Hz)

**Why 1 second?**
- Fast enough for real-time feel
- Not so fast it overwhelms the network
- Balances responsiveness vs. efficiency

---

## Dashboard Server Architecture

### FastAPI Application Structure

**Code** (dashboard.py:12-15):
```python
app = FastAPI(title="Secure Drone Telemetry Dashboard")

# Encryption handler (shared by all connections)
encryption = SecureTransmission()

# Connection managers
drone_connection: Optional[WebSocket] = None
client_connections: list[WebSocket] = []
```

**Why global variables?**
- `encryption`: One instance, shared by all connections (same keys)
- `drone_connection`: Track the current drone (only one drone supported)
- `client_connections`: List of all web browsers viewing the dashboard

### Three Endpoints

**1. HTTP Endpoint** (dashboard.py:22-26):
```python
@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read())
```

This serves the web page when you visit `http://localhost:8000`

**2. Drone WebSocket** (dashboard.py:29):
```python
@app.websocket("/ws/drone")
async def drone_websocket(websocket: WebSocket):
```

For authenticated drone connections only.

**3. Client WebSocket** (dashboard.py:130):
```python
@app.websocket("/ws/client")
async def client_websocket(websocket: WebSocket):
```

For web browsers (no authentication needed - they just view data).

### Broadcasting Telemetry to Multiple Clients

**Code** (dashboard.py:106-118):
```python
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
```

**How broadcasting works:**
```
Drone → API receives telemetry
        ↓
        API decrypts
        ↓
    ┌───┴───┬───────┬───────┐
    ↓       ↓       ↓       ↓
 Client1 Client2 Client3 Client4
(Browser) (Browser) (Browser) (Browser)
```

**Why track disconnected clients?**
If a browser closes, trying to send to it raises an exception. We collect these failed sends and remove those clients from the list.

---

## Frontend Implementation

### HTML Structure

The dashboard uses a **card-based layout**:

```html
<div class="dashboard-grid">
    <!-- Status Panel -->
    <div class="panel">
        <h2>📊 System Status</h2>
        <div class="telemetry-item">...</div>
    </div>

    <!-- Location Panel -->
    <div class="panel">
        <h2>📍 Location Data</h2>
        <div class="telemetry-item">...</div>
    </div>

    <!-- Flight Data Panel -->
    <div class="panel">
        <h2>✈️ Flight Data</h2>
        <div class="telemetry-item">...</div>
    </div>

    <!-- Navigation Panel -->
    <div class="panel">
        <h2>🧭 Navigation</h2>
        <div class="telemetry-item">...</div>
    </div>
</div>
```

**CSS Grid Layout** (static/index.html:73-78):
```css
.dashboard-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
}
```

This automatically arranges panels in a responsive grid:
- Desktop: 2-4 columns
- Tablet: 2 columns
- Mobile: 1 column

### WebSocket Client Connection

**JavaScript code** (static/index.html:352-380):
```javascript
function connect() {
    // Build WebSocket URL
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/client`;

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        console.log('Connected to dashboard');
        document.getElementById('connectionStatus').className = 'connection-status connected';
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        updateTelemetry(data);
        updatePacketStats();
    };

    ws.onclose = () => {
        console.log('Disconnected from dashboard');
        setTimeout(connect, 3000);  // Reconnect after 3 seconds
    };
}

// Start connection
connect();
```

**Event handlers:**
- `onopen`: Connection established
- `onmessage`: New telemetry data received
- `onclose`: Connection lost (auto-reconnect)

### Updating the UI

**JavaScript code** (static/index.html:383-421):
```javascript
function updateTelemetry(data) {
    // Update status
    document.getElementById('status').textContent = data.status.toUpperCase();

    // Update location
    document.getElementById('latitude').textContent = data.latitude.toFixed(6);
    document.getElementById('longitude').textContent = data.longitude.toFixed(6);

    // Update flight data
    document.getElementById('altitude').textContent = data.altitude.toFixed(1);
    document.getElementById('speed').textContent = data.speed.toFixed(1);

    // Update navigation
    document.getElementById('heading').textContent = data.heading.toFixed(1);
    document.getElementById('direction').textContent = getDirection(data.heading);

    // Update battery
    const batteryLevel = data.battery_level;
    document.getElementById('batteryLevel').textContent = batteryLevel.toFixed(1) + '%';
    document.getElementById('batteryFill').style.width = batteryLevel + '%';

    // Change color based on level
    if (batteryLevel < 20) {
        document.getElementById('batteryFill').classList.add('battery-low');
    }
}
```

**Why `toFixed()`?**
- Limits decimal places for readability
- `toFixed(6)` for GPS: 50.123456
- `toFixed(1)` for altitude: 25.3
- `toFixed(1)` for battery: 87.3

### Compass Direction Conversion

**JavaScript code** (static/index.html:424-429):
```javascript
function getDirection(heading) {
    const directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                      'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
    const index = Math.round(heading / 22.5) % 16;
    return directions[index];
}
```

**How it works:**
- 360° / 16 directions = 22.5° per direction
- 0° → N, 45° → NE, 90° → E, 180° → S, 270° → W

**Example:**
- Heading: 47° → 47 / 22.5 = 2.09 → rounds to 2 → directions[2] = 'NE'

---

## Security Best Practices

### 1. Never Commit Secrets to Git

**`.gitignore`** (lines 38-40):
```
# Security - encryption and authentication keys
secret.key
auth.key
```

**Why?**
- Git history is permanent
- If pushed to GitHub, keys are exposed forever
- Anyone with keys can impersonate your drone

### 2. Constant-Time Comparison

**Code** (encryption.py:152):
```python
if not hmac.compare_digest(received_signature, expected_signature):
    return False
```

**Why not use `==`?**

**Vulnerable code:**
```python
if received == expected:  # DON'T DO THIS!
```

**Timing attack:**
```
Attacker tries: "aaaa..." → Fails at character 1 → Takes 1ms
Attacker tries: "5aaa..." → Fails at character 2 → Takes 2ms
Attacker tries: "58aa..." → Fails at character 3 → Takes 3ms
...
Attacker learns the signature one byte at a time!
```

**Safe code:**
```python
hmac.compare_digest(received, expected)
# Always takes the same time regardless of where they differ
```

### 3. Time-based Token Expiration

**Code** (encryption.py:163-165):
```python
timestamp = int(timestamp_str)
current_time = int(time.time())
if abs(current_time - timestamp) > timeout:  # timeout = 30 seconds
    return False
```

**Attack prevented:**
```
10:00:00 - Attacker captures valid token
10:05:00 - Attacker tries to replay token
         - Server: "This token is 5 minutes old, rejected!"
```

**Why 30 seconds?**
- Long enough for network delays
- Short enough to prevent meaningful replay window

### 4. Separate Keys for Different Purposes

**Two keys:**
- `secret.key` (44 bytes, Fernet format) - For encrypting telemetry
- `auth.key` (32 bytes, random) - For HMAC authentication

**Benefit:**
If one key is compromised, the other operation remains secure.

### 5. Fail Securely

**Code pattern everywhere:**
```python
try:
    # Attempt operation
    if not verify_something():
        return False
except Exception:
    return False  # Any error = deny access
```

**Never:**
```python
try:
    # Attempt operation
except Exception:
    return True  # DON'T allow access on error!
```

### 6. Input Validation

**Token format check** (encryption.py:140-142):
```python
parts = token.split('|')
if len(parts) != 2:
    return False  # Reject malformed tokens immediately
```

**Why?**
Prevents:
- Buffer overflow attempts
- Injection attacks
- Malformed data crashing the system

### 7. Graceful Degradation

**Battery depleted handling** (drone_simulator.py:44-46):
```python
if self.battery_level <= 0:
    self.speed = 0
    return
```

The drone doesn't crash when battery is depleted - it just stops moving and reports status.

---

## Code Walkthroughs

### Walkthrough 1: Complete Authentication Sequence

Let's trace the authentication with actual data:

**Time: T+0s - Drone generates token**
```python
# encryption.py:119-124
identity = "drone"
timestamp = "1762474261"  # Current Unix timestamp
message = b"drone:1762474261"
signature = HMAC-SHA256(auth_key, message)
token = "64726f6e653a31373632343734323631|5806eb1742f3933c..."
```

**Time: T+0.1s - Drone sends token**
```python
# drone_simulator.py:130
await websocket.send(token)
# Travels over network...
```

**Time: T+0.2s - API receives and verifies**
```python
# dashboard.py:44
drone_auth_token = await websocket.receive_text()
# drone_auth_token = "64726f6e653a31373632343734323631|5806..."

# encryption.py:140-152
parts = drone_auth_token.split('|')  # Split into message and signature
message = bytes.fromhex(parts[0])    # b"drone:1762474261"
received_sig = bytes.fromhex(parts[1])

# Recompute signature
expected_sig = HMAC-SHA256(auth_key, message)

# Compare
if hmac.compare_digest(received_sig, expected_sig):  # ✓ Match!
    # Check timestamp
    identity, timestamp_str = message.decode().split(':')
    if "drone" == identity:  # ✓ Correct identity
        if (current_time - int(timestamp_str)) < 30:  # ✓ Recent
            return True  # Token valid!
```

**Time: T+0.3s - API sends challenge**
```python
# dashboard.py:57-58
challenge = secrets.token_bytes(32).hex()
# challenge = "a7f3c9e2d4b8f1a6c3e5d7b9f0a2c4e6..."
await websocket.send_text(f"CHALLENGE:{challenge}")
```

**Time: T+0.4s - Drone responds**
```python
# drone_simulator.py:149-150
challenge_response = HMAC-SHA256(auth_key, challenge_bytes + b"drone")
await websocket.send(challenge_response)
```

**Time: T+0.5s - API verifies**
```python
# dashboard.py:65
expected = HMAC-SHA256(auth_key, challenge_bytes + b"drone")
if hmac.compare_digest(challenge_response, expected):  # ✓ Match!
    print("✓ Drone challenge response verified")
```

**Time: T+0.6s - API sends its token (drone verifies similarly)**
**Time: T+0.8s - Both sides authenticated! 🔒**

### Walkthrough 2: Telemetry Flow with Encryption

**Drone side:**
```python
# 1. Generate telemetry (drone_simulator.py:198)
telemetry = {
    "timestamp": 1762474300.123,
    "latitude": 51.234567,
    "longitude": -0.876543,
    "altitude": 28.5,
    "speed": 16.2,
    "battery_level": 85.7,
    "heading": 135.0,
    "status": "active"
}

# 2. Convert to JSON (encryption.py:65)
json_data = '{"timestamp": 1762474300.123, "latitude": 51.234567, ...}'

# 3. Encrypt with Fernet (encryption.py:66)
encrypted = Fernet.encrypt(json_data.encode())
# Result: b'gAAAAABl3xZ7c9f2a1b4e6d8c0f3a5e7b9d1c3e5f7...'

# 4. Send (drone_simulator.py:202)
await websocket.send(encrypted)
```

**Network transmission** (encrypted bytes)

**API side:**
```python
# 5. Receive (dashboard.py:98)
encrypted_data = await websocket.receive_bytes()
# encrypted_data = b'gAAAAABl3xZ7c9f2a1b4e6d8c0f3a5e7b9d1c3e5f7...'

# 6. Decrypt (encryption.py:78-79)
decrypted = Fernet.decrypt(encrypted_data)
# Result: b'{"timestamp": 1762474300.123, "latitude": 51.234567, ...}'

# 7. Parse JSON (encryption.py:80)
telemetry = json.loads(decrypted.decode())
# Back to dict: {"timestamp": 1762474300.123, ...}

# 8. Broadcast to web clients (dashboard.py:110)
for client in client_connections:
    await client.send_json(telemetry)
```

**Web browser:**
```javascript
// 9. Receive (index.html:364)
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    // data = {"timestamp": 1762474300.123, "latitude": 51.234567, ...}

    // 10. Update UI (index.html:395-396)
    document.getElementById('latitude').textContent = data.latitude.toFixed(6);
    // Display: "51.234567"
};
```

**Total time:** ~100-200ms from drone to browser update!

---

## Learning Exercises

### Exercise 1: Understanding Authentication

**Question:** What would happen if we removed the timestamp from authentication tokens?

<details>
<summary>Click for answer</summary>

**Answer:** The system would be vulnerable to replay attacks!

**Attack scenario:**
1. Attacker captures a valid token on Monday
2. On Friday, attacker replays the same token
3. Without timestamp check, the signature is still valid
4. Attacker gains unauthorized access

**Prevention:** Timestamps ensure tokens expire, making captured tokens useless after 30 seconds.
</details>

### Exercise 2: Encryption Strength

**Question:** How long would it take to brute-force our AES-128 encryption key?

<details>
<summary>Click for answer</summary>

**Answer:** Essentially forever with current technology.

**Math:**
- AES-128 has 2^128 possible keys
- That's 340,282,366,920,938,463,463,374,607,431,768,211,456 possibilities
- If you could try 1 trillion keys per second
- It would take 10,790,283,070,806,014,188 years
- The universe is only 13.8 billion years old!

**Practical takeaway:** AES-128 is considered unbreakable by brute force.
</details>

### Exercise 3: WebSocket vs HTTP Polling

**Question:** If we used HTTP polling instead of WebSockets, how much more overhead would we have?

<details>
<summary>Click for answer</summary>

**Answer:** Significant overhead!

**HTTP Polling** (1 request per second):
- TCP connection setup: 3-way handshake
- TLS handshake: 2-4 round trips
- HTTP headers: ~500 bytes per request
- Total per minute: 60 connections × 500 bytes = 30 KB overhead

**WebSocket** (1 connection):
- Initial handshake once
- Minimal framing: ~2-6 bytes per message
- Total per minute: 60 messages × 6 bytes = 360 bytes overhead

**Savings:** ~98.8% reduction in overhead!
</details>

### Exercise 4: Modifying the Code

**Challenge:** Modify the drone to send telemetry every 2 seconds instead of every 1 second.

<details>
<summary>Click for hint</summary>

**Hint:** Look in `drone_simulator.py` at the main loop. Find the `asyncio.sleep()` call.
</details>

<details>
<summary>Click for answer</summary>

**Answer:** Change line 213 in `drone_simulator.py`:

```python
# Before
await asyncio.sleep(1.0)

# After
await asyncio.sleep(2.0)
```

**Effect:** Updates will happen half as often, reducing network traffic but making the dashboard update less frequently.
</details>

### Exercise 5: Security Analysis

**Question:** Is it safe to have the web dashboard connect without authentication?

<details>
<summary>Click for answer</summary>

**Answer:** It depends on the threat model!

**Current design:**
- Web clients just view data (read-only)
- They can't send commands to the drone
- They don't have the encryption/auth keys

**Safe for:** Demonstrations, internal networks, when you want anyone to view the dashboard

**Not safe for:** Sensitive operations where viewing telemetry data itself is restricted

**To secure:** Add authentication to `/ws/client` endpoint using sessions, JWT tokens, or OAuth.
</details>

### Exercise 6: Challenge-Response Protocol

**Question:** Why do we include the identity ("drone") in the challenge response?

<details>
<summary>Click for answer</summary>

**Answer:** To bind the response to a specific identity!

**Without identity:**
```python
response = HMAC(key, challenge)
```
- Any entity with the key could respond
- Can't distinguish between drone, API, or other authorized devices

**With identity:**
```python
response = HMAC(key, challenge + "drone")
```
- Response is specific to "drone" identity
- Even with the same key, "drone" and "api" produce different responses
- Prevents identity confusion attacks

**Example attack prevented:**
1. Attacker captures API's response to a challenge
2. Tries to replay it when connecting as "drone"
3. Fails because response includes identity binding
</details>

### Exercise 7: Thinking About Improvements

**Question:** How would you modify the system to support multiple drones simultaneously?

<details>
<summary>Click for hint</summary>

**Hints:**
1. Each drone needs a unique identifier
2. Change `drone_connection` from single to multiple
3. Modify authentication to include drone ID
4. Update dashboard to show multiple drones
</details>

<details>
<summary>Click for detailed answer</summary>

**Changes needed:**

**1. Give each drone a unique ID:**
```python
# drone_simulator.py
def __init__(self, drone_id: str):
    self.drone_id = drone_id  # e.g., "drone_001"
```

**2. Include ID in authentication:**
```python
# encryption.py
identity = f"drone:{self.drone_id}"  # e.g., "drone:drone_001"
token = self.encryption.generate_auth_token(identity)
```

**3. Track multiple drones:**
```python
# dashboard.py
drone_connections: dict[str, WebSocket] = {}  # ID → WebSocket

# In drone_websocket():
drone_id = extract_id_from_token(drone_auth_token)
drone_connections[drone_id] = websocket
```

**4. Update dashboard UI:**
```html
<!-- Show list of drones -->
<div id="droneList">
  <div class="drone-card" id="drone_001">...</div>
  <div class="drone-card" id="drone_002">...</div>
</div>
```

**Result:** Multiple drones can connect simultaneously, each with its own authenticated connection and display!
</details>

---

## Conclusion

Congratulations! You now understand:

✅ **Authentication** - How HMAC-SHA256 verifies identity
✅ **Encryption** - How Fernet/AES-128 protects data
✅ **WebSockets** - How real-time bidirectional communication works
✅ **Async Programming** - How Python handles concurrent connections
✅ **Security** - Why timestamps, constant-time comparison, and key separation matter

### Next Steps

**To deepen your understanding:**

1. **Read the actual code** - Follow along with this guide while reading each file
2. **Make modifications** - Try the challenges in the exercises section
3. **Break things** - Remove security features and see what attacks become possible
4. **Extend it** - Add features like multiple drones, logging, or 3D visualization

### Further Reading

**Authentication & Cryptography:**
- HMAC RFC: https://tools.ietf.org/html/rfc2104
- Fernet Specification: https://github.com/fernet/spec
- NIST Cryptographic Standards: https://csrc.nist.gov/

**WebSockets:**
- RFC 6455: https://tools.ietf.org/html/rfc6455
- MDN WebSocket API: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket

**Python Async:**
- Python asyncio docs: https://docs.python.org/3/library/asyncio.html
- Real Python asyncio tutorial: https://realpython.com/async-io-python/

---

**Remember:** Security is not about making attacks impossible, but about making them impractically difficult. Every layer of defense increases the effort required, making your system safer!

Happy learning! 🚀
