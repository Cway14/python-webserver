from socket import *
from utils import *
import os
import time


def parse_headers(request):
    headers = {}

    return headers

def get_headers(status, body):
    headers = "HTTP/1.1" + status + "\r\n"
    headers += "Content-Type: text/html\r\n"
    headers += "Content-Length: " + str(len(body)) + "\r\n"

    return headers

def construct_http_packet(status, body = ""):
    headers = get_headers(status, body)
    response = headers + "\r\n" + body

    print("Responding with: " + status)
    return response

def get_file(path):
    path = path[1:] # remove the leading slash
    if os.path.exists(path):
        f = open(path, "r")
        file = f.read()
        f.close()
        return file
    else:
        return None

def is_modified_since(headers, path):
    return False


# SETUP SERVER
serverName = 'localhost'
serverPort = 12000
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind((serverName, serverPort))

serverSocket.listen(1)
print('Listening on port', serverPort)
while True:
        connectionSocket, addr = serverSocket.accept()
        request = connectionSocket.recv(1024).decode()
        try:
                request_words = request.split()
                method = request_words[0]
                path = request_words[1]
                print("Handling " + method + " request on path " + path)
                
                if method == 'GET':
                        # parse headers
                        response_body = get_file(path)
                        if response_body:
                            response = construct_http_packet("200 OK", response_body)
                        else: 
                            response = construct_http_packet("404 Not Found", "<h1>404 Not Found</h1>")
                else:
                        response = construct_http_packet("405 Method Not Allowed")
                        
                connectionSocket.send(response.encode())
        except Exception as e:
                print(e)
                response = construct_http_packet("500 Internal Server Error")
        
        connectionSocket.close()


### TODO
#[X] 200 	OK
#[] 304 	Not Modified
#[] 400 	Bad request
#[#] 404 	Not Found
#[] 408 	Request Timed Out
