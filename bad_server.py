import os

from http.server import (BaseHTTPRequestHandler,
                         HTTPServer)


class HttpProcessor(BaseHTTPRequestHandler):
    URLS = {
        'HOME': '/',
        'FORM': '/form',
    }

    DEFAULT_ROUTING = {
        URLS['HOME']: '/'.join([os.getcwd(), 'another_form.html']),
        URLS['FORM']: '/'.join([os.getcwd(), 'another_form.html']),
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
        self.send_header('Content-Type', 'text/html')
        self.end_headers()

    def rendering(self):
        with open(self.path, encoding='UTF-8') as page:
            full_data = []
            for line in page:
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
