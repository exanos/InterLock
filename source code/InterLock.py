import getpass
import time
from datetime import datetime as dt, timedelta
import pickle
import os
import json
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from Crypto.Protocol.KDF import scrypt

def block_websites(website_list, hosts_path, redirect):
    with open(hosts_path, 'r+') as file:
        content = file.read()
        for website in website_list:
            if website in content:
                pass
            else:
                # write the website URLs to the hosts file and redirect them to localhost
                file.write(redirect + " " + website + "\n")
        file.flush()

def unblock_websites(website_list, hosts_path):
    with open(hosts_path, 'r+') as file:
        content = file.readlines()
        file.seek(0)
        for line in content:
            # remove the website URLs from the hosts file during the allowed time range
            if not any(website in line for website in website_list):
                file.write(line)
        file.truncate()
        file.flush()
    

def check_password(password):
    while True:
        user_input = getpass.getpass("Enter password to unblock websites: ")
        if user_input == password:
            return True
        else:
            print("Invalid password, please try again.")

def add_website(website_list):
    website = input("Enter the website to add: ")
    if website in website_list:
        print("Website already in the list.")
    else:
        website_list.append(website)
        print("Website added to the list.")

def remove_website(website_list):
    website = input("Enter the website to remove: ")
    if website not in website_list:
        print("Website not in the list.")
    else:
        website_list.remove(website)
        print("Website removed from the list.")

def modify_website(website_list):
    print("currently blocked websites:")
    for i in website_list:
        print(i)
    website = input("Enter the website to modify: ")
    if website not in website_list:
        print("Website not in the list.")
    else:
        new_website = input("Enter the new website: ")
        website_list[website_list.index(website)] = new_website
        print("Website modified.")
        
def give_break(website_list, hosts_path):
    redirect = "127.0.0.1"
    duration = int(input("Please enter the duration of break (in minutes): "))
    unblock_websites(website_list, hosts_path)
    
    end_time = dt.now() + timedelta(minutes=duration)
    print("Taking a break for", duration, "minutes.")
    while dt.now() < end_time:
        remaining_time = (end_time - dt.now()).seconds
        print("Time remaining:", remaining_time // 60, "minutes", remaining_time % 60, "seconds", end="\r")
        time.sleep(1)
        
    print("Break is over.")
    block_websites(website_list, hosts_path, redirect)

def print_menu():
    print("1. Add website")
    print("2. Remove website")
    print("3. Modify website")
    print("4. Give a Break")
    print("5. Change password")
    print("6. Exit")

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

def change_password(website_list):
    password=input("Enter new password:")
    blocked_data = {"website_list": website_list, "password": password}
    store_data(blocked_data)
    print("password changed succesfully!")
    return load_data(password)

def main():
    # change the path of the hosts file depending on your operating system
    hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
    redirect = "127.0.0.1"
    password=getpass.getpass("Enter password: ")
    # load the blocked websites and password from the file
    try:
        blocked_data = load_data(password)
        website_list = blocked_data["website_list"]
        password = blocked_data["password"]
        
    except (FileNotFoundError, KeyError):
        print("file not found or incorrect key; terminating...")# runs an infinite loop if the 'data.bin' file is moved
        while True:
            print("")
    
    # run this script as administrator to have write access to the hosts file
    while True:
        try:
            blocked_data = load_data(password)
            website_list = blocked_data["website_list"]
            password = blocked_data["password"]
        except (FileNotFoundError, KeyError):
            print("file not found or incorrect key; terminating...")# file not found or incorrect key;
            while True:
                pass
        block_websites(website_list, hosts_path, redirect)
        print_menu()
        choice = input("Enter your choice: ")
        if choice == '1':
            add_website(website_list)
            blocked_data = {"website_list": website_list, "password": password}
            store_data(blocked_data)
        elif choice == '2':
            if check_password(password):
                remove_website(website_list)
                blocked_data = {"website_list": website_list, "password": password}
                store_data(blocked_data)
            else:
                print("Invalid password")
        elif choice == '3':
            if check_password(password): 
                modify_website(website_list)
                blocked_data = {"website_list": website_list, "password": password}
                store_data(blocked_data)
            else:
                print("Invalid password")
        elif choice =='4':
            if check_password(password):
                give_break(website_list,hosts_path)
            else:
                print("Invalid password")
        elif choice =='5':
            if check_password(password):
                blocked_data=change_password(website_list)
                password=blocked_data["password"]
            else:
                print("Invalid password")
        elif choice == '6':
            break
        else:
            print("Invalid choice.")
        

if __name__ == '__main__':
    main()

