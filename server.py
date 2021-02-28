"""
    Chat application
"""
import socket
import threading
from datetime import datetime
from game import rock_paper_scissors

SERVER_MESSAGE_PREFIX = 'System'

# Chat commands:
HELP = '##help'
END_CHAT_CMD = '##stop'
GAME_CMD = '##game'
PARTICIPANT_COUNT = '##number'
PARTICIPANTS = '##users'
SHOW_TIME = '##time'

COMMANDS_LIST = {HELP, GAME_CMD, PARTICIPANT_COUNT, PARTICIPANTS, SHOW_TIME, END_CHAT_CMD}

CMD_DESC = f"\n{HELP} - show chat commands" \
           f"\n{GAME_CMD} - start Rock Paper Scissors game" \
           f"\n{PARTICIPANT_COUNT} - number of users in chat" \
           f"\n{PARTICIPANTS} - name of users in chats" \
           f"\n{SHOW_TIME} - current time" \
           f"\n{END_CHAT_CMD} - exit from the chat"

HOST = socket.gethostname()
PORT = 55500
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

clients = []    # [{'connection': socket, 'name': user_name}, ...]


def send_message(user_id, message_text, prefix=SERVER_MESSAGE_PREFIX, to_self=0):
    message = prefix + ': ' + message_text
    message = message.encode()
    if to_self == 1:
        recipient = clients[user_id]['connection']
        recipient.send(message)
    else:
        for client_id in range(len(clients)):
            if client_id != user_id:
                recipient = clients[client_id]['connection']
                recipient.send(message)


def log(*log_line):
    print(datetime.now().isoformat(sep=' ', timespec='milliseconds'), "-", ' '.join(log_line))


def start():
    log("[START] server has been started")
    while True:
        server.listen()
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn,))
        thread.start()


def check_user_name(conn):
    exist = True
    while exist:
        user_name = conn.recv(128).decode()
        exist = False
        for client in clients:
            if user_name == client['name']:
                exist = True
                conn.send("System: The user with this name already exist".encode())
    return user_name


def user_initial_steps(user_id):
    user_name = clients[user_id]['name']
    log(f"[USER_CONNECTION] new user has been connected. user_id: {user_id}, user_name: {user_name}.")
    send_message(user_id, f"Greetings, {user_name}!", to_self=1)
    message = "You are connected to the chat. Now you can send messages." \
              f'\nType "{HELP}" to see chat commands.'
    send_message(user_id, message, to_self=1)
    send_message(user_id, user_name + ' has joined to the chat')
    log(f"[CHAT_JOIN] user {user_name} joins to the chat. Active users: {len(clients)}")


def handle_client(conn):
    try:
        user_name = check_user_name(conn)
    except ConnectionResetError:
        log(f"[CLIENT_DISCONNECT] unregistered user disconnected")
    else:
        clients.append({'connection': conn, 'name': user_name})
        user_id = len(clients) - 1
        print(f"user_id: {user_id}")
        print(clients)
        user_initial_steps(user_id)
        try:
            while True:
                new_message = conn.recv(1024).decode()
                if new_message.startswith('##'):

                    if new_message == HELP:
                        send_message(user_id, CMD_DESC, to_self=1)

                    elif new_message == END_CHAT_CMD:
                        send_message(user_id, 'You leave the chat', to_self=1)
                        send_message(user_id, f"{user_name} left the chat")
                        log(f"[USER_END_CHAT] user: {user_name}.")
                        break

                    elif new_message == GAME_CMD:
                        log(f"[GAME_START] user {user_name} started RPS")
                        send_message(user_id, 'Rock Paper Scissors game has been started', to_self=1)
                        rock_paper_scissors(conn)
                        send_message(user_id, 'Now you can continue chat', to_self=1)
                        log(f'[GAME_END] user {user_name} ended RPS')

                    elif new_message == PARTICIPANT_COUNT:
                        send_message(user_id, f"Number of Participants - {len(clients)}", to_self=1)

                    elif new_message == PARTICIPANTS:
                        users_list = 'Chat participants: \n'
                        for client in clients:
                            users_list += client['name'] + '\n'
                        send_message(user_id, users_list, to_self=1)

                    elif new_message == SHOW_TIME:
                        send_message(user_id, "Current time " + datetime.now().isoformat(sep=' ', timespec='seconds'), to_self=1)

                    else:
                        send_message(user_id, f'Invalid command. Type "{HELP}" to see chat commands.', to_self=1)

                    log(f"[COMMAND_MESSAGE] user: {user_name}, command_text: {new_message}")

                else:
                    send_message(user_id, new_message, user_name)
                    log(f"[NEW_MESSAGE] user: {user_name}, message_text: {new_message}")

        except ConnectionResetError:
            send_message(user_id, f"{user_name} has been disconnected")
            log(f"[CLIENT_DISCONNECT] {user_name} has been disconnected. Active users: {len(clients)}")
        finally:
            clients.pop(user_id)
            log(f"Active users: {len(clients)}")
    finally:
        conn.close()
        


start()
