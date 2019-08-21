import os

from http.server import (BaseHTTPRequestHandler,
                         HTTPServer)


SERVER_ADDRESSES = {1: 'localhost:8001', 2: '0.0.0.0:8002'}


class HttpProcessor(BaseHTTPRequestHandler):
    # list of allowed urls
    URLS = {
        'HOME': '/',
        'FORM': '/form',
    }

    # connect url and html file in the PC
    DEFAULT_ROUTING = {
        URLS['HOME']: '/'.join([os.getcwd(), 'form.html']),
        URLS['FORM']: '/'.join([os.getcwd(), 'form.html']),
    }

    def do_OPTION(self) -> None:
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Credentials', True)
        self.send_header('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
        self.send_header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept")
        self.end_headers()

    def do_GET(self) -> None:
        self.routing()
        self.fill_header()
        self.path = self.DEFAULT_ROUTING[self.path]
        payload = self.context()
        self.rendering_with_params(**payload)

    def routing(self) -> None:
        """check if the page is presented"""
        if self.path not in self.DEFAULT_ROUTING:
            self.send_error(404, message="Page Not Found")
        else:
            self.send_response(200, message="OK")

    def fill_header(self) -> None:
        """fill the header out"""
        allowed_server = '*'
        self.send_header("Access-Control-Allow-Origin", allowed_server)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()

    def context(self, **kwargs) -> dict:
        """set default context to change in html pages"""
        default = {
            '{{server_a}}': SERVER_ADDRESSES[1],
            '{{server_b}}': SERVER_ADDRESSES[2],
        }
        for key, value in kwargs.items():
            default[key] = value
        return default

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
    server_config = SERVER_ADDRESSES[1]
    server_addr, server_port = server_config.split(':')
    my_server = HTTPServer((server_addr, int(server_port)), HttpProcessor)
    try:
        my_server.serve_forever()
    except KeyboardInterrupt:
        my_server.shutdown()
