import os
import rsa 
from dotenv import load_dotenv

load_dotenv(override=True)

PUBLIC_KEY_FILE = os.environ.get("PAYMENTS_SERVICE_PUBLIC_KEY")

public_key=None

if os.path.exists(PUBLIC_KEY_FILE):
    with open(PUBLIC_KEY_FILE, "rb") as pub_file:
        public_key = rsa.PublicKey.load_pkcs1(pub_file.read())

def verify_signature(value, sig):
    if public_key:
        try:
            rsa.verify(value.encode(), sig, public_key)
            return True
        except rsa.VerificationError:
            return False
    else:
        raise FileNotFoundError(f"Public key file not found: {PUBLIC_KEY_FILE}")
    
