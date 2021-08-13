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
        data = raw_body.decode('utf-8')
        print(data)

        _self.protocol_version = 'HTTP/1.1'
        _self.send_response(200)
        _self.send_header("Content-type", "text/plain")
        _self.end_headers()
        _self.wfile.write(data.encode("utf-8"))


with socketserver.TCPServer(("", 8000), ServerHandler) as httpd:
    print("serving at port", 8000)
    httpd.serve_forever()
