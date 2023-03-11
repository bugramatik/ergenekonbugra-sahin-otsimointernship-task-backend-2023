from http.server import HTTPServer
import socket
from api.main_code import SimpleHTTPRequestHandler
#TODO: Error handling
 
def run():
    host = ''
    port = 8080
    server_address = (host, port)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    httpd.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # SO_REUSEADDR for releasing TCP port after closing program
    print(f"Server running on http://{host}:{port}")
    httpd.serve_forever()

if __name__ == '__main__':
    run()

