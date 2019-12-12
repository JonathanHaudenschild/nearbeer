from http.server import HTTPServer, BaseHTTPRequestHandler
import get_keywords_polarity
from io import BytesIO
import json


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello, world!')

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        body_decode = body.decode('utf-8').replace("'", '"')
        data = json.loads(body_decode)
        #data_json = json.dumps(data)
        keywords_pol = get_keywords_polarity.get_keywords_polarity(data["barname"])
        encode_keywords_pol = json.dumps(keywords_pol, indent=2).encode('utf-8')
        self.send_response(200)
        self.end_headers()
        response = BytesIO()
        response.write(encode_keywords_pol)
        self.wfile.write(response.getvalue())


httpd = HTTPServer(('localhost', 8000), SimpleHTTPRequestHandler)
print("Starting...")
httpd.serve_forever()