import os
import cgi
import datetime
import argparse
import decimal

from http import cookies
from http.server import (BaseHTTPRequestHandler,
                         HTTPServer)


SERVER_ADDRESSES = {1: '127.0.0.1:8001', 2: '0.0.0.0:8002'}


class HttpProcessor(BaseHTTPRequestHandler):
    # list of allowed urls
    URLS = {
        'HOME': '/',
        'AUTH': '/auth',
        'FORM': '/form',
        'CHARGE': '/charge',
        'LOGOUT': '/out',
    }

    # connect url and html file in the PC
    DEFAULT_ROUTING = {
        URLS['HOME']: '/'.join([os.getcwd(), 'auth.html']),
        URLS['AUTH']: '/'.join([os.getcwd(), 'auth.html']),
        URLS['FORM']: '/'.join([os.getcwd(), 'form.html']),
        URLS['CHARGE']: '/'.join([os.getcwd(), 'charge.html']),
        URLS['LOGOUT']: '/'.join([os.getcwd(), 'auth.html']),
    }

    LIST_OF_POST_METHOD_PAGES = [URLS['CHARGE']]

    def __init__(self, *args, **kwargs):
        self.file_path = ''
        super().__init__(*args, **kwargs)

    def do_GET(self) -> None:
        self.verify_url()
        self.file_path = self.DEFAULT_ROUTING[self.path]
        self.check_file_existence()
        payload = self.context()
        data = self.rendering_with_params(**payload)
        self.send_response(200, message='OK')
        self.fill_header()
        self.wfile.write(data.encode(encoding="UTF-8"))

    def do_POST(self) -> None:
        self.verify_url()
        if self.path in self.LIST_OF_POST_METHOD_PAGES:
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )
            form_data = ''
            payload = {}
            self.file_path = self.DEFAULT_ROUTING[self.path]
            self.check_file_existence()
            if self.path == self.URLS['CHARGE']:
                form_data = self.process_charge_data(form)
                payload = {
                    '{purchase}': form_data,
                }
            payload = self.context(**payload)
            data = self.rendering_with_params(**payload)
            self.send_response(200, message='OK')
            self.fill_header()
            self.wfile.write(data.encode(encoding="UTF-8"))
        else:
            self.send_error(404, message="Such page is not presented")

    def verify_url(self) -> None:
        """check if the page is presented"""
        if self.path not in self.DEFAULT_ROUTING:
            self.send_error(404, message="Such page is not presented")

    def check_file_existence(self) -> None:
        """Check if file exists in a dirictory"""
        if not os.path.exists(self.file_path):
            self.send_error(500, message="File was removed")

    def fill_header(self) -> None:
        """
        add or delete cookies when login or logout page is chosen
        check if cookies are presented to get access to charge page
        """
        self.send_header('content-type', 'text/html')
        if self.path in (self.URLS['HOME'], self.URLS['AUTH']):
            self.handle_auth("OK")
        elif self.path == self.URLS['CHARGE']:
            self.handle_charge_access()
        elif self.path == self.URLS['LOGOUT']:
            self.handle_auth()
        self.end_headers()

    def handle_auth(self, auth_val=0) -> None:
        """set or delete cookie"""
        cookie = cookies.SimpleCookie()
        cookie["auth_cookie"] = auth_val
        if not auth_val:
            expires = datetime.datetime(1970, 1, 1, 0, 0, 0)
            cookie["auth_cookie"]["expires"] = expires.strftime('%a, %d %b %Y %H:%M:%S')
        self.send_header("Set-Cookie", cookie.output(header='', sep=''))

    def handle_charge_access(self) -> None:
        """check cookie"""
        if not self.headers.get("cookie") or self.headers.get("cookie") != 'auth_cookie=OK':
            self.send_error(401, message="Please, log in")

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

    def context(self, **kwargs) -> dict:
        """create full dict of values to change in html"""
        default = {
            '{server_a}': SERVER_ADDRESSES[1],
            '{server_b}': SERVER_ADDRESSES[2],
        }
        for key, value in kwargs.items():
            default[key] = value
        return default

    def rendering_with_params(self, **kwargs) -> str:
        """rendering page with parameters (like Jinja)"""
        with open(self.file_path, encoding='UTF-8') as page:
            full_data = []
            for line in page:
                for key, value in kwargs.items():
                    if line.find(key) != -1:
                        line = line.replace(key, value)
                full_data.append(line)
        data = ''.join(full_data)
        if not data:
            self.send_error(400, message='Somwthing wrong with sent data')
        return data


def init_parser():
    """parser to run servers using one script"""
    parser = argparse.ArgumentParser(
        prog="Server",
        prefix_chars='-',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Program to work with simple server")
    parser.add_argument(
        "serverA",
        nargs='?',
        type=str)
    parser.add_argument(
        "serverB",
        nargs='?',
        type=str)
    parser.add_argument(
        "-r", "--reverse",
        action="store_true",
        default=False,
        help="Reverse both servers' ips"
    )
    return parser


if __name__ == '__main__':
    parser = init_parser()
    args = parser.parse_args()
    if args.reverse:
        SERVER_ADDRESSES[1], SERVER_ADDRESSES[2] = SERVER_ADDRESSES[2], SERVER_ADDRESSES[1]
    else:
        if args.serverA:
            SERVER_ADDRESSES[1] = args.serverA
        if args.serverB:
            SERVER_ADDRESSES[2] = args.serverB
    print(f'Your server addresses are: {SERVER_ADDRESSES[1]} and {SERVER_ADDRESSES[2]}')
    server_config = SERVER_ADDRESSES[1]
    server_addr, server_port = server_config.split(':')
    my_server = HTTPServer((server_addr, int(server_port)), HttpProcessor)
    try:
        my_server.serve_forever()
    except KeyboardInterrupt:
        my_server.shutdown()
