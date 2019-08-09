import os

from http.server import (BaseHTTPRequestHandler,
                         HTTPServer)


SERVER_ADDRESSES = {1: 'localhost:8001', 2: '0.0.0.0:8002'}


class HttpProcessor(BaseHTTPRequestHandler):
    URLS = {
        'HOME': '/',
        'FORM': '/form',
    }

    DEFAULT_ROUTING = {
        URLS['HOME']: '/'.join([os.getcwd(), 'form.html']),
        URLS['FORM']: '/'.join([os.getcwd(), 'form.html']),
    }

    def do_OPTION(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Credentials', True)
        self.send_header('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
        self.send_header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept")
        self.end_headers()

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
        allowed_server = '*'
        self.send_header("Access-Control-Allow-Origin", allowed_server)
        self.send_header('Content-Type', 'text/html')
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
    my_server = HTTPServer((server_addr, int(server_port)), HttpProcessor)
    try:
        my_server.serve_forever()
    except KeyboardInterrupt:
        my_server.shutdown()
