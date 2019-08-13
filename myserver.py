import os
import cgi

from http import cookies
from http.server import (BaseHTTPRequestHandler,
                         HTTPServer)
from datetime import datetime, timedelta
from hashlib import sha256
from random import random


class HttpProcessor(BaseHTTPRequestHandler):
    SECRET = 'R@s1q*ePy5(gvOiom9Ve)xzSml0kKp&owGq7?ad/F'

    TOKENS_DICT = {}

    # list of allowed urls
    URLS = {
        'HOME': '/',
        'AUTH': '/auth',
        'FORM': '/form',
        'CHARGE': '/charge',
        'LOGIN': '/in',
        'LOGOUT': '/out',
    }

    # connect url and html file in the PC
    DEFAULT_ROUTING = {
        URLS['HOME']: '/'.join([os.getcwd(), 'auth.html']),
        URLS['AUTH']: '/'.join([os.getcwd(), 'auth.html']),
        URLS['FORM']: '/'.join([os.getcwd(), 'form.html']),
        URLS['CHARGE']: '/'.join([os.getcwd(), 'charge.html']),
        URLS['LOGIN']: '/'.join([os.getcwd(), 'auth.html']),
        URLS['LOGOUT']: '/'.join([os.getcwd(), 'auth.html']),
    }

    def do_GET(self) -> None:
        self.routing()
        self.fill_header()
        if self.path != self.URLS['FORM']:
            self.path = self.DEFAULT_ROUTING[self.path]
            self.rendering()
        else:
            self.path = self.DEFAULT_ROUTING[self.path]
            self.token_delete_by_expired_time()
            payload = {
                '{{my_token}}': self.create_token(),
            }
            self.rendering_with_params(**payload)

    def do_POST(self) -> None:
        if self.path == self.URLS['CHARGE']:
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )
            token = form.getvalue("token")
            self.token_delete_by_expired_time()
            self.token_manipulation(token)
            self.routing()
            self.fill_header()
            purchase = form.getvalue("purchase")
            self.path = self.DEFAULT_ROUTING[self.path]
            payload = {
                '{{from_form.purchase}}': purchase,
            }
            self.rendering_with_params(**payload)

    def routing(self) -> None:
        """check if the page is presented"""
        if self.path not in self.DEFAULT_ROUTING:
            self.send_error(404, message="Page Not Found")
        else:
            self.send_response(200, message="OK")

    def fill_header(self) -> None:
        """
        add or delete cookies when login or logout page is chosen
        check if cookies are presented to get access to charge page
        """
        self.send_header('content-type', 'text/html')
        if self.path == self.URLS['LOGIN']:
            self.handle_auth(1)
        elif self.path == '/charge':
            self.handle_charge()
        elif self.path == self.URLS['LOGOUT']:
            self.handle_auth()
        self.end_headers()

    def handle_auth(self, auth_val: int = 0) -> None:
        """enable or disable cookie"""
        cookie = cookies.SimpleCookie()
        cookie["auth_cookie"] = auth_val
        self.send_header("Set-Cookie", cookie.output(header='', sep=''))

    def handle_charge(self) -> None:
        """check cookie"""
        if not self.headers.get("cookie") or self.headers.get("cookie") != 'auth_cookie=1':
            self.send_error(401, message="Forbidden")

    def create_token(self) -> str:
        """create token for the form page"""
        time_now = datetime.now()
        time_expired = time_now + timedelta(minutes=1)
        actual_time = str(time_now)
        random_data = str(random())
        full_data = ''.join([actual_time, random_data, self.SECRET])
        token = sha256(full_data.encode()).hexdigest()
        self.TOKENS_DICT[token] = time_expired
        return token

    def token_manipulation(self, token: str) -> None:
        """check and delete token"""
        self.token_check(token)
        self.token_delete(token)

    def token_check(self, token: str) -> None:
        """check if token is presented"""
        if token in self.TOKENS_DICT:
            return
        self.send_error(401, 'Wrong token')

    def token_delete(self, token: str) -> None:
        """delete token after using it"""
        if self.TOKENS_DICT and token in self.TOKENS_DICT:
            del self.TOKENS_DICT[token]

    def token_delete_by_expired_time(self) -> None:
        """check if token is expired"""
        control_time = datetime.now()
        list_of_keys_to_delete = []
        for key, value in self.TOKENS_DICT.items():
            if value < control_time:
                list_of_keys_to_delete.append(key)
        for key in list_of_keys_to_delete:
            del self.TOKENS_DICT[key]

    def rendering(self) -> None:
        """standard page rendering"""
        with open(self.path, encoding='UTF-8') as page:
            self.wfile.write(page.read().encode(encoding='UTF-8'))

    def rendering_with_params(self, **kwargs) -> None:
        """rendering page with parameters (like Jinja)"""
        with open(self.path, encoding='UTF-8') as page:
            full_data = []
            for line in page:
                for key, value in kwargs.items():
                    if line.find(key) != -1:
                        line = line.replace(key, value)
                full_data.append(line)
            data = ''.join(full_data)
            self.wfile.write(data.encode(encoding="UTF-8"))


if __name__ == '__main__':
    my_server = HTTPServer(("", 8001), HttpProcessor)
    try:
        my_server.serve_forever()
    except KeyboardInterrupt:
        my_server.shutdown()
