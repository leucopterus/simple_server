import os
import cgi

from http import cookies
from http.server import (BaseHTTPRequestHandler,
                         HTTPServer)
from urllib.parse import parse_qs


SERVER_ADDRESSES = {1: '127.0.0.1:8001', 2: '127.0.0.2:8002'}


class HttpProcessor(BaseHTTPRequestHandler):
    URLS = {
        'HOME': '/',
        'FORM': '/form',
    }

    DEFAULT_ROUTING = {
        URLS['HOME']: '/'.join([os.getcwd(), 'form.html']),
        URLS['FORM']: '/'.join([os.getcwd(), 'form.html']),
    }

    def do_GET(self):
        self.routing()
        self.fill_header()
        self.path = self.DEFAULT_ROUTING[self.path]
        payload = self.context()
        self.rendering_with_params(**payload)

    def routing(self):
        if self.path not in self.DEFAULT_ROUTING:
            self.send_error(404, message="Page Not Found")
        else:
            self.send_response(200, message="OK")

    def fill_header(self):
        self.send_header('content-type', 'text/html')
        self.end_headers()

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
    server_config = SERVER_ADDRESSES[1]
    server_addr, server_port = server_config.split(':')
    try:
        my_server = HTTPServer((server_addr, int(server_port)), HttpProcessor)
        my_server.serve_forever()
    except KeyboardInterrupt:
        my_server.shutdown()
