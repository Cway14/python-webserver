from datetime import datetime
import os

# define exceptions
class BadRequest(Exception): pass
class NotFound(Exception): pass
class NotAllowed(Exception): pass
class Timeout(Exception): pass

def log(message):
    print("LOG - " + message)

def construct_http_request(method, path):
    request = method + " " + path + " HTTP/1.1\r\n"
    request += "\r\n"

    return request

def construct_headers(status, body, additional_headers = {}):
    headers = "HTTP/1.1 " + status + "\r\n"
    headers += "Content-Type: text/html\r\n"
    headers += "Content-Length: " + str(len(body)) + "\r\n"

    for key, value in additional_headers.items():
        headers += key + ": " + str(value) + "\r\n"

    return headers

def construct_http_response(status, body = "", additional_headers = {}):
    headers = construct_headers(status, body, additional_headers)
    response = headers + "\r\n" + body

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
    return datetime.fromtimestamp(timestamp).strftime("%a, %d %b %Y %H:%M:%S %Z")
