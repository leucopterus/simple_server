import os
import cgi

from http import cookies
from http.server import (BaseHTTPRequestHandler,
                         HTTPServer)
from urllib.parse import parse_qs


class HttpProcessor(BaseHTTPRequestHandler):
    LOGOUT = '/out'
    DEFAULT_ROUTING = {
        '/': '/'.join([os.getcwd(), 'auth.html']),
        '/auth': '/'.join([os.getcwd(), 'auth.html']),
        '/form': '/'.join([os.getcwd(), 'form.html']),
        '/charge': '/'.join([os.getcwd(), 'charge.html']),
        LOGOUT: '/'.join([os.getcwd(), 'auth.html']),
    }

    def do_GET(self):
        self.routing()
        self.fill_header()
        self.path = self.DEFAULT_ROUTING[self.path]
        self.rendering()

    def do_POST(self):
        self.routing()
        self.fill_header()
        if self.path == '/charge':
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )
            purchase = form.getvalue("purchase")
            self.path = self.DEFAULT_ROUTING[self.path]
            with open(self.path, encoding='UTF-8') as page:
                full_data = []
                for line in page:
                    if '{{from_form.purchase}}' in line:
                        line = line.replace('{{from_form.purchase}}', str(purchase))
                    full_data.append(line)
                data = ''.join(full_data)
                self.wfile.write(data.encode(encoding="UTF-8"))
            return

    def routing(self):
        if self.path not in self.DEFAULT_ROUTING:
            self.send_error(404, message="Page Not Found")
        else:
            self.send_response(200, message="OK")

    def fill_header(self):
        self.send_header('content-type', 'text/html')
        if self.path in ('/', '/auth'):
            self.handle_auth("OK")
        elif self.path == '/charge':
            self.handle_charge()
        elif self.path == self.LOGOUT:
            self.handle_auth()
        self.end_headers()

    def handle_auth(self, auth_val=0):
        cookie = cookies.SimpleCookie()
        cookie["auth_cookie"] = auth_val
        self.send_header("Set-Cookie", cookie.output(header='', sep=''))

    def handle_charge(self):
        # pass cookies from one server to another
        print(self.headers.get("cookie"))
        if not self.headers.get("cookie") or self.headers.get("cookie") != 'auth_cookie=OK':
            self.send_error(403, message="Forbidden")

    def rendering(self):
        with open(self.path, encoding='UTF-8') as page:
            self.wfile.write(page.read().encode(encoding='UTF-8'))
        return


if __name__ == "__main__":
    server_addresses = {1: '127.0.0.1:8001', 2: '127.0.0.2:8002'}
    answer = None
    while True:
        print('server can be run on two different addresses:', '1) 127.0.0.1:8001', '2) 127.0.0.2:8002', sep='\n')
        answer = input('Choose one of options in 1 or 2: ')
        if answer in ("1", "2"):
            break
    server_config = server_addresses[int(answer)]
    server_addr, server_port = server_config.split(':')
    try:
        my_server = HTTPServer((server_addr, int(server_port)), HttpProcessor)
        my_server.serve_forever()
    except KeyboardInterrupt:
        my_server.shutdown()
