import random

def gcd(a: int, b: int) -> int:
    """
    Euclidean algorithm to find the greatest common divisor.
    Discrete Math Concept: Number Theory
    """
    while b:
        a, b = b, a % b
    return a

def extended_gcd(a: int, b: int):
    """
    Extended Euclidean Algorithm.
    Returns (g, x, y) such that a*x + b*y = g = gcd(a, b).
    Discrete Math Concept: Diophantine Equations / Modular Inverse
    """
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = extended_gcd(b % a, a)
        return (g, x - (b // a) * y, y)

def mod_inverse(a: int, m: int) -> int:
    """
    Modular multiplicative inverse.
    Returns x such that (a * x) % m == 1.
    """
    g, x, y = extended_gcd(a, m)
    if g != 1:
        raise Exception('Modular inverse does not exist')
    else:
        return x % m

def fast_power(base: int, exp: int, mod: int) -> int:
    """
    Fast modular exponentiation: (base^exp) % mod.
    Discrete Math Concept: Modular Exponentiation
    """
    res = 1
    base = base % mod
    while exp > 0:
        if (exp % 2) == 1:
            res = (res * base) % mod
        exp = exp >> 1
        base = (base * base) % mod
    return res

def miller_rabin(n: int, k: int = 5) -> bool:
    """
    Miller-Rabin primality test.
    Returns True if n is probably prime.
    Discrete Math Concept: Probabilistic Primality Testing
    """
    if n == 2 or n == 3:
        return True
    if n <= 1 or n % 2 == 0:
        return False
    
    # Write n - 1 as 2^r * d
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
        
    for _ in range(k):
        a = random.randrange(2, n - 2)
        x = fast_power(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = fast_power(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def generate_prime(bits: int = 512) -> int:
    """
    Generates a prime number with a specified number of bits.
    Uses Miller-Rabin test to verify primality.
    """
    while True:
        p = random.getrandbits(bits)
        # Ensure it's odd and has the correct bit length
        p |= (1 << bits - 1) | 1
        if miller_rabin(p):
            return p
