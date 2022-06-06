import os
import json
import logging
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256
from base64 import b64encode, b64decode
from Crypto.Util.Padding import pad, unpad

log = logging.getLogger(__name__)


def hash_password(password: str) -> bytes:
    h = SHA256.new()
    h.update(str.encode(password))
    return h.digest()


class SecurityKeysHandler:
    PRIVATE_KEY_PATH_SUFFIX = "private"
    PUBLIC_KEY_PATH_SUFFIX = "public"

    def __init__(self):
        self.private_key = None
        self.public_key = None
        self.session_keys = None

    def generate_session_key(self,) -> bool:
        if self.public_key is None or self.private_key is None:
            log.warning('In order to generate session key, load rsa keys')

        #session_key = get_random_bytes(16)
        return True

    def generate_rsa_keys(self) -> None:
        key = RSA.generate(2048)
        self.public_key = key.public_key().exportKey()
        self.private_key = key.exportKey()
        log.info('Client generated new rsa keys.')

    def load_rsa_keys(self, path: str, password: str) -> None:
        public_path = os.path.join(path, self.PUBLIC_KEY_PATH_SUFFIX, 'key.json')
        private_path = os.path.join(path, self.PRIVATE_KEY_PATH_SUFFIX, 'key.json')
        keys_exist = os.path.isfile(public_path) and os.path.isfile(private_path)

        if not keys_exist:
            self.generate_rsa_keys()
            self.save_rsa_keys(path, password)
            return

        local_key = hash_password(password)
        rsa_keys = []
        decrypted = True
        for key_file_path in [public_path, private_path]:
            with open(key_file_path) as key_file:
                try:
                    b64 = json.load(key_file)
                    iv = b64decode(b64['iv'])
                    ct = b64decode(b64['ciphertext'])
                    cipher = AES.new(local_key, AES.MODE_CBC, iv)
                    rsa_key = unpad(cipher.decrypt(ct), AES.block_size)
                    rsa_keys.append(rsa_key)
                except (ValueError, KeyError):
                    log.error('Wrong password for decryption')
                    decrypted = False

        if not decrypted:
            return

        self.public_key, self.private_key = rsa_keys
        log.info('The keys have been loaded.')

    def save_rsa_keys(self, path: str, password: str) -> None:
        if not self.public_key or not self.private_key:
            return

        local_key = hash_password(password)

        for el in zip([self.public_key, self.private_key], [self.PUBLIC_KEY_PATH_SUFFIX, self.PRIVATE_KEY_PATH_SUFFIX]):
            subdir_path = os.path.join(path, el[1])
            subdir_exists = os.path.isdir(subdir_path)

            if not subdir_exists:
                os.makedirs(subdir_path)

            cipher = AES.new(local_key, AES.MODE_CBC)
            ct_bytes = cipher.encrypt(pad(el[0], AES.block_size))
            iv = b64encode(cipher.iv).decode('utf-8')
            ct = b64encode(ct_bytes).decode('utf-8')
            result = json.dumps({'iv': iv, 'ciphertext': ct})

            with open(os.path.join(subdir_path, 'key.json'), 'w') as outfile:
                outfile.write(result)

        log.info(f'Client saved rsa keys: {path}')
