import threading
import socket
import signal
import time


PORT = 55500
END_CHAT_CMD = '##stop'


class SendMessage(threading.Thread):
    def __init__(self, socket):
        self.client_socket = socket
        threading.Thread.__init__(self)

        # The shutdown_flag is a threading.Event object that
        # indicates whether the thread should be terminated.
        self.shutdown_flag = threading.Event()
   
    def run(self):
        while not self.shutdown_flag.is_set():
            try:
                new_message_text = input(str())
                self.client_socket.send(new_message_text.encode())

                if new_message_text == END_CHAT_CMD:
                    self.shutdown_flag.set()

            # Handle exception when server was shut down
            except ConnectionResetError:
                self.shutdown_flag.set()
                print('[INFO] connection was closed')

        print('[INFO] stop sending messages')
        self.client_socket.close()


class ReceiveMessage(threading.Thread):

    def __init__(self, socket):
        self.client_socket = socket
        threading.Thread.__init__(self)

        # The shutdown_flag is a threading.Event object that
        # indicates whether the thread should be terminated.
        self.shutdown_flag = threading.Event()

    def run(self):
        while not self.shutdown_flag.is_set():
            try:
                incoming_message = self.client_socket.recv(1024).decode()
                print(incoming_message)

            # Handle exceptions when chat was closed by client
            # ConnectionAbortedError - END_CHAT_CMD
            # OSError - Ctrl c
            except (ConnectionAbortedError, OSError):
                self.shutdown_flag.set()
                print('[INFO] connection was terminated')

        print('[INFO] stop receiving messages')
        
        
class ServiceExit(Exception):
    """
    Custom exception which is used to trigger the clean exit
    of all running threads and the main program.
    """
    pass


def service_shutdown(sig, frame):
    print('Caught the termination signal. Press Enter to finish the program')
    raise ServiceExit


def main():
    # Register the signal handlers
    signal.signal(signal.SIGINT, service_shutdown)

    host = socket.gethostname()
    s = socket.socket()
    s.connect((host, PORT))
    print("[INFO] client app is started.")

    # Check user name for duplicates on the server
    while True:
        print("Please enter your nickname:")
        new_message_text = input(str())
        if new_message_text == '':
            print("Nick name can not be empty")
            continue
        s.send(new_message_text.encode())
        incoming_message = s.recv(1024).decode()
        print(incoming_message)
        if incoming_message != "System: The user with this name already exist":
            break
            
    try:
        t1 = SendMessage(s)
        t2 = ReceiveMessage(s)
        t1.start()
        t2.start()

        # Keep the main thread running, otherwise signals are ignored.
        while t1.is_alive() and t2.is_alive():
            time.sleep(0.5)          

        # in case thread is still running because of running input
        if t1.is_alive():
            print('Press Enter to finish the program')
           
    except ServiceExit:
        # Terminate the running threads.
        # Set the shutdown flag on each thread to trigger a clean shutdown of each thread.
        t1.shutdown_flag.set()
        t2.shutdown_flag.set()

    # Wait for the threads to close...
    t1.join()
    t2.join()

    print('[EXIT] Closing main program')


if __name__ == '__main__':
    main()
