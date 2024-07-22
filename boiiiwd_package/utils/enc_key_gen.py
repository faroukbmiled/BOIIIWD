import os
import base64

def generate_key():
    key = os.urandom(32)
    print(f"Generated AES key: {base64.b64encode(key).decode('utf-8')}")


if __name__ == "__main__":
    generate_key()
