from cryptography.fernet import Fernet

class Encryption:
    def __init__(self, key: str):
        self.fernet = Fernet(key.encode())

    def encrypt(self, message: str) -> str:
        return self.fernet.encrypt(message.encode()).decode()

    def decrypt(self, token: str) -> str:
        return self.fernet.decrypt(token.encode()).decode()