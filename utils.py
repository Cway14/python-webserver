from datetime import datetime
from threading import get_native_id
from socket import *
import os

# define exceptions
class BadRequest(Exception): pass
class NotFound(Exception): pass
class NotAllowed(Exception): pass
class Timeout(Exception): pass

terminal_colors = ['\033[94m', '\033[92m', '\033[93m']

def log(message):
    tid = get_native_id()
    color = terminal_colors[tid % 3]
    print(f'{color}LOG - Thread: {str(tid)} - {message} \033[0m')

def error(message):
    errorColor = '\033[91m'
    tid = get_native_id()
    print(f'{errorColor}ERROR - Thread: {str(tid)} - {message} \033[0m')

def construct_http_request(method, path, additional_headers = {}):
    request = method + " " + path + " HTTP/1.1\r\n"

    for key, value in additional_headers.items():
        request += key + ": " + str(value) + "\r\n"

    request += "\r\n"

    return request

def construct_headers(status, body, additional_headers = {}):
    headers = "HTTP/1.1 " + status + "\r\n"
    headers += "Content-Type: text/html\r\n"
    headers += "Content-Length: " + str(len(body)) + "\r\n"

    for key, value in additional_headers.items():
        headers += key + ": " + str(value) + "\r\n"

    headers += "\r\n"
    return headers

def construct_http_response(status, body = "", additional_headers = {}):
    headers = construct_headers(status, body, additional_headers)
    response = headers + body

    return response

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

def get_file(path):
    if os.path.exists(path):
        f = open(path, "r")
        file = f.read()
        f.close()
        return file
    else:
        raise NotFound

def get_mtime(path):
    if os.path.exists(path):
        return os.path.getmtime(path)
    else:
        raise NotFound
        
def from_timestamp_to_http_date(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%a, %d %b %Y %H:%M:%S")

# CODE FROM: https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
def get_local_ip():
    print("Getting local IP address")
    try:
        s = socket(AF_INET, SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        print("Local IP address is " + ip)
    except Exception as e: 
        error("Could not get local IP address, resorting to localhost")
        ip = "localhost"
    return ip
