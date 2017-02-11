# Keep coding and change the world..And do not forget anything..Not Again..
import json
import cPickle
import socket
import threading


class Connection(object):
    def __init__(self, digit=30):
        self.max_digit = digit

    def send_fragments(self, client, msg):
        l = len(msg)
        client.send(str(l).rjust(self.max_digit, '0'))
        client.send(msg)
        # print msg, 'sent to', client


class Server(Connection):
    def __init__(self, **kwargs):
        super(Server, self).__init__(**kwargs)
        self.connections = {}
        self.host_name = '0.0.0.0'  # socket.gethostname()
        self.port_no = 1239
        self.server = None
        print self.host_name, self.port_no
        # quit()

    def add_to_connections(self, client):
        num_len = int(client.recv(self.max_digit))
        number = client.recv(num_len)
        if number not in self.connections:
            self.connections[number] = client
            self.send_list_to_all()
            return number
        return None

    def send_list_to_all(self):
        # print self.connections
        connection_list = cPickle.dumps(self.connections.keys())
        # print connection_list
        for client in self.connections.values():
            self.send_fragments(client, '-1')
            self.send_fragments(client, connection_list)

    def start_server(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host_name, self.port_no))
        self.server.listen(300)
        print 'Server Started'
        while True:
            client, address = self.server.accept()
            mob_number = self.add_to_connections(client)
            print 'New connection', mob_number
            if mob_number:
                threading.Thread(target=self.connect_clients, args=(client, mob_number,)).start()
            else:
                client.close()
                # print self.connections

    def connect_clients(self, client, sender):
        cnt = 5
        while True:
            try:
                # sen_len = int(client.recv(self.max_digit))
                # sender = client.recv(sen_len)
                rec_len = int(client.recv(self.max_digit))
                receiver = client.recv(rec_len)
                msg_len = int(client.recv(self.max_digit))
                msg = client.recv(msg_len)
                # print receiver, msg
                # print self.connections
                self.send_fragments(self.connections[receiver], sender)
                self.send_fragments(self.connections[receiver], msg)
                cnt = 5
            except Exception as e:
                cnt -= 1
                if not cnt:
                    # print "Error :", e
                    for name in self.connections:
                        if self.connections[name] == client:
                            self.connections.pop(name)
                            print 'Connection lost with', name
                            self.send_list_to_all()
                            break
                    break


if __name__ == '__main__':
    s = Server()
    s.start_server()
