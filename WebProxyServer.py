# will store files in memory and send them to the client
# will send If-Modified-Since header to the server
from socket import *
from SingleThreadServer import HOST as serverHost, PORT as serverPort
from utils import log, construct_http_request, parse_headers, construct_http_response

HOST = serverHost
PORT = serverPort + 1

# define constants
files = {}

def connect_with_server(method, path, additional_headers = {}):
    clientSocket = socket(AF_INET, SOCK_STREAM) 
    clientSocket.connect((serverHost, serverPort))
    request = construct_http_request(method, path, additional_headers)
    clientSocket.send(request.encode())
    response = clientSocket.recv(1024).decode()
    return response


def update_file_in_memory(path, response):
    headers, data = response.split("\r\n\r\n")
    headers = parse_headers(headers.splitlines()[1:])
    files[path] = {"data": data, "modified-date": headers["Last-Modified"]}

# note: if response from server is not 200 or 204, this function will simply pass on the response (ie. 404) to client
def request_file_and_store(path, isConditionalGet = False):
    headers = {}

    if isConditionalGet:
        log("Sending conditional GET request")
        headers = {"If-Modified-Since": files[path]["modified-date"]}

    # send request to server
    response = connect_with_server("GET", path, headers)

    # if response is 200 OK, store file in memory and send it to client
    if response.startswith("HTTP/1.1 200 OK"):
        log("Received file from server, storing file in memory")
        update_file_in_memory(path, response)

    # if response is 304 Not Modified, send file from memory to client
    elif response.startswith("HTTP/1.1 304 Not Modified"):
        log("File not modified, sending file from memory")
        response = construct_http_response("200 OK", files[path]["data"])
        
    # send it to client
    return response


def handle_new_connection(connectionSocket):
    try:
        request = connectionSocket.recv(1024).decode()

        # parse the request
        request_words = request.split()
        path = request_words[1]
        method = request_words[0]
        log("Handling " + method + " request on path " + path)
        
        # check if file is in memory
        if path in files:
            log("File is in memory")
            # send conditional GET request to server
            response = request_file_and_store(path, True)

        else: # file is not in memory
            log("File is not memory")

            response = request_file_and_store(path)

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