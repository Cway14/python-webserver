from socket import *
from utils import *
import os
import time

# SETUP SERVER
serverName = 'localhost'
serverPort = 12000
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind((serverName, serverPort))

serverSocket.listen(1)
print('Listening on port', serverPort)
while True:
        connectionSocket, addr = serverSocket.accept()
        # get path from request
        try:
                request = connectionSocket.recv(1024).decode()
                request_words = request.split()
                method = request_words[0]
                path = request_words[1]
                file_name = path[1:]
                print("Handling " + method + " request on path " + path)
                
                if method == 'GET':
                        # parse headers
                        headers = parse_headers(request)
                        # get If-Modified-Since header
                        modified_since = 0
                        for header in headers:
                                if header[0] == "If-Modified-Since":
                                        modified_since = header[1]
                                        # TODO: parse date
                                        break
                        response = get_file(path, modified_since) 
                else:
                        response = get_headers("405 Method Not Allowed")
                        
                connectionSocket.send(response.encode())
        except Exception as e:
                print(e)
                response = get_headers("500 Internal Server Error")
        
        connectionSocket.close()


### TODO
#[X] 200 	OK
#[] 304 	Not Modified
#[] 400 	Bad request
#[#] 404 	Not Found
#[] 408 	Request Timed Out
