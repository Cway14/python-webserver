from socket import *
from utils import *
import os
import time
from datetime import datetime
import signal

# define exceptions
class BadRequest(Exception): pass
class NotFound(Exception): pass
class NotAllowed(Exception): pass
class Timeout(Exception): pass

def parse_headers(request):
    try:
        headers = {}
        for header in request:
            if header == "":
                break
            key, value = header.split(": ")
            headers[key] = value
        return headers
    except:
        raise BadRequest

def get_headers(status, body):
    headers = "HTTP/1.1 " + status + "\r\n"
    headers += "Content-Type: text/html\r\n"
    headers += "Content-Length: " + str(len(body)) + "\r\n"

    return headers

def construct_http_packet(status, body = ""):
    headers = get_headers(status, body)
    response = headers + "\r\n" + body

    return response

def get_file(path):
    path = path[1:] # remove the leading slash
    if os.path.exists(path):
        f = open(path, "r")
        file = f.read()
        f.close()
        return file
    else:
        raise NotFound

# checks if requested file has been modified since the last time it was requested
# return True if it has been modified, False otherwise
# returns True if If-Modified-Since header is not present
def is_modified_since(headers, path):
    if "If-Modified-Since" in headers:
        headerTime = headers["If-Modified-Since"]
        path = path[1:] # remove the leading slash

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
    print("Handling " + method + " request on path " + path)

    if method == 'GET':
            headers = parse_headers(request_lines[1:])
            if is_modified_since(headers, path):
                response_body = get_file(path)
                response = construct_http_packet("200 OK", response_body)
            else:
                response = construct_http_packet("304 Not Modified")
    else:
           raise NotAllowed
    return response

def timeout_handler(signum, frame):
    raise Timeout

try:
    # SETUP SERVER
    serverName = 'localhost'
    serverPort = 12000
    timeout = 2
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind((serverName, serverPort))
    serverSocket.settimeout(10)
    serverSocket.listen(1)
    serverSocket.settimeout(None)
    print('Listening on port', serverPort)
    signal.signal(signal.SIGALRM, timeout_handler)

    while True:
        connectionSocket, addr = serverSocket.accept()
            
        try:
            signal.alarm(timeout) # set timeout
            request = connectionSocket.recv(1024).decode()
            response = handle_request(request)
            signal.alarm(0) # cancel alarm
        except NotAllowed:
                response = construct_http_packet("405 Method Not Allowed")
        except NotFound:
                response = construct_http_packet("404 Not Found", "<h1>404 Not Found</h1>")
        except Timeout:
                response = construct_http_packet("408 Request Timeout")
        except Exception as e:
                print(e)
                response = construct_http_packet("500 Internal Server Error")
       
        print("Responding with status code " + response.split()[1])
        connectionSocket.send(response.encode())
        connectionSocket.close()
except KeyboardInterrupt:
    print("Shutting down server...")
    serverSocket.close()
    exit()

### TODO
#[X] 200 	OK
#[X] 304 	Not Modified
#[X] 400 	Bad request
#[X] 404 	Not Found
#[X] 408 	Request Timed Out
