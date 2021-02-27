import socket
import threading

import sys
import os
import signal

HOST = socket.gethostname()
PORT = 55500
END_CHAT_CMD = '##stop'
connection = 1


def signal_handler(signal, frame):
  sys.exit(0)


def close_chat(client):
    client.close()
    return 0


def get_message():
    global connection
    while connection:
        incoming_message = s.recv(1024).decode()
        if incoming_message == '':
            connection = 0
        print(incoming_message)


def send_message():
    global connection
    while connection:
        new_message_text = input(str())
        if new_message_text == END_CHAT_CMD:
            connection = 0
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
        signal.signal(signal.SIGINT, signal_handler)
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

