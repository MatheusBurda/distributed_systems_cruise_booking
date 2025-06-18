import os
import rsa 
from dotenv import load_dotenv

load_dotenv(override=True)

PRIVATE_KEY_FILE = os.environ.get("PAYMENTS_SERVICE_PRIVATE_KEY")

private_key=None

if os.path.exists(PRIVATE_KEY_FILE):
    with open(PRIVATE_KEY_FILE, "rb") as priv_file:
        private_key = rsa.PrivateKey.load_pkcs1(priv_file.read())
    
def signature(value):
    if private_key:
        return rsa.sign(value.encode(), private_key, "SHA-256")
    else:
        raise FileNotFoundError(f"Private key file not found: {PRIVATE_KEY_FILE}")