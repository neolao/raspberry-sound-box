from BaseHTTPServer import BaseHTTPRequestHandler

import urlparse, json

class GetHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write('Sound Box')
        return

    def do_POST(self):
        content_len = int(self.headers.getheader('content-length'))
        post_body = self.rfile.read(content_len)
        self.send_response(200)
        self.end_headers()

        data = json.loads(post_body)
        print data

        self.wfile.write('ok')
        return

if __name__ == '__main__':
    from BaseHTTPServer import HTTPServer
    server = HTTPServer(('', 8080), GetHandler)
    print 'Starting server on port 8080'
    server.serve_forever()
