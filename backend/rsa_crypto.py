import math_utils
import os
import hashlib
import json
import base64

class RSA:
    def __init__(self, key_size=256):
        # We use a smaller default size here for speed in demonstration,
        # but in a real app this should be 1024 or 2048.
        self.key_size = key_size
        
    def generate_keypair(self):
        """
        Generates an RSA keypair.
        Discrete Math Concept: Euler's Totient function and Prime Numbers
        Returns: ((e, n), (d, n), p, q, phi)
        """
        p = math_utils.generate_prime(self.key_size)
        q = math_utils.generate_prime(self.key_size)
        
        # Ensure p != q
        while p == q:
            q = math_utils.generate_prime(self.key_size)
            
        n = p * q
        phi = (p - 1) * (q - 1)
        
        # Choose e such that 1 < e < phi and gcd(e, phi) = 1
        e = 65537
        if math_utils.gcd(e, phi) != 1:
            e = 3
            while math_utils.gcd(e, phi) != 1:
                e += 2
                
        d = math_utils.mod_inverse(e, phi)
        
        # Returning extra mathematical parameters just for educational visualization
        return ((e, n), (d, n), p, q, phi)
        
    def encrypt(self, public_key, plaintext):
        """
        Encrypts a string using the public key.
        Discrete Math Concept: Modular Exponentiation c = m^e (mod n)
        """
        e, n = public_key
        
        # In actual RSA we'd use padding (like PKCS#1 OAEP).
        # For pure discrete math demonstration, we'll map characters to ints
        # or encrypt chunks. Let's do it per character for simplicity in visualization.
        cipher = [math_utils.fast_power(ord(char), e, n) for char in plaintext]
        
        # Convert list of ints to a string for easy storage (comma separated)
        return json.dumps(cipher)
        
    def decrypt(self, private_key, ciphertext):
        """
        Decrypts a list of integers using the private key.
        Discrete Math Concept: Modular Exponentiation m = c^d (mod n)
        """
        d, n = private_key
        
        try:
            cipher_ints = json.loads(ciphertext)
            plain = [chr(math_utils.fast_power(char_c, d, n)) for char_c in cipher_ints]
            return ''.join(plain)
        except Exception as e:
            print(f"Decryption error: {e}")
            return ""

def hash_password(password: str, salt: str = None) -> tuple:
    """
    Hashes a password using SHA-256 and a random salt.
    Discrete Math Concept: Cryptographic Hash Functions (One-way mapping)
    """
    if salt is None:
        salt = os.urandom(16).hex()
    salted_password = password + salt
    hashed = hashlib.sha256(salted_password.encode()).hexdigest()
    return hashed, salt
    
def verify_password(password: str, hashed: str, salt: str) -> bool:
    """Verifies a given password against a hash and salt."""
    return hash_password(password, salt)[0] == hashed
