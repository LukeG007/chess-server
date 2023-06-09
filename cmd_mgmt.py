import socket
import threading
import tabulate

class CommandMGMT:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.add_vnc_callback = lambda novnc_port, vnc_port, password: None
        self.restart_vnc_callback = lambda vnc_port: None
        self.start_vnc_callback = lambda vnc_port: None
        self.stop_vnc_callback = lambda vnc_port: None
        self.list_vnc_callback = lambda: None
    def process_cmd(self, command):
        if command == '':
            return None
        args = command.split(' ')
        if args[0] == 'echo':
            return command[5:]
        elif args[0] == 'help':
            header = ['Syntax', 'Description']
            commands = [
                ['echo <anything after>', 'Repeats command back'],
                ['add_vnc <b64 encoded name> <novnc port> <vnc port> <b64 encoded password>', 'Adds a VNC server'],
                ['start_vnc <vnc port>', 'Starts a VNC server'],
                ['stop_vnc <vnc port>', 'Stops a VNC server'],
                ['list_vncs', 'List all VNC servers'],
                ['restart_vnc <vnc port>', 'Restarts a VNC server']
            ]
            return tabulate.tabulate(commands, headers=header)
        elif args[0] == 'add_vnc':
            return self.add_vnc_callback(args[1], args[2], args[3], args[4])
        elif args[0] == 'stop_vnc':
            return self.stop_vnc_callback(args[1])
        elif args[0] == 'start_vnc':
            return self.start_vnc_callback(args[1])
        elif args[0] == 'list_vncs':
            return self.list_vnc_callback()
        elif args[0] == 'restart_vnc':
            return self.restart_vnc_callback(args[1])
        else:
            return 'Invalid Command'
    def handle_client(self, conn):
        conn.send(b'Chess VNC console\r\n')
        while True:
            conn.send(b': ')
            command = conn.recv(1024)
            if command.endswith(b'\xff\xf4\xff\xfd\x06'):
                conn.close()
                break
            command = command.decode('utf-8').replace('\r', '').replace('\n', '')
            cmd_processed = self.process_cmd(command)
            if not cmd_processed == None:
                conn.send(cmd_processed.encode() + b'\r\n')
    def serve(self):
        self.socket.bind(('0.0.0.0', 1111))
        self.socket.listen()
        while True:
            conn, addr = self.socket.accept()
            threading.Thread(target=self.handle_client, args=(conn,)).start()