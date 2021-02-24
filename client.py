import socket
import threading
import sys
import os

HOST = socket.gethostname()
PORT = 55500


def close_chat(client):
    client.close()
    return 0


def get_message():
    connection = 1
    while connection:
        incoming_message = s.recv(1024).decode()
        print(incoming_message)


def send_message():
    connection = 1
    while connection:
        new_message_text = input(str())
        s.send(new_message_text.encode())


os.system('cls' if os.name == 'nt' else 'clear')
try:
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
except:
    print("Server parametrs were not provided. Default accepted.")

tc = True
while tc:
    tc = False
    try:
        s = socket.socket()
        s.connect((HOST, PORT))
    except TimeoutError:
        print(f"Server {HOST} on {PORT} is not available.")
        tc = True
        print("Enter Host (IP):")
        HOST = str(input())
        print("Enter port number")
        PORT = int(input())

print("Client app is started.")
user_exist = True
while user_exist:
    print("Please enter your nickname:")
    new_message_text = input(str())
    s.send(new_message_text.encode())
    user_exist = False
    incoming_message = s.recv(1024).decode()
    print(incoming_message)
    if incoming_message == "System: The user with this name already exist":
        user_exist = True
os.system('cls' if os.name == 'nt' else 'clear')
thread = threading.Thread(target=get_message, args=())
thread.start()
thread = threading.Thread(target=send_message, args=())
thread.start()
