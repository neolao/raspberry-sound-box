import http.server
import socketserver
import json

class ServerHandler(http.server.SimpleHTTPRequestHandler):

    def do_GET(_self):
        _self.protocol_version = 'HTTP/1.1'
        #self._headers = _self.headers
        #self._url = _self.path
        _self.send_response(200)
        _self.send_header("Content-type", "application/json")
        _self.end_headers()
        _self.wfile.write(b"{}")

    def do_POST(_self):
        content_len = int(_self.headers.get("Content-Length"), 0)
        raw_body = _self.rfile.read(content_len)

        #data = json.load(raw_body)
        print(raw_body)

        _self.protocol_version = 'HTTP/1.1'
        _self.send_response(200)
        _self.send_header("Content-type", "application/json")
        _self.end_headers()
        _self.wfile.write(b"{}")


with socketserver.TCPServer(("", 8080), ServerHandler) as httpd:
    print("serving at port", 8080)
    httpd.serve_forever()
