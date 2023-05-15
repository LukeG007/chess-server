import cmd_mgmt
import proc_mgmt
import os
import base64
import json

cmd = cmd_mgmt.CommandMGMT()
vnc_list_f = open('vnc_list.json')
vnc_list = json.loads(vnc_list_f.read())
vnc_list_f.close()
proc = proc_mgmt.ProcessMGMT(vnc_list)

def add_vnc_callback(novnc_port, vnc_port, password):
    vnc_list_f = open('vnc_list.json', 'w')
    plaintext_pass = base64.b64decode(password.encode()).decode('utf-8')
    os.system('echo "{}" | vncpasswd -f > password_files/passwd{}'.format(password.replace('"', '\\"'), vnc_port))
    vnc_list[vnc_port] = {
        'novnc_port': novnc_port,
        'password_file': 'password_files/passwd{}'.format(vnc_port)
    }
    vnc_list_f.write(json.dumps(vnc_list), indent=4)
    vnc_list_f.close()
    proc.vnc_list = vnc_list
    proc.start_vnc(vnc_port)

def restart_vnc_callback(vnc_port):
    try:
        proc.restart_vnc(vnc_port)
    except Exception as e:
        return str(e)

cmd.add_vnc_callback = add_vnc_callback
cmd.restart_vnc_callback = restart_vnc_callback

cmd.serve()
