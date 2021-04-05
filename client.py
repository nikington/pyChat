import socket
import threading
import signal
import sys


HOST = socket.gethostname()
PORT = 55500
END_CHAT_CMD = '##stop'
connection = 1


def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')
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


signal.signal(signal.SIGINT, signal_handler)

s = socket.socket()
s.connect((HOST, PORT))
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
thread = threading.Thread(target=get_message, args=())
thread.start()
thread = threading.Thread(target=send_message, args=())
thread.start()
