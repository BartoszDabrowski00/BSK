from Crypto.Cipher import AES
from Crypto.Cipher.AES import MODE_CBC, MODE_ECB
from Crypto.Util.Padding import pad, unpad


IV_SIZE_BYTES = 16


class Encryptions:

    def __init__(self):
        pass

    @staticmethod
    def encrypt_message(key: bytes, mode: int, message: bytes) -> bytes:
        if mode == MODE_CBC:
            return Encryptions.encrypt_cbc_message(key, mode, message)
        elif mode == MODE_ECB:
            return Encryptions.encrypt_ecb_message(key, mode, message)

    @staticmethod
    def encrypt_ecb_message(key: bytes, mode: int, message: bytes):
        return AES.new(key, mode).encrypt(pad(message, AES.block_size))

    @staticmethod
    def encrypt_cbc_message(key: bytes, mode: int, message: bytes):
        cipher = AES.new(key, mode)
        iv = cipher.iv
        encrypted_message = cipher.encrypt(pad(message, AES.block_size))
        return b''.join([iv, encrypted_message])

    @staticmethod
    def decrypt_message(key: bytes, mode: int, message: bytes) -> bytes:
        if mode == MODE_CBC:
            return Encryptions.decrypt_cbc_message(key, mode, message)
        elif mode == MODE_ECB:
            return Encryptions.decrypt_ecb_message(key, mode, message)

    @staticmethod
    def decrypt_cbc_message(key: bytes, mode: int, message: bytes):
        iv = message[:IV_SIZE_BYTES]
        encrypted_message = message[IV_SIZE_BYTES:]
        cipher = AES.new(key, mode, iv=iv)
        return unpad(cipher.decrypt(encrypted_message), AES.block_size)

    @staticmethod
    def decrypt_ecb_message(key: bytes, mode: int, message: bytes):
        return unpad(AES.new(key, mode).decrypt(message), AES.block_size)
