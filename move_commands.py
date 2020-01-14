import socket
import zmq

class move_commands:

    def __init__(self):
        '''
        established connection from receiving end
        '''
        # # Create a TCP/IP socket
        # self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # server_address = ('localhost', 8889)
        # self.sock.connect(server_address)

        # connect zmq socket
        context = zmq.Context()
        self.socket = context.socket(zmq.PUB)
        socket_address = "tcp://*:5555"
        self.socket.bind(socket_address)


    def send_message(self, msg):
        '''
        send commands to bhv files in team_usqrd
        '''
        self.socket.send_string(msg)

if __name__ == "__main__":

    sc = move_commands()

    message = " "
    msg = "-50,-40,-30,-20,-10,-50,-40,-30,-20,-10,0"
    # msg = "-50"
    while len(message) > 0:
        # message = self.sock.recv(1024).decode("utf-8")
        # print(message)
        sc.send_message(msg)
        # print("sent "+ msg)




print('done')