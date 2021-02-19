import socket
import threading


HOST = socket.gethostname()
PORT = 55500

s = socket.socket()
s.connect((HOST,PORT))
print("Client app is started.\nPlease enter your nickname:")


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


thread = threading.Thread(target=get_message, args=())
thread.start()
thread = threading.Thread(target=send_message, args=())
thread.start()
