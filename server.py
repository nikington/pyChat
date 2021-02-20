"""
    Chat application
"""
import socket
import threading
import time
import game

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

clients = {}
client_id = 0
chat_participants = {}


def add_client_info(client_connection, nick_name):
    global client_id
    client_id += 1
    clients[client_id] = {'connection': client_connection, 'name': nick_name}
    return client_id


def send_message(user_id, message_text, prefix=SERVER_MESSAGE_PREFIX, to_self=0):
    message = prefix + ': ' + message_text
    message = message.encode()
    if to_self == 1:
        recipient = clients[user_id]['connection']
        recipient.send(message)
    else:
        for client in clients:
            if client != user_id:
                recipient = clients[client]['connection']
                recipient.send(message)


def log(*log_line):
    now = time.time()
    milliseconds = '%03d' % int((now - int(now)) * 1000)
    current_time = time.strftime("%Y/%m/%d %H:%M:%S.") + milliseconds
    text = "".join(log_line)
    print(current_time, "-", text)


def start():
    log("[START] server has been started")
    while 1:
        server.listen()
        conn, addr = server.accept()
        user_name = conn.recv(1024).decode()
        user_id = add_client_info(conn, user_name)
        log("[USER_CONNECTION] new user has been connected. user_id: ", str(user_id), ", user_name:", user_name)
        thread = threading.Thread(target=handle_client, args=(conn, user_name, user_id))
        thread.start()


def handle_client(conn, user_name, user_id):
    send_message(user_id, f"Greetings, {user_name}!", to_self=1)
    message = "You are connected to the chat. Now you can send messages." \
              f'\nType "{HELP}" to see chat commands.'
    send_message(user_id, message, to_self=1)

    #
    # Add verification of existent users in the chat
    #

    message = user_name + ' has joined to the chat'
    send_message(user_id, message)
    log(f"[CHAT_JOIN] user {user_name} joins to the chat")
    chat_participants[user_id] = user_name
    while 1:
        new_message = conn.recv(1024).decode()
        if new_message.startswith('##'):

            if new_message == HELP:
                send_message(user_id, CMD_DESC, to_self=1)

            elif new_message == END_CHAT_CMD:
                send_message(user_id, f"{user_name} has left the chat")
                send_message(user_id, 'You leave the chat', to_self=1)
                log("[USER_END_CHAT] user: ", user_name)
                clients.pop(user_id)
                chat_participants.pop(user_id)
                conn.close
                break

            elif new_message == GAME_CMD:
                log(f"[GAME_START] user {user_name} started RPS")
                send_message(user_id, 'Rock Paper Scissors game has been started', to_self=1)
                game.rock_paper_scissors(conn)
                send_message(user_id, 'Now you can continue chat', to_self=1)
                log(f'[GAME_END] user {user_name} ended RPS')

            elif new_message == PARTICIPANT_COUNT:
                send_message(user_id, "Number of Participants - "+str(len(chat_participants)), to_self=1)

            elif new_message == PARTICIPANTS:
                list='\nChat participants: \n'
                for id, user in chat_participants.items():
                    list+=user+'\n'
                send_message(user_id, list, to_self=1)

            elif new_message == SHOW_TIME:
                now="Current time "+time.strftime("%Y/%m/%d %H:%M:%S")
                send_message(user_id, now, to_self=1)

            else:
                send_message(user_id, f'Invalid command. Type "{HELP}" to see chat commands.', to_self=1)

            log("[COMMAND_MESSAGE] user: ", user_name, ", command_text: ", new_message)

        else:
            log("[NEW_MESSAGE] user: ", user_name, ", message_text: ", new_message)
            send_message(user_id, new_message, user_name)


start()
