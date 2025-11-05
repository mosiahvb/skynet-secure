"""
Encryption module for secure telemetry data transmission.
Uses Fernet symmetric encryption from the cryptography library.
"""

from cryptography.fernet import Fernet
import json
import os


class SecureTransmission:
    """Handles encryption and decryption of telemetry data."""

    def __init__(self, key_file="secret.key"):
        """
        Initialize the encryption handler.

        Args:
            key_file: Path to the encryption key file
        """
        self.key_file = key_file
        self.key = self._load_or_generate_key()
        self.cipher = Fernet(self.key)

    def _load_or_generate_key(self):
        """Load existing key or generate a new one."""
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            return key

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
