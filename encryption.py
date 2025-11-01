# encryption.py - Handles all encryption and decryption

from cryptography.fernet import Fernet
import base64
import hashlib
from config import ENCRYPTION_KEY

class SecureChannel:
    """
    This class handles encryption and decryption of telemetry data.
    
    Think of it like a secret code machine:
    - encrypt() turns normal text into scrambled gibberish
    - decrypt() turns gibberish back into normal text
    """
    
    def __init__(self, key):
        """
        Initialize the encryption machine with a secret key.
        
        Args:
            key: Your secret password (as bytes)
        """
        # Convert the key to the right format for Fernet encryption
        # SHA-256 creates a 32-byte hash from any input
        key_bytes = hashlib.sha256(key).digest()
        # Base64 encode it (Fernet requires this format)
        key_base64 = base64.urlsafe_b64encode(key_bytes)
        # Create the cipher object (our encryption machine)
        self.cipher = Fernet(key_base64)
    
    def encrypt(self, data):
        """
        Encrypt data (scramble it into secret code).
        
        Args:
            data: String or bytes to encrypt
            
        Returns:
            Encrypted bytes (gibberish that only we can decrypt)
        """
        # If data is a string, convert it to bytes first
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Encrypt the data
        encrypted = self.cipher.encrypt(data)
        return encrypted
    
    def decrypt(self, encrypted_data):
        """
        Decrypt data (unscramble the secret code back to normal).
        
        Args:
            encrypted_data: Encrypted bytes to decrypt
            
        Returns:
            Decrypted string (original readable text)
        """
        # Decrypt the data
        decrypted = self.cipher.decrypt(encrypted_data)
        # Convert bytes back to string
        return decrypted.decode('utf-8')

# Test function to make sure encryption works
if __name__ == "__main__":
    print("Testing encryption...")
    
    # Create a secure channel
    channel = SecureChannel(ENCRYPTION_KEY)
    
    # Test message
    original = "Battery: 85%, Altitude: 100m"
    print(f"Original message: {original}")
    
    # Encrypt it
    encrypted = channel.encrypt(original)
    print(f"Encrypted (scrambled): {encrypted}")
    
    # Decrypt it back
    decrypted = channel.decrypt(encrypted)
    print(f"Decrypted (unscrambled): {decrypted}")
    
    # Check if it matches
    if original == decrypted:
        print("✓ Encryption working perfectly!")
    else:
        print("✗ Something went wrong!")
