import random
import socket


def rock_paper_scissors(client: socket):
    variants = {1: 'rock', 2: 'paper', 3: 'scissors'}
    initial_msg = '1 - rock\n2 - paper\n3 - scissors\nType you option 1, 2 or 3:'
    client.send(initial_msg.encode())
    while 1:
        while 1:
            user_option = client.recv(1024).decode()
            if user_option == '1' or user_option == '2' or user_option == '3' or user_option == 'END':
                break
            invalid_opt_msg = 'Invalid option. Please type 1, 2 or 3. Type "END" to end the game'
            client.send(invalid_opt_msg.encode())
        if user_option == 'END':
            break
        user_option = int(user_option)
        server_option = random.randint(1, 3)

        # Possible game result combinations
        draw = {1: 1, 2: 2, 3: 3}
        usr_win = {1: 3, 2: 1, 3: 2}
        srvr_win = {1: 2, 2: 3, 3: 1}

        game_result = 'Something goes wrong'

        if draw[user_option] == server_option:
            game_result = "It's a draw"
        elif usr_win[user_option] == server_option:
            game_result = 'Winner winner chicken dinner!'
        elif srvr_win[user_option] == server_option:
            game_result = 'You lose. Better luck next time.'

        message1 = 'Your option: ' + variants[user_option] + '. Server option: ' + variants[server_option]
        message2 = "\nLet's try again.\nType you option 1, 2, 3. Type 'END' to end the game"
        response = message1 + '\n' + game_result + '\n' + message2
        client.send(response.encode())

