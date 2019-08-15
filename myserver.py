import os
import cgi
import datetime

from http import cookies
from http.server import (BaseHTTPRequestHandler,
                         HTTPServer)


class HttpProcessor(BaseHTTPRequestHandler):
    LOGOUT = '/out'
    DEFAULT_ROUTING = {
        '/': os.path.join(os.getcwd(), 'auth.html'),
        '/auth': os.path.join(os.getcwd(), 'auth.html'),
        '/form': os.path.join(os.getcwd(), 'form.html'),
        '/charge': os.path.join(os.getcwd(), 'charge.html'),
        LOGOUT: os.path.join(os.getcwd(), 'auth.html'),
    }

    def do_GET(self):
        self.verify_url()
        self.file_path = self.DEFAULT_ROUTING[self.path]
        if os.path.exists(self.file_path):
            self.send_response(200)
            self.fill_header()
            self.rendering()
        self.send_error(500)

    def do_POST(self):
        self.verify_url()
        if self.path == '/charge':
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )
            purchase = form.getvalue("purchase")
            if purchase is None:
                self.send_error(400)
            try:
                int(purchase)
            except ValueError:
                try:
                    float(purchase)
                except ValueError:
                    self.send_error(400)
            self.file_path = self.DEFAULT_ROUTING[self.path]
            if not os.path.exists(self.file_path):
                self.send_error(500)
            with open(self.file_path, encoding='UTF-8') as page:
                data = page.read()
                data = data.format(purchase=purchase)
            self.send_response(200)
            self.fill_header()
            self.wfile.write(data.encode(encoding="UTF-8"))
        else:
            self.send_error(404)

    def verify_url(self):
        if self.path not in self.DEFAULT_ROUTING:
            self.send_error(404, message="Page Not Found")

    def fill_header(self):
        self.send_header('content-type', 'text/html')
        if self.path in ('/', '/auth'):
            self.handle_auth("OK")
        elif self.path == '/charge':
            self.handle_charge_access()
        elif self.path == self.LOGOUT:
            self.handle_auth()
        self.end_headers()

    def handle_auth(self, auth_val=0):
        cookie = cookies.SimpleCookie()
        cookie["auth_cookie"] = auth_val
        if not auth_val:
            expires = datetime.datetime(1970, 1, 1, 0, 0, 0)
            cookie["auth_cookie"]["expires"] = expires.strftime('%a, %d %b %Y %H:%M:%S')
        self.send_header("Set-Cookie", cookie.output(header='', sep=''))

    def handle_charge_access(self):
        if not self.headers.get("cookie") or self.headers.get("cookie") != 'auth_cookie=OK':
            self.send_error(401, message="Forbidden")

    def rendering(self):
        with open(self.file_path, encoding='UTF-8') as page:
            self.wfile.write(page.read().encode(encoding='UTF-8'))


if __name__ == '__main__':
    my_server = HTTPServer(("", 8001), HttpProcessor)
    try:
        my_server.serve_forever()
    except KeyboardInterrupt:
        my_server.shutdown()
