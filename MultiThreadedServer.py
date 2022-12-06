import signal
import threading
from socket import *
from SingleThreadServer import handle_new_connection, PORT, HOST, timeout_handler
from utils import log

threads = []

# TODO:
# assign new port number to each thread
def handle_new_connection_multi(connectionSocket, address):
    log("Handling new connection on port " + str(address[1]))
    handle_new_connection(connectionSocket, address)
    log("Closing thread " + str(threading.get_native_id()))

    # bind to new port
    # send from new socket

def main():
    try:

        # SETUP TIMEOUT 
        signal.signal(signal.SIGALRM, timeout_handler)
        # SETUP SERVER

        serverSocket = socket(AF_INET, SOCK_STREAM)
        serverSocket.bind((HOST, PORT))
        serverSocket.listen(1)
        print(f'Listening on {HOST}, port {PORT}')
        print(f'Test file: http://{HOST}:{PORT}/test.html')

        while True:
            connectionSocket, addr = serverSocket.accept()
            newServerThread = threading.Thread(target=handle_new_connection_multi, args=(connectionSocket, addr))
            newServerThread.start()
            threads.append(newServerThread)

    except KeyboardInterrupt:
        print("Shutting down server...")
        serverSocket.close()
        exit()

if __name__ == "__main__":
    main()
