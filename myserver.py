import os
import cgi

from http import cookies
from http.server import (BaseHTTPRequestHandler,
                         HTTPServer)


class HttpProcessor(BaseHTTPRequestHandler):
    LOGOUT = '/out'
    DEFAULT_ROUTING = {
        '/': '/'.join([os.getcwd(), 'auth.html']),
        '/auth': '/'.join([os.getcwd(), 'auth.html']),
        '/form': '/'.join([os.getcwd(), 'form.html']),
        '/charge': '/'.join([os.getcwd(), 'charge.html']),
        LOGOUT: '/'.join([os.getcwd(), 'auth.html']),
    }

    def do_GET(self) -> None:
        self.routing()
        self.fill_header()
        self.path = self.DEFAULT_ROUTING[self.path]
        self.rendering()

    def do_POST(self) -> None:
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

    def routing(self) -> None:
        if self.path not in self.DEFAULT_ROUTING:
            self.send_error(404, message="Page Not Found")
        else:
            self.send_response(200, message="OK")

    def fill_header(self) -> None:
        self.send_header('content-type', 'text/html')
        if self.path in ('/', '/auth'):
            self.handle_auth("OK")
        elif self.path == '/charge':
            self.handle_charge()
        elif self.path == self.LOGOUT:
            self.handle_auth()
        self.end_headers()

    def handle_auth(self, auth_val=0) -> None:
        cookie = cookies.SimpleCookie()
        cookie["auth_cookie"] = auth_val
        self.send_header("Set-Cookie", cookie.output(header='', sep=''))

    def handle_charge(self) -> None:
        if not self.headers.get("cookie") or self.headers.get("cookie") != 'auth_cookie=OK':
            self.send_error(403, message="Forbidden")

    def rendering(self) -> None:
        with open(self.path, encoding='UTF-8') as page:
            self.wfile.write(page.read().encode(encoding='UTF-8'))
        return


if __name__ == '__main__':
    my_server = HTTPServer(("", 8001), HttpProcessor)
    try:
        my_server.serve_forever()
    except KeyboardInterrupt:
        my_server.shutdown()
