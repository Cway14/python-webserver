# Include Python's Socket Library
from socket import *
from utils import *
from SingleThreadServer import HOST as serverHost, PORT as serverPort

def connect_to_server():
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverHost, serverPort))
    return clientSocket

def send_test_request(clientSocket, path):
    request = construct_http_request("GET", path)
    clientSocket.send(request.encode())
    response = clientSocket.recv(1024).decode()
    print("Connected to server port: " + str(clientSocket.getpeername()))
    clientSocket.close()
    return response

client1 = connect_to_server()
client2 = connect_to_server()
client3 = connect_to_server()

send_test_request(client1, "/timeoutTest.html")
send_test_request(client3, "/test.html")
send_test_request(client2, "/largeTest.html")