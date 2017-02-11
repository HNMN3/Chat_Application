# Keep coding and change the world..And do not forget anything..Not Again..
import pickle
import socket
import threading

import cPickle

import time


class Connection(object):
    def __init__(self, digit=30, *args, **kwargs):
        self.max_digit = digit

    def send_fragments(self, client, msg):
        l = len(msg)
        try:
            client.send(str(l).rjust(self.max_digit, '0'))
            client.send(msg)
            return False
        except:
            print 'Connection Error'
            return True


class Client(Connection):
    def __init__(self, *args, **kwargs):
        self.window = kwargs.pop('window', None)
        self.number = kwargs.pop('number', socket.gethostname())
        super(Client, self).__init__(*args, **kwargs)
        self.server_name = 'HNMN3s-PC'
        self.server_port = 1239
        self.me = None
        self.other_connections = {}

    def introduce_yourself(self):
        self.send_fragments(self.me, self.number)

    def update_list(self):
        while True:
            try:
                data_len = int(self.me.recv(self.max_digit)[:self.max_digit])
                break
            except:
                continue
        connections = self.me.recv(data_len)
        self.other_connections = cPickle.loads(connections)
        print 'List updated to', self.other_connections
        while not self.window.root_window:
            continue
        self.window.root_window.children[0].screens[0].ids['friends_list'].adapter.data = self.other_connections

    def connect(self):
        while True:
            try:
                self.me = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.me.connect((self.server_name,
                                 self.server_port))
                break
            except:
                time.sleep(3)
                continue

        # print socket.gethostname()
        self.introduce_yourself()
        # threading.Thread(target=self.send_msg, args=('sample_number',)).start()
        print 'connected'
        self.receive_msg()

    def send_msg(self, receiver, msg):
        # self.send_fragments(self.me, self.number)
        x = self.send_fragments(self.me, receiver)
        y = self.send_fragments(self.me, msg)
        if x or y:
            threading.Thread(target=self.connect).start()

    def receive_msg(self):
        cnt = 5
        while True:
            try:
                try:
                    add_len = int(self.me.recv(self.max_digit)[:self.max_digit])
                except:
                    continue
                sender = self.me.recv(add_len)
                if sender == '-1':
                    # print msg
                    # threading.Thread(target=self.update_list).start()
                    self.update_list()
                    continue
                msg_len = int(self.me.recv(self.max_digit)[:self.max_digit])
                msg = self.me.recv(msg_len)
                # print address, 'sent', msg
                while not self.window.root_window:
                    continue
                sender_screen = self.window.root_window.children[0].screen_instance[sender]
                sender_screen.receive_message(msg)
                sender_screen.update_height()
                cnt = 5
            except Exception as e:
                print e
                cnt -= 1
                if not cnt:
                    break


if __name__ == '__main__':
    c = Client()
    c.connect()
