import os
import cgi

from http import cookies
from http.server import (BaseHTTPRequestHandler,
                         HTTPServer)


SERVER_ADDRESSES = {1: 'localhost:8001', 2: '0.0.0.0:8002'}


class HttpProcessor(BaseHTTPRequestHandler):
    URLS = {
        'HOME': '/',
        'AUTH': '/auth',
        'CHARGE': '/charge',
        'LOGOUT': '/out',
    }

    DEFAULT_ROUTING = {
        URLS['HOME']: '/'.join([os.getcwd(), 'auth.html']),
        URLS['AUTH']: '/'.join([os.getcwd(), 'auth.html']),
        URLS['CHARGE']: '/'.join([os.getcwd(), 'charge.html']),
        URLS['LOGOUT']: '/'.join([os.getcwd(), 'auth.html']),
    }

    def do_GET(self):
        self.routing()
        self.fill_header()
        self.path = self.DEFAULT_ROUTING[self.path]
        payload = self.context()
        self.rendering_with_params(**payload)

    def do_OPTION(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Credentials', True)
        self.send_header('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
        self.end_headers()

    def do_POST(self):
        self.routing()
        self.fill_header()
        if self.path == self.URLS['CHARGE']:
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={
                    'REQUEST_METHOD': 'POST',
                    'CONTENT_TYPE': 'text/html'
                }
                # {'REQUEST_METHOD': 'POST'}
            )
            purchase = form.getvalue("purchase")
            # print(f"purchase = {purchase}")
            self.path = self.DEFAULT_ROUTING[self.path]
            payload = {
                '{{from_form.purchase}}': purchase,
            }
            payload = self.context(**payload)
            self.rendering_with_params(**payload)
            # print(f'POST get {purchase}')
            self.wfile.write(f'{purchase}$ were sent'.encode(encoding='UTF-8'))
        return

    def routing(self):
        if self.path not in self.DEFAULT_ROUTING:
            self.send_error(404, message="Page Not Found")
        else:
            self.send_response(200)

    def fill_header(self):
        allowed_server = '*'
        self.send_header("Access-Control-Allow-Origin", allowed_server)
        self.send_header('Content-Type', 'text/html')
        if self.path in (self.URLS['HOME'], self.URLS['AUTH']):
            self.handle_auth("OK")
        elif self.path == self.URLS['CHARGE']:
            self.handle_charge()
        elif self.path == self.URLS['LOGOUT']:
            self.handle_auth()
        # allowed_server = ''.join(['http://', SERVER_ADDRESSES[1]])
        self.end_headers()

    def handle_auth(self, auth_val=0):
        cookie = cookies.SimpleCookie()
        cookie["auth_cookie"] = auth_val
        self.send_header("Set-Cookie", cookie.output(header='', sep=''))

    def handle_charge(self):
        if not self.headers.get("cookie") or 'auth_cookie=OK' not in self.headers.get("cookie"):
            self.send_error(401, message="Forbidden")

    def context(self, **kwargs):
        default = {
            '{{server_a}}': SERVER_ADDRESSES[1],
            '{{server_b}}': SERVER_ADDRESSES[2],
        }
        for key, value in kwargs.items():
            default[key] = value
        return default

    def rendering_with_params(self, **kwargs):
        with open(self.path, encoding='UTF-8') as page:
            full_data = []
            for line in page:
                for key, value in kwargs.items():
                    if line.find(key) != -1:
                        line = line.replace(key, value)
                full_data.append(line)
            data = ''.join(full_data)
            self.wfile.write(data.encode(encoding="UTF-8"))


if __name__ == "__main__":
    server_config = SERVER_ADDRESSES[2]
    server_addr, server_port = server_config.split(':')
    my_server = HTTPServer((server_addr, int(server_port)), HttpProcessor)
    try:
        my_server.serve_forever()
    except KeyboardInterrupt:
        my_server.shutdown()
