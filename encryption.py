"""
Encryption module for secure telemetry data transmission.
Uses Fernet symmetric encryption from the cryptography library.
Includes mutual authentication between drone and API.
"""

from cryptography.fernet import Fernet
import json
import os
import secrets
import hmac
import hashlib
import time


class SecureTransmission:
    """Handles encryption, decryption, and mutual authentication."""

    def __init__(self, key_file="secret.key", auth_file="auth.key"):
        """
        Initialize the encryption and authentication handler.

        Args:
            key_file: Path to the encryption key file
            auth_file: Path to the authentication key file
        """
        self.key_file = key_file
        self.auth_file = auth_file
        self.key = self._load_or_generate_key()
        self.auth_key = self._load_or_generate_auth_key()
        self.cipher = Fernet(self.key)

    def _load_or_generate_key(self):
        """Load existing encryption key or generate a new one."""
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            return key

    def _load_or_generate_auth_key(self):
        """Load existing authentication key or generate a new one."""
        if os.path.exists(self.auth_file):
            with open(self.auth_file, 'rb') as f:
                return f.read()
        else:
            # Generate a 256-bit random authentication key
            auth_key = secrets.token_bytes(32)
            with open(self.auth_file, 'wb') as f:
                f.write(auth_key)
            return auth_key

    def encrypt_data(self, data: dict) -> bytes:
        """
        Encrypt telemetry data.

        Args:
            data: Dictionary containing telemetry data

        Returns:
            Encrypted data as bytes
        """
        json_data = json.dumps(data)
        encrypted = self.cipher.encrypt(json_data.encode())
        return encrypted

    def decrypt_data(self, encrypted_data: bytes) -> dict:
        """
        Decrypt telemetry data.

        Args:
            encrypted_data: Encrypted data as bytes

        Returns:
            Decrypted data as dictionary
        """
        decrypted = self.cipher.decrypt(encrypted_data)
        return json.loads(decrypted.decode())

    def encrypt_command(self, command: str) -> bytes:
        """
        Encrypt control commands.

        Args:
            command: Command string (e.g., 'up', 'down', 'left', 'right')

        Returns:
            Encrypted command as bytes
        """
        return self.cipher.encrypt(command.encode())

    def decrypt_command(self, encrypted_command: bytes) -> str:
        """
        Decrypt control commands.

        Args:
            encrypted_command: Encrypted command as bytes

        Returns:
            Decrypted command string
        """
        return self.cipher.decrypt(encrypted_command).decode()

    # ===== Authentication Methods =====

    def generate_auth_token(self, identity: str) -> str:
        """
        Generate an authentication token for initial connection.

        Args:
            identity: Identity string (e.g., 'drone', 'api')

        Returns:
            Authentication token as hex string
        """
        timestamp = str(int(time.time())).encode()
        message = identity.encode() + b':' + timestamp
        signature = hmac.new(self.auth_key, message, hashlib.sha256).digest()
        # Use pipe separator to avoid conflicts with colon in message
        token = message.hex() + '|' + signature.hex()
        return token

    def verify_auth_token(self, token: str, expected_identity: str, timeout: int = 30) -> bool:
        """
        Verify an authentication token.

        Args:
            token: Authentication token to verify
            expected_identity: Expected identity string
            timeout: Maximum age of token in seconds

        Returns:
            True if token is valid, False otherwise
        """
        try:
            # Split by pipe separator
            parts = token.split('|')
            if len(parts) != 2:
                return False

            message_hex = parts[0]
            signature_hex = parts[1]

            message = bytes.fromhex(message_hex)
            received_signature = bytes.fromhex(signature_hex)

            # Verify signature
            expected_signature = hmac.new(self.auth_key, message, hashlib.sha256).digest()
            if not hmac.compare_digest(received_signature, expected_signature):
                return False

            # Parse message (identity:timestamp)
            message_str = message.decode()
            identity, timestamp_str = message_str.split(':')

            # Verify identity
            if identity != expected_identity:
                return False

            # Verify timestamp (prevent replay attacks)
            timestamp = int(timestamp_str)
            current_time = int(time.time())
            if abs(current_time - timestamp) > timeout:
                return False

            return True

        except Exception:
            return False

    def generate_challenge(self) -> str:
        """
        Generate a random challenge for mutual authentication.

        Returns:
            Challenge string (hex encoded random bytes)
        """
        challenge = secrets.token_bytes(32)
        return challenge.hex()

    def generate_challenge_response(self, challenge: str, identity: str) -> str:
        """
        Generate a response to an authentication challenge.

        Args:
            challenge: Challenge string received
            identity: Identity of the responder

        Returns:
            Challenge response as hex string
        """
        challenge_bytes = bytes.fromhex(challenge)
        message = challenge_bytes + identity.encode()
        response = hmac.new(self.auth_key, message, hashlib.sha256).digest()
        return response.hex()

    def verify_challenge_response(self, challenge: str, response: str, expected_identity: str) -> bool:
        """
        Verify a challenge response.

        Args:
            challenge: Original challenge that was sent
            response: Response received
            expected_identity: Expected identity of responder

        Returns:
            True if response is valid, False otherwise
        """
        try:
            expected_response = self.generate_challenge_response(challenge, expected_identity)
            return hmac.compare_digest(response, expected_response)
        except Exception:
            return False
