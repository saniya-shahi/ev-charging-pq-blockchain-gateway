import base64

KEY = "lightweightkey"

def encrypt(data):
    encrypted = "".join(chr(ord(c) ^ ord(KEY[i % len(KEY)])) for i, c in enumerate(data))
    return base64.b64encode(encrypted.encode()).decode()

def decrypt(data):
    decoded = base64.b64decode(data).decode()
    decrypted = "".join(chr(ord(c) ^ ord(KEY[i % len(KEY)])) for i, c in enumerate(decoded))
    return decrypted