import subprocess
import json
import os
import time

class VNCNotFound(Exception):
    pass

class VNCAlreadyRunning(Exception):
    pass

class VNCAlreadyStopped(Exception):
    pass

class ProcessMGMT:
    def __init__(self, vnc_list):
        self.vnc_list = vnc_list
        self.vnc_process_list = {}
        config = open('config.json')
        self.config = json.loads(config.read())
        config.close()
        for vnc in self.vnc_list:
            self.start_vnc(vnc)
    def start_vnc(self, vnc_port):
        if vnc_port in self.vnc_process_list:
            raise VNCAlreadyRunning('VNC server is already running.')
        elif not vnc_port in self.vnc_list:
            raise VNCNotFound('VNC server does not exist.')
        else:
            novnc_process = subprocess.Popen([self.config['novnc'] + 'utils/novnc_proxy', '--listen', self.vnc_list[vnc_port]['novnc_port'], '--vnc', 'localhost:59' + vnc_port])
            vnc_process = subprocess.Popen(['Xvnc', ':' + vnc_port, '-rfbauth', os.getcwd() + '/' + self.vnc_list[vnc_port]['password_file']])
            env = os.environ.copy()
            env['DISPLAY'] = ':' + vnc_port
            time.sleep(0.05)
            chromium_process = subprocess.Popen(['chromium', '--profile-directory={}'.format(vnc_port), '--user-data-dir=$HOME/instances/{}'.format(vnc_port), '--kiosk', 'https://chess.com'], env=env)
            self.vnc_process_list[vnc_port] = [
                novnc_process,
                vnc_process,
                chromium_process
            ]
    def stop_vnc(self, vnc_port):
        if not vnc_port in self.vnc_process_list:
            raise VNCAlreadyStopped('VNC server is already stopped.')
        elif not vnc_port in self.vnc_list:
            raise VNCNotFound('VNC server does not exist.')
        else:
            for process in self.vnc_process_list[vnc_port]:
                process.kill()
            del self.vnc_process_list[vnc_port]
    def restart_vnc(self):
        try:
            self.stop_vnc(vnc_port)
        except VNCAlreadyStopped:
            pass
        else:
            self.start_vnc(vnc_port)
