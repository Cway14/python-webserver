from socket import *
from utils import *
import os
from datetime import datetime
import signal
from utils import *
import time

# define constants
HOST = get_local_ip()
PORT = 80
TIMEOUT = 10 #seconds

# define timeout handler 
def timeout_handler(signum, frame):
    raise Timeout

# checks if requested file has been modified since the last time it was requested
# return True if it has been modified or If-Modified-Since header is not present, False otherwise
# (true if file should be sent to client)
def is_modified_since(headers, path):
    if "If-Modified-Since" in headers:
        headerTime = headers["If-Modified-Since"]

        mtime = os.path.getmtime(path)

        # convert headerTime to datetime object
        headerTime = datetime.strptime(headerTime, "%a, %d %b %Y %H:%M:%S")
        mtime = datetime.fromtimestamp(mtime).replace(microsecond=0)

        if mtime <= headerTime: 
            return False

    return True

def handle_request(request):
    request_words = request.split()
    request_lines = request.splitlines()

    method = request_words[0]
    path = request_words[1]
    log("Handling " + method + " request on path " + path)
    path = path[1:] # remove the leading slash

    if path == "largeTest.html":
        time.sleep(2) # simulate a long request
        path = "test.html"
    
    if path == "timeoutTest.html":
        time.sleep(20) # simulate a request that times out
        path = "test.html"

    if method != "GET":
        raise NotAllowed

    headers = parse_headers(request_lines[1:])

    mtime = get_mtime(path)
    additional_headers = {"Last-Modified": from_timestamp_to_http_date(mtime)}
    
    
    if is_modified_since(headers, path):
        response_body = get_file(path)
        response = construct_http_response("200 OK", response_body, additional_headers)
    else:
        response = construct_http_response("304 Not Modified", additional_headers = additional_headers)

    return response

def handle_new_connection(connectionSocket, address):
    try:
        signal.alarm(TIMEOUT) # set timeout
        request = connectionSocket.recv(1024).decode()
        response = handle_request(request)
    except NotAllowed:
        response = construct_http_response("405 Method Not Allowed")
    except NotFound:
        response = construct_http_response("404 Not Found", "<h1>404 Not Found</h1>")
    except Timeout:
        response = construct_http_response("408 Request Timeout")
    except BadRequest:
        response = construct_http_response("400 Bad Request")
    except Exception as e:
        error(e)
        response = construct_http_response("500 Internal Server Error")
    
    signal.alarm(0) # cancel timeout 
    log("Responding with status code " + response.split()[1])
    connectionSocket.send(response.encode())
    connectionSocket.close()

def main():
    try:
        # SETUP TIMEOUT 
        signal.signal(signal.SIGALRM, timeout_handler)

        # SETUP SERVER
        serverSocket = socket(AF_INET, SOCK_STREAM)
        serverSocket.bind((HOST, PORT))
        serverSocket.listen(1)
        print(f'Listening on {HOST}, port {PORT}')


        while True:
            connectionSocket, addr = serverSocket.accept()
            handle_new_connection(connectionSocket, addr)
    except KeyboardInterrupt:
        print("Shutting down server...")
        serverSocket.close()
        exit()
    except BrokenPipeError:
        print("Client closed connection")

if __name__ == "__main__":
    main()