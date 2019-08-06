import os
import cgi

from http import cookies
from http.server import (BaseHTTPRequestHandler,
                         HTTPServer)
from urllib.parse import parse_qs


class HttpProcessor(BaseHTTPRequestHandler):
    DEFAULT_ROUTING = {
        '/': '/'.join([os.getcwd(), 'form.html']),
        '/form': '/'.join([os.getcwd(), 'form.html']),
    }

    def do_GET(self):
        self.routing()
        self.fill_header()
        self.path = self.DEFAULT_ROUTING[self.path]
        self.rendering()

    def routing(self):
        if self.path not in self.DEFAULT_ROUTING:
            self.send_error(404, message="Page Not Found")
        else:
            self.send_response(200, message="OK")

    def fill_header(self):
        self.send_header('content-type', 'text/html')
        self.end_headers()

    def rendering(self):
        with open(self.path, encoding='UTF-8') as page:
            self.wfile.write(page.read().encode(encoding='UTF-8'))
        return


if __name__ == "__main__":
    server_addresses = {1: '127.0.0.1:8001', 2: '127.0.0.2:8002'}
    server_config = server_addresses[1]
    server_addr, server_port = server_config.split(':')
    try:
        my_server = HTTPServer((server_addr, int(server_port)), HttpProcessor)
        my_server.serve_forever()
    except KeyboardInterrupt:
        my_server.shutdown()
