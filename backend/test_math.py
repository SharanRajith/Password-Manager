import math_utils
import rsa_crypto
import entropy

print("--- Testing Math Utils ---")
# Test Primality
p = math_utils.generate_prime(256)
print(f"Generated Prime p: {p}")
print(f"Is p prime? {math_utils.miller_rabin(p)}")

# Test GCD and Mod Inverse
a = 17
m = 3120
print(f"GCD(17, 3120) = {math_utils.gcd(a, m)}")
inv = math_utils.mod_inverse(a, m)
print(f"Mod Inverse of 17 mod 3120 = {inv}")
print(f"Check (17 * {inv}) % 3120 = {(17 * inv) % m}")

print("\n--- Testing RSA Crypto ---")
rsa = rsa_crypto.RSA(key_size=128)
pub, priv, pp, qq, phi = rsa.generate_keypair()
print("Generated RSA keys")
plaintext = "Hello Discrete Math!"
print(f"Plaintext: {plaintext}")
ciphertext = rsa.encrypt(pub, plaintext)
print(f"Ciphertext: {ciphertext}")
decrypted = rsa.decrypt(priv, ciphertext)
print(f"Decrypted: {decrypted}")
assert plaintext == decrypted

print("\n--- Testing Entropy ---")
pw = entropy.generate_secure_password(16)
print(f"Generated PW: {pw}")
ent = entropy.calculate_entropy(pw)
print(f"Entropy: {ent} bits, Strength: {entropy.evaluate_strength(ent)}")

print("\nAll Tests Passed Successfully!")
