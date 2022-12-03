import threading
from socket import *
from SingleThreadServer import handle_new_connection


# define constants
HOST = 'localhost'
PORT = 12000
TIMEOUT = 2

threads = []


def main():
    try:
        # SETUP SERVER

        serverSocket = socket(AF_INET, SOCK_STREAM)
        serverSocket.bind((HOST, PORT))
        serverSocket.listen(1)
        print('Listening on port', PORT)


        while True:
            connectionSocket, addr = serverSocket.accept()
            newServerThread = threading.Thread(target=handle_new_connection, args=(connectionSocket,))
            newServerThread.start()
            threads.append(newServerThread)

    except KeyboardInterrupt:
        print("Shutting down server...")
        serverSocket.close()
        exit()

if __name__ == "__main__":
    main()
