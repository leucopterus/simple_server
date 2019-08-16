import os
import cgi
import datetime
import decimal

from http import cookies
from http.server import (BaseHTTPRequestHandler,
                         HTTPServer)


class HttpProcessor(BaseHTTPRequestHandler):

    LOGOUT = '/out'
    CHARGE = '/charge'
    FORM = '/form'
    HOME = '/'
    AUTH = '/auth'

    LIST_OF_POST_METHOD_PAGES = [CHARGE]

    DEFAULT_ROUTING = {
        HOME: os.path.join(os.getcwd(), 'auth.html'),
        AUTH: os.path.join(os.getcwd(), 'auth.html'),
        FORM: os.path.join(os.getcwd(), 'form.html'),
        CHARGE: os.path.join(os.getcwd(), 'charge.html'),
        LOGOUT: os.path.join(os.getcwd(), 'auth.html'),
    }

    def do_GET(self) -> None:
        """GET method implementation"""
        self.verify_url()
        self.file_path = self.DEFAULT_ROUTING[self.path]
        self.check_file_existence()
        self.send_response(200)
        self.fill_header()
        self.rendering()

    def do_POST(self) -> None:
        """POST method implementation"""
        self.verify_url()
        if self.path in self.LIST_OF_POST_METHOD_PAGES:
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )
            form_data = ''
            html_page = ''
            if self.path == self.CHARGE:
                form_data = self.process_charge_data(form)
            self.file_path = self.DEFAULT_ROUTING[self.path]
            self.check_file_existence()
            if self.path == self.CHARGE:
                html_page = self.rendering_charge(form_data)
            self.send_response(200)
            self.fill_header()
            self.wfile.write(html_page.encode(encoding="UTF-8"))
        else:
            self.send_error(404, message="Page Not Found")

    def verify_url(self) -> None:
        """Check if page on server is presented"""
        if self.path not in self.DEFAULT_ROUTING:
            self.send_error(404, message="Page Not Found")

    def check_file_existence(self) -> None:
        """Check is file in a dirictory"""
        if not os.path.exists(self.file_path):
            self.send_error(500)

    def fill_header(self) -> None:
        """Fill out response header"""
        self.send_header('content-type', 'text/html')
        if self.path in ('/', '/auth'):
            self.handle_auth("OK")
        elif self.path == '/charge':
            self.handle_charge_access()
        elif self.path == self.LOGOUT:
            self.handle_auth()
        self.end_headers()

    def handle_auth(self, auth_val=0) -> None:
        """Set or delete cookie for auth page"""
        cookie = cookies.SimpleCookie()
        cookie["auth_cookie"] = auth_val
        if not auth_val:
            expires = datetime.datetime(1970, 1, 1, 0, 0, 0)
            cookie["auth_cookie"]["expires"] = expires.strftime('%a, %d %b %Y %H:%M:%S')
        self.send_header("Set-Cookie", cookie.output(header='', sep=''))

    def handle_charge_access(self) -> None:
        """Check cookie to access the charge page"""
        if not self.headers.get("cookie") or self.headers.get("cookie") != 'auth_cookie=OK':
            self.send_error(401, message="Forbidden")

    def process_charge_data(self, form) -> str:
        """Collect date out of form"""
        purchase = form.getvalue("purchase")
        if purchase is None:
            self.send_error(400, message='invalid sum value, should be number')
        try:
            decimal.Decimal(purchase)
        except decimal.InvalidOperation:
            self.send_error(400, message='invalid sum value, should be number')
        return purchase

    def rendering(self) -> None:
        """Collect data from html file without parameters"""
        with open(self.file_path, encoding='UTF-8') as page:
            self.wfile.write(page.read().encode(encoding='UTF-8'))

    def rendering_charge(self, purchase) -> str:
        """Collect data from html file with parameters"""
        with open(self.file_path, encoding='UTF-8') as page:
            data = page.read()
            data = data.format(purchase=purchase)
        return data


if __name__ == '__main__':
    my_server = HTTPServer(("", 8001), HttpProcessor)
    try:
        my_server.serve_forever()
    except KeyboardInterrupt:
        my_server.shutdown()
