import os
import cgi

from http import cookies
from http.server import (BaseHTTPRequestHandler,
                         HTTPServer)
from datetime import datetime
from hashlib import sha256
from random import random


class HttpProcessor(BaseHTTPRequestHandler):
    SECRET = 'R@s1q*ePy5(gvOiom9Ve)xzSml0kKp&owGq7?ad/F'

    URLS = {
        'HOME': '/',
        'AUTH': '/auth',
        'FORM': '/form',
        'CHARGE': '/charge',
        'LOGIN': '/in',
        'LOGOUT': '/out',
    }

    DEFAULT_ROUTING = {
        URLS['HOME']: '/'.join([os.getcwd(), 'auth.html']),
        URLS['AUTH']: '/'.join([os.getcwd(), 'auth.html']),
        URLS['FORM']: '/'.join([os.getcwd(), 'form.html']),
        URLS['CHARGE']: '/'.join([os.getcwd(), 'charge.html']),
        URLS['LOGIN']: '/'.join([os.getcwd(), 'auth.html']),
        URLS['LOGOUT']: '/'.join([os.getcwd(), 'auth.html']),
    }

    def do_GET(self):
        self.routing()
        self.fill_header()
        if self.path != self.URLS['FORM']:
            self.path = self.DEFAULT_ROUTING[self.path]
            self.rendering()
        else:
            self.path = self.DEFAULT_ROUTING[self.path]
            payload = {
                '{{my_token}}': self.create_token(),
            }
            self.rendering_with_params(**payload)

    def do_POST(self):
        self.routing()
        self.fill_header()
        if self.path == self.URLS['CHARGE']:
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )
            purchase = form.getvalue("purchase")
            self.path = self.DEFAULT_ROUTING[self.path]
            payload = {
                '{{from_form.purchase}}': purchase,
            }
            self.rendering_with_params(**payload)

    def routing(self):
        if self.path not in self.DEFAULT_ROUTING:
            self.send_error(404, message="Page Not Found")
        else:
            self.send_response(200, message="OK")

    def fill_header(self):
        self.send_header('content-type', 'text/html')
        if self.path == self.URLS['LOGIN']:
            self.handle_auth("OK")
        elif self.path == '/charge':
            self.handle_charge()
        elif self.path == self.URLS['LOGOUT']:
            self.handle_auth()
        self.end_headers()

    def handle_auth(self, auth_val=0):
        cookie = cookies.SimpleCookie()
        cookie["auth_cookie"] = auth_val
        self.send_header("Set-Cookie", cookie.output(header='', sep=''))

    def handle_charge(self):
        if not self.headers.get("cookie") or self.headers.get("cookie") != 'auth_cookie=OK':
            self.send_error(401, message="Forbidden")

    def rendering(self):
        with open(self.path, encoding='UTF-8') as page:
            self.wfile.write(page.read().encode(encoding='UTF-8'))
        return

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

    def create_token(self):
        actual_time = str(datetime.now())
        random_data = str(random())
        full_data = ''.join([actual_time, random_data, self.SECRET])
        return sha256(full_data.encode()).hexdigest()


if __name__ == '__main__':
    my_server = HTTPServer(("", 8001), HttpProcessor)
    try:
        my_server.serve_forever()
    except KeyboardInterrupt:
        my_server.shutdown()
