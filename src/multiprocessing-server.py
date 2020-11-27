import sys
import traceback
import socket
from http.server import BaseHTTPRequestHandler
from multiprocessing import Pool


TEMPLATE_RESPONSE = """\
<html>
    <head>
        <title>Multi-Tasking Server</title>
    </head>
    <body>
        <h1>Response for path : %(path)s</h1>
    </body>
</html>
"""


class SingleTaskRequestHandler(BaseHTTPRequestHandler):
    
    def __init__(self, socket_client, socket_addr):
        self.client = socket_client
        super().__init__(socket_client, socket_addr, None)

    def do_GET(self) -> None:
        try:
            # print("Worker : processing ", self.path)
            if (self.path.startswith("/favicon.ico")):
                self.send_response(404)
                self.end_headers()
            else:
                msg = (TEMPLATE_RESPONSE % {
                    'path': self.path
                })
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(bytes(msg, "utf-8"))

            return

        except Exception as e:
            print(e)


def worker(socket_client, socket_addr) -> None:
    SingleTaskRequestHandler(socket_client, socket_addr)
    socket_client.close()
    return


def serve():
    address = ''
    port = 8000

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', port))

    print('Listening on address %s and port %d' % (address, port))
    # backlog connection queue on server port
    s.listen(1000)

    try:
        # start worker pool
        worker_pool = Pool(processes=5)

        while True:
            try:
                s_sock, s_addr = s.accept()

                # worker(s_sock, s_addr)
                worker_pool.apply_async(worker, (s_sock, s_addr,))

            except socket.error:
                # stop the client disconnect from killing us
                print(socket.error)

    except Exception as e:
        print(e)
        traceback.print_exc()
        sys.exit(1)
    finally:
        s.close()


if __name__ == '__main__':
    serve()
