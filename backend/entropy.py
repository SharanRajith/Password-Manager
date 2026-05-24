import string
import random
import math

def calculate_entropy(password: str) -> float:
    """
    Calculates the Shannon entropy (in bits) of a given password.
    Discrete Math Concept: Combinatorics and Information Theory
    Formula: E = L * log2(R) where L is length, R is size of the pool of characters used.
    """
    pool_size = 0
    if any(c.islower() for c in password): pool_size += 26
    if any(c.isupper() for c in password): pool_size += 26
    if any(c.isdigit() for c in password): pool_size += 10
    if any(c in string.punctuation for c in password): pool_size += len(string.punctuation)
    
    if pool_size == 0:
        return 0.0
        
    length = len(password)
    # Combinatorial possible combinations = pool_size ^ length
    # Entropy = log2(pool_size ^ length) = length * log2(pool_size)
    entropy = length * math.log2(pool_size)
    return round(entropy, 2)

def evaluate_strength(entropy: float) -> str:
    """
    Uses simple logic (thresholds) to evaluate strength.
    """
    if entropy < 40: return "Weak"
    if entropy < 60: return "Fair"
    if entropy < 80: return "Good"
    return "Excellent"

def generate_secure_password(length: int = 16, use_upper=True, use_lower=True, use_digits=True, use_special=True) -> str:
    """
    Generates a secure password using combinatorial selection.
    Discrete Math Concept: Set Theory, Combinations, Permutations
    """
    pool = ""
    requirements = []
    
    if use_upper:
        pool += string.ascii_uppercase
        requirements.append(string.ascii_uppercase)
    if use_lower:
        pool += string.ascii_lowercase
        requirements.append(string.ascii_lowercase)
    if use_digits:
        pool += string.digits
        requirements.append(string.digits)
    if use_special:
        pool += string.punctuation
        requirements.append(string.punctuation)
        
    if not pool or length < len(requirements):
        raise ValueError("Invalid parameters for password generation.")
        
    # Ensure at least one character from each required set is chosen
    password = [random.choice(req_set) for req_set in requirements]
    
    # Fill the rest with random choices from the combined pool
    password += [random.choice(pool) for _ in range(length - len(requirements))]
    
    # Shuffle to remove predictable patterns (Permutations)
    random.shuffle(password)
    
    return "".join(password)
