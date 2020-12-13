from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import base64
import re

class EncryptionManager:
    def __init__(self):
        key = os.urandom(32)
        nonce = os.urandom(16)
        aes_context = Cipher(algorithms.AES(key), modes.CTR(nonce), backend=default_backend())
        self.encryptor = aes_context.encryptor()
        self.decryptor = aes_context.decryptor()
        self.counter = base64.b64encode(os.urandom(16))

    def updateEncryptor(self, plaintext):
        plainbytes = plaintext.encode()
        secret = self.counter + plainbytes
        encrypted_text = base64.b64encode(self.encryptor.update(secret)).decode()
        return encrypted_text

    def finalizeEncryptor(self):
        return self.encryptor.finalize()

    def updateDecryptor(self, ciphertext):
        cipherbytes = base64.b64decode(ciphertext.encode())
        secret = self.decryptor.update(cipherbytes)
        secret_str = secret.decode()
        plaintext = secret_str[len(self.counter.decode()):]
        return plaintext

    def finalizeDecryptor(self):
        return self.decryptor.finalize()

#manager = EncryptionManager()

#plaintexts = [
#        "3asdasdx"
#        ]

#ciphertexts = []

#for m in plaintexts:
#    c = manager.updateEncryptor(m)
#    print(c)
#    ciphertexts.append(c)
#manager.finalizeEncryptor()

#for c in ciphertexts:
#    print("recovered", manager.updateDecryptor(c))
#manager.finalizeDecryptor()
