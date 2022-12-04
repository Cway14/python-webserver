from socket import *
from utils import *
import os
from datetime import datetime
import signal
from utils import *

# define constants
HOST = 'localhost'
PORT = 12000
TIMEOUT = 5 #seconds

# define timeout handler 
def timeout_handler(signum, frame):
    raise Timeout

# checks if requested file has been modified since the last time it was requested
# return True if it has been modified, False otherwise
# returns True if If-Modified-Since header is not present
def is_modified_since(headers, path):
    if "If-Modified-Since" in headers:
        headerTime = headers["If-Modified-Since"]

        mtime = os.path.getmtime(path)

        # convert headerTime to datetime object
        headerTime = datetime.strptime(headerTime, "%a, %d %b %Y %H:%M:%S %Z")
        mtime = datetime.fromtimestamp(mtime)

        if mtime < headerTime:
            return False

    return True

def handle_request(request):
    request_words = request.split()
    request_lines = request.splitlines()

    method = request_words[0]
    path = request_words[1]
    path = path[1:] # remove the leading slash
    print("Handling " + method + " request on path " + path)

    if method not in ['GET', 'HEAD']:
        raise NotAllowed

    headers = parse_headers(request_lines[1:])

    mtime = get_mtime(path)
    additional_headers = {"Last-Modified": from_timestamp_to_http_date(mtime)}
    
    if method == "HEAD":
        return construct_http_response("200 OK", additional_headers = additional_headers)
    
    if is_modified_since(headers, path):
        response_body = get_file(path)
        response = construct_http_response("200 OK", response_body, additional_headers)
    else:
        response = construct_http_response("304 Not Modified", additional_headers = additional_headers)

    return response

def handle_new_connection(connectionSocket):
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
        except Exception as e:
                print(e)
                response = construct_http_response("500 Internal Server Error")
       
        signal.alarm(0) # cancel timeout 
        print("Responding with status code " + response.split()[1])
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
        print('Listening on port', PORT)


        while True:
            connectionSocket, addr = serverSocket.accept()
            handle_new_connection(connectionSocket)
    except KeyboardInterrupt:
        print("Shutting down server...")
        serverSocket.close()
        exit()

if __name__ == "__main__":
    main()