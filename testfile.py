import socket
import zmq

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 8889)
sock.connect(server_address)

socket_list = []
for i in range(11):
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://*:5555")



message = " "
while len(message) > 0:
    # message = sock.recv(1024).decode("utf-8")
    # print(message)
    # sock2.send(bytes("2", "utf8"))
    msg = "-50"
    socket.send_string(msg)
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