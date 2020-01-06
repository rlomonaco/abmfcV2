import socket

class mysocket:

    def __init__(self):
        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('localhost', 8888)
        self.sock.connect(server_address)

    def receive_msg(self):

        # while True:
        message = self.sock.recv(1024).decode("utf-8")
        print(message)
        # self.sock.send(bytes(message, "utf8"))
        return message

    def send_msg(self, msg):
        # message argument has to be in byte

        self.sock.send(bytes(msg, "utf8"))


if __name__ == "__main__":

    s = mysocket()
    message = " "
    while len(message) > 0:
        message = s.receive_msg()
        s.send_msg(message)


    print('done')
