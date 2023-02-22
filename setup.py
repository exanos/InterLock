import pickle
import os
import json
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from Crypto.Protocol.KDF import scrypt

def store_data(data):
    password=data["password"]
    # Generate a random salt
    salt = get_random_bytes(16)
    # Derive a 256-bit key using scrypt
    key = scrypt(password, salt, 32, N=2**14, r=8, p=1)
    # Serialize data to JSON
    serialized_data = json.dumps(data).encode()
    # Pad the data to a multiple of 16 bytes
    padded_data = pad(serialized_data)
    # Generate a random initialization vector (IV)
    iv = get_random_bytes(16)
    # Encrypt the data using AES in CBC mode
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(padded_data)
    # Store salt, IV, and ciphertext in a binary file
    with open("data.bin", "wb") as f:
        f.write(salt)
        f.write(iv)
        f.write(ciphertext)

        
        
def load_data(password):
    # Load salt, IV, and ciphertext from binary file
    with open("data.bin", "rb") as f:
        salt = f.read(16)
        iv = f.read(16)
        ciphertext = f.read()
    # Derive key using scrypt
    key = scrypt(password, salt, 32, N=2**14, r=8, p=1)
    # Decrypt ciphertext using AES in CBC mode
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = cipher.decrypt(ciphertext)
    # Unpad the decrypted data
    serialized_data = unpad(padded_data)
    # Deserialize JSON data
    data = json.loads(serialized_data.decode())
    return data

def pad(data):
    # Pad the data to a multiple of 16 bytes
    padding_length = 16 - (len(data) % 16)
    padding = bytes([padding_length] * padding_length)
    return data + padding


def unpad(data):
    # Unpad the data
    padding_length = data[-1]
    return data[:-padding_length]


website_list = ['www.nonexistentwebsite.com', 'www.anothernonexistentwebsite.com']

password = "yourpassword"

blocked_list = {"website_list": website_list, "password": password}


store_data(blocked_list)


print(load_data(password))
