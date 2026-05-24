from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import rsa_crypto
import entropy
import json
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

VAULT_FILE = "vault.json"

class SetupRequest(BaseModel):
    master_password: str

class LoginRequest(BaseModel):
    master_password: str

class PasswordEntry(BaseModel):
    site: str
    username: str
    password: str

class GenerateRequest(BaseModel):
    length: int = 16
    use_upper: bool = True
    use_lower: bool = True
    use_digits: bool = True
    use_special: bool = True

def load_vault():
    if os.path.exists(VAULT_FILE):
        with open(VAULT_FILE, "r") as f:
            return json.load(f)
    return None

def save_vault(data):
    with open(VAULT_FILE, "w") as f:
        json.dump(data, f)

@app.post("/setup")
def setup(req: SetupRequest):
    vault = load_vault()
    if vault is not None:
        raise HTTPException(status_code=400, detail="Already setup")
    
    # Hash master password (Discrete Math: Cryptographic Hashing)
    hashed, salt = rsa_crypto.hash_password(req.master_password)
    
    # Generate RSA keys (Discrete Math: Number Theory)
    rsa = rsa_crypto.RSA(key_size=256) # 256 for fast demonstration
    pub, priv, p, q, phi = rsa.generate_keypair()
    
    vault_data = {
        "master_hash": hashed,
        "salt": salt,
        "public_key": pub,
        "private_key": priv,
        "math_params": {"p": p, "q": q, "phi": phi},
        "entries": []
    }
    save_vault(vault_data)
    return {"message": "Setup successful", "math_params": vault_data["math_params"], "public_key": pub, "private_key": priv}

@app.post("/login")
def login(req: LoginRequest):
    vault = load_vault()
    if vault is None:
        raise HTTPException(status_code=400, detail="Not setup yet")
        
    if not rsa_crypto.verify_password(req.master_password, vault["master_hash"], vault["salt"]):
        raise HTTPException(status_code=401, detail="Invalid master password")
        
    return {
        "message": "Login successful",
        "public_key": vault["public_key"],
        "math_params": vault["math_params"]
    }

@app.get("/vault")
def get_vault():
    vault = load_vault()
    if vault is None:
        raise HTTPException(status_code=400, detail="Not setup yet")
        
    # Return encrypted entries, and decrypt them for the frontend
    rsa = rsa_crypto.RSA()
    decrypted_entries = []
    
    for entry in vault["entries"]:
        decrypted_pw = rsa.decrypt(vault["private_key"], entry["encrypted_password"])
        decrypted_entries.append({
            "site": entry["site"],
            "username": entry["username"],
            "encrypted_password": entry["encrypted_password"],
            "decrypted_password": decrypted_pw
        })
        
    return {"entries": decrypted_entries}

@app.post("/vault")
def add_password(req: PasswordEntry):
    vault = load_vault()
    if vault is None:
        raise HTTPException(status_code=400, detail="Not setup yet")
        
    rsa = rsa_crypto.RSA()
    encrypted_pw = rsa.encrypt(vault["public_key"], req.password)
    
    vault["entries"].append({
        "site": req.site,
        "username": req.username,
        "encrypted_password": encrypted_pw
    })
    
    save_vault(vault)
    return {"message": "Password added successfully", "encrypted": encrypted_pw}

@app.post("/generate")
def generate(req: GenerateRequest):
    try:
        pw = entropy.generate_secure_password(req.length, req.use_upper, req.use_lower, req.use_digits, req.use_special)
        ent = entropy.calculate_entropy(pw)
        strength = entropy.evaluate_strength(ent)
        return {"password": pw, "entropy": ent, "strength": strength}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/reset")
def reset_vault():
    """Endpoint purely for testing to start fresh."""
    if os.path.exists(VAULT_FILE):
        os.remove(VAULT_FILE)
    return {"message": "Vault reset"}

# Mount the frontend directory to serve the static UI files
frontend_path = os.path.join(os.path.dirname(__file__), "../frontend")
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")
