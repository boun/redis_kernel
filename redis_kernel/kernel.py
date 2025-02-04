from __future__ import print_function

import socket

from .parser import RedisParser
from .constants import *
import sys
from metakernel import MetaKernel as Kernel

try:
    # check if we have defined these variables, if not default
    from redis_kernel_config import *
    if 'PORT' not in locals() and 'PORT' not in globals():
        PORT = None
    if 'HOST' not in locals() and 'HOST' not in globals():
        HOST = None
except:
    # if the config isnt found at all
    HOST = None
    PORT = None
    HISTORY_DB = None


class RedisKernel(Kernel):
    # these are required for the kernel to identify itself
    implementation = NAME
    implementation_version = VERSION
    language = LANGUAGE

    # the database connection
    redis_socket = None
    connected = False

    # required for the kernel
    @property
    def language_version(self):
        return VERSION

    @property
    def banner(self):
        return BANNER
        
    language_info = {
        'name': NAME,
        'version': VERSION,
        'mimetype': 'text',
        'file_extension': '.txt',
    }

    # handle all init logic here
    def __init__(self, **kwargs):
        Kernel.__init__(self, **kwargs)
        self.start_redis(**kwargs)
        self.get_commands()

    def start_redis(self, **kwargs):
        if self.redis_socket is None:
            host = HOST or DEFAULT_HOST
            port = PORT or DEFAULT_PORT
            # loop through all connection options
            for res in socket.getaddrinfo(host, port):
                try:
                    family, stype, protocol, name, address = res
                    sock = socket.socket(family, stype, protocol)
                    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    sock.connect(address)
                    # just half a second timeout
                    sock.settimeout(0.25)
                    self.redis_socket = sock
                    self.connected = True
                    # and return on the first successful one
                    return
                except:
                    self.connected = False
                    if sock is not None:
                        sock.close()

    def recv_all(self):
        total_data = []
        while True:
            try:
                data = self.redis_socket.recv(1024)
            except socket.timeout:
                # sink any timeout here
                break
            if data is None:
                break
            total_data.append(data)
        return ''.encode('utf-8').join(total_data)

    def get_commands(self):
        if self.connected:
            self.commands = RedisParser('')
            try:
                self.redis_socket.send('command count\r\n'.encode('utf-8'))
                count_response = self.recv_all()
                self.command_count = RedisParser(
                    count_response.decode('utf-8'))
                self.redis_socket.send('command\r\n'.encode('utf-8'))
                response = self.recv_all()
                self.commands = RedisParser(response.decode('utf-8'), True)
            except:
                pass
                # print(sys.exc_info()[0])
                # traceback.print_tb(sys.exc_info()[2])
                #self.commands = []

    # the core of the kernel where the work happens
    def do_execute_direct(self, code):
        if not code.strip():
            # we got blank code
            return

        if not self.connected:
            self.Error("Not Connected");
            return

        # check and fix CRLF before we do anything
        code = self.validate_and_fix_code_crlf(code)
        # print code
        data = None
        try:
            # execute the code and get the result
            self.redis_socket.send(code.encode('utf-8'))
            response = self.recv_all()
            data = RedisParser(response.decode('utf-8'))
        except:
            self.Error({'status': 'error',
                    'ename': '',
                    'error': 'Error executing code ' + str(sys.exc_info()[0]),
                    'traceback': 'Error executing code ' + str(sys.exc_info()[0]),
                    })
            return

        # using display data instead allows to show html
        #stream_content = {'name': 'stdout', 'text':data._repr_text_()}
        #self.send_response(self.iopub_socket, 'stream', stream_content)

        display_content = {
            'source': 'kernel',
            'data': {
                'text/plain': data._repr_text_(),
                'text/html': data._repr_html_()
            }, 'metadata': {}
        }

        self.send_response(
            self.iopub_socket, 'display_data', display_content)

        return

    def do_shutdown(self, restart):
        if self.redis_socket is not None:
            try:
                self.redis_socket.close()
            except:
                pass

    def do_is_complete(self, code):
        # for now always return true - need to add something here
        # later if we decide not to send multi to redis immediately
        return True

    def do_complete(self, code, cursor_pos):
        options = []
        for command in self.commands.result:
            if command.startswith(code):
                options.append(command)

        return {
            'matches': options,
            'metadata': {},
            'status': 'ok',
            'cursor_start': 0,
            'cursor_end': len(code)
        }

    def validate_and_fix_code_crlf(self, code):
        if not (code[-2:] == '\r\n'):
            code = code.strip() + '\r\n'
        return code
