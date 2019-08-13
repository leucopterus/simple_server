import os

from http.server import (BaseHTTPRequestHandler,
                         HTTPServer)
from datetime import datetime
from hashlib import sha256
from random import random

class HttpProcessor(BaseHTTPRequestHandler):
    BAD_SECRETE = 'E#s1q%ePy4[nvY8Tm9Vx}EzSml0jFp&oqWq7!mp|K'

    # list of allowed urls
    URLS = {
        'HOME': '/',
        'FORM': '/form',
    }

    # connect url and html file in the PC
    DEFAULT_ROUTING = {
        URLS['HOME']: '/'.join([os.getcwd(), 'another_form.html']),
        URLS['FORM']: '/'.join([os.getcwd(), 'another_form.html']),
    }

    def do_GET(self) -> None:
        self.routing()
        self.fill_header()
        if self.path not in (self.URLS['FORM'], self.URLS['HOME']):
            self.path = self.DEFAULT_ROUTING[self.path]
            self.rendering()
        else:
            self.path = self.DEFAULT_ROUTING[self.path]
            payload = {
                '{{my_bad_token}}': self.create_token(),
            }
            self.rendering_with_params(**payload)

    def routing(self) -> None:
        """check if the page is presented"""
        if self.path not in self.DEFAULT_ROUTING:
            self.send_error(404, message="Page Not Found")
        else:
            self.send_response(200, message="OK")

    def fill_header(self) -> None:
        """add headers to response"""
        self.send_header('Content-Type', 'text/html')
        self.end_headers()

    def create_token(self) -> str:
        """create token for the form page"""
        time_now = datetime.now()
        actual_time = str(time_now)
        random_data = str(random())
        full_data = ''.join([actual_time, random_data, self.BAD_SECRETE])
        token = sha256(full_data.encode()).hexdigest()
        return token

    def rendering(self):
        """standard page rendering"""
        with open(self.path, encoding='UTF-8') as page:
            full_data = []
            for line in page:
                full_data.append(line)
            data = ''.join(full_data)
            self.wfile.write(data.encode(encoding="UTF-8"))

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


if __name__ == "__main__":
    server_config = "0.0.0.0:8002"
    server_addr, server_port = server_config.split(':')
    my_server = HTTPServer((server_addr, int(server_port)), HttpProcessor)
    try:
        my_server.serve_forever()
    except KeyboardInterrupt:
        my_server.shutdown()
