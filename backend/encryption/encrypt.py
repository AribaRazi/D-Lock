# from cryptography.fernet import Fernet

# # Generate only once — keep the key safe
# KEY = Fernet.generate_key()
# cipher = Fernet(KEY)

# def encrypt_file(file_bytes: bytes) -> bytes:
#     return cipher.encrypt(file_bytes)

# def decrypt_file(encrypted_bytes: bytes) -> bytes:
#     return cipher.decrypt(encrypted_bytes)


# from cryptography.fernet import Fernet
# import base64

# def encrypt_file(file_data):
#     """Encrypt file and return both encrypted data and the key"""
#     # Generate a unique key for this file
#     key = Fernet.generate_key()
#     fernet = Fernet(key)
#     encrypted_data = fernet.encrypt(file_data)
    
#     # Return both encrypted data and the key (user needs this to decrypt!)
#     return encrypted_data, key.decode('utf-8')

# def decrypt_file(encrypted_data, decryption_key):
#     """Decrypt file using the provided key"""
#     try:
#         fernet = Fernet(decryption_key.encode('utf-8'))
#         decrypted_data = fernet.decrypt(encrypted_data)
#         return decrypted_data
#     except Exception as e:
#         raise ValueError("Invalid decryption key")

"""
AES-256 encryption/decryption module with proper error handling
"""
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os


def encrypt_file(file_data: bytes) -> tuple[bytes, str]:
    """
    Encrypt file data using AES-256-CBC
    
    Args:
        file_data: Raw file bytes to encrypt
    
    Returns:
        tuple: (encrypted_data, decryption_key_hex)
    """
    # Generate random 256-bit key (32 bytes)
    key = os.urandom(32)
    
    # Generate random 128-bit IV (16 bytes)
    iv = os.urandom(16)
    
    # Pad the data to be a multiple of block size (128 bits = 16 bytes)
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(file_data) + padder.finalize()
    
    # Encrypt using AES-256-CBC
    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
        backend=default_backend()
    )
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    
    # Combine IV + encrypted data (IV needs to be stored with ciphertext)
    final_data = iv + encrypted_data
    
    # Return encrypted data and key as hex string
    return final_data, key.hex()


def decrypt_file(encrypted_data: bytes, decryption_key_hex: str) -> bytes:
    """
    Decrypt file data using AES-256-CBC
    
    Args:
        encrypted_data: Encrypted file bytes (IV + ciphertext)
        decryption_key_hex: Hex string of the decryption key
    
    Returns:
        bytes: Decrypted file data
    
    Raises:
        ValueError: If decryption key is invalid or decryption fails
    """
    try:
        # Convert hex key back to bytes
        key = bytes.fromhex(decryption_key_hex)
        
        # Validate key length (must be 32 bytes for AES-256)
        if len(key) != 32:
            raise ValueError("Invalid key length. Expected 32 bytes (64 hex characters).")
        
        # Extract IV (first 16 bytes) and ciphertext (rest)
        if len(encrypted_data) < 16:
            raise ValueError("Encrypted data is too short to contain IV")
        
        iv = encrypted_data[:16]
        ciphertext = encrypted_data[16:]
        
        # Decrypt using AES-256-CBC
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Remove padding
        unpadder = padding.PKCS7(128).unpadder()
        file_data = unpadder.update(padded_data) + unpadder.finalize()
        
        return file_data
    
    except ValueError as e:
        # Re-raise ValueError with clear message
        print(f"Decryption ValueError: {e}")
        raise ValueError(f"Invalid decryption key: {str(e)}")
    
    except Exception as e:
        # Catch any other errors (wrong key causes padding errors)
        print(f"Decryption failed: {e}")
        raise ValueError("Invalid decryption key or corrupted data")


# Test function to verify encryption/decryption works
def test_encryption():
    """Test encryption and decryption"""
    test_data = b"Hello, this is a test file!"
    
    # Encrypt
    encrypted, key = encrypt_file(test_data)
    print(f"✅ Encryption successful")
    print(f"   Key: {key}")
    print(f"   Encrypted size: {len(encrypted)} bytes")
    
    # Decrypt with correct key
    try:
        decrypted = decrypt_file(encrypted, key)
        assert decrypted == test_data
        print(f"✅ Decryption with correct key successful")
    except Exception as e:
        print(f"❌ Decryption failed: {e}")
    
    # Try decrypt with wrong key
    wrong_key = "0" * 64  # 64 hex chars = 32 bytes
    try:
        decrypt_file(encrypted, wrong_key)
        print(f"❌ ERROR: Wrong key should have failed!")
    except ValueError as e:
        print(f"✅ Wrong key correctly rejected: {e}")


if __name__ == "__main__":
    test_encryption()