# will store files in memory and send them to the client
# will send If-Modified-Since header to the server
from socket import *
import SingleThreadServer
from utils import log, construct_http_request, parse_headers, construct_http_response

HOST = SingleThreadServer.HOST
PORT = SingleThreadServer.PORT + 1

# define constants
files = {}

def connect_with_server(method, path):
    clientSocket = socket(AF_INET, SOCK_STREAM) 
    clientSocket.connect((SingleThreadServer.HOST, SingleThreadServer.PORT))
    request = construct_http_request(method, path)
    clientSocket.send(request.encode())
    response = clientSocket.recv(1024).decode()
    return response

def get_modified_date_from_server(path):
    response = connect_with_server("HEAD", path)
    headers = response.splitlines()[1:]
    headers = parse_headers(headers)
    return headers["Last-Modified"]


def get_file_and_store_in_memory(path):
    log("Getting file from server")
    # get file from server
    response = connect_with_server("GET", path)

    # if response is 200 OK, store file in memory and send it to client
    if response.startswith("HTTP/1.1 200 OK"):
        # add file to memory
        headers, data = response.split("\r\n\r\n")
        headers = SingleThreadServer.parse_headers(headers.splitlines()[1:])
        files[path] = {"data": data, "modified-date": headers["Last-Modified"]}
        
    # send it to client
    return response


def handle_new_connection(connectionSocket):
    try:
        request = connectionSocket.recv(1024).decode()

        # parse the request
        request_words = request.split()
        path = request_words[1]
        
        # check if file is in memory
        if path in files:
            log("File is in memory")
            # check if it has been modified since last time
            local_modified_time = files[path]["modified-date"]
            log("Local modified time: " + local_modified_time)
            server_modified_time = get_modified_date_from_server(path)
            log("Server modified time: " + server_modified_time)

            if local_modified_time >= server_modified_time:
                # file has not been modified
                log("Sending file from memory")
                response = construct_http_response("200 OK", files[path]["data"])
            else: 
                # file has been modified
                response = get_file_and_store_in_memory(path)

        else: # file is not in memory
            log("File is not memory")
            response = get_file_and_store_in_memory(path)

    except Exception as e:
        print(e)
        response = construct_http_response("500 Internal Server Error")

    log("Sending response to client\n")
    connectionSocket.send(response.encode())
    connectionSocket.close()

def start_web_proxy_server():
    try:
        # SETUP SERVER
        serverSocket = socket(AF_INET, SOCK_STREAM)
        serverSocket.bind((HOST, PORT))
        serverSocket.listen(1)
        print('Listening on port', PORT)

        while True:
            connectionSocket, addr = serverSocket.accept()
            handle_new_connection(connectionSocket)
    except KeyboardInterrupt:
        print("Shutting down server...")
        serverSocket.close()
        exit()

def main():
    start_web_proxy_server()

if __name__ == "__main__":
    main()