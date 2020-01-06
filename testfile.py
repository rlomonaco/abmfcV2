import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 8888)
# print (>>sys.stderr, 'starting up on %s port %s' % server_address)
sock.connect(server_address)
message = " "
while len(message) > 0:
    message = sock.recv(1024).decode("utf-8")
    print(message)

print('done')