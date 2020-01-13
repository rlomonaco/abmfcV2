import socket
import zmq

class send_commands:

    def __init__(self):
        '''
        established connection from receiving end
        '''
        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('localhost', 8889)
        self.sock.connect(server_address)

        # connect zmq socket
        context = zmq.Context()
        self.socket = context.socket(zmq.PUB)
        socket_address = "tcp://*:5555"
        self.socket.bind(socket_address)


    def send_message(self, msg):
        '''
        send commands to bhv files in team_usqrd
        '''
        # socket_list = []
        # for i in range(11):
        #     context = zmq.Context()
        #     socket = context.socket(zmq.PUB)
        #     socket_address = "tcp://*:555{}".format(str(i))
        #     socket.bind(socket_address)
        #     socket_list.append(socket)

        self.socket.send_string(msg)

if __name__ == "__main__":

    sc = send_commands()

    message = " "
    # msg = "-50, -40, -30, -20, -10, -50, -40, -30, -20, -10, 0"
    msg = "-50"
    while len(message) > 0:
        # message = self.sock.recv(1024).decode("utf-8")
        # print(message)
        # for i in range(11):
        sc.send_message(msg)
        # print("sent "+ msg)





#
# sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server_address2 = ('localhost', 7778)
# sock2.connect(server_address2)
# message = " "
# while len(message) > 0:
#     message = sock2.recv(1024).decode("utf-8")
#     print(message)
#
#





print('done')