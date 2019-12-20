# import socket
#
# class mysocket:
#     '''demonstration class only
#       - coded for clarity, not efficiency
#     '''
#
#     def __init__(self, sock=None):
#         if sock is None:
#             self.sock = socket.socket(
#                 socket.AF_INET, socket.SOCK_STREAM)
#         else:
#             self.sock = sock
#
#     def connect(self, host, port):
#         self.sock.connect((host, port))
#
#     def mysend(self, msg):
#         totalsent = 0
#         while totalsent < MSGLEN:
#             sent = self.sock.send(msg[totalsent:])
#             if sent == 0:
#                 raise RuntimeError("socket connection broken")
#             totalsent = totalsent + sent
#
#     def myreceive(self):
#         chunks = []
#         bytes_recd = 0
#         while bytes_recd < MSGLEN:
#             chunk = self.sock.recv(min(MSGLEN - bytes_recd, 2048))
#             if chunk == '':
#                 raise RuntimeError("socket connection broken")
#             chunks.append(chunk)
#             bytes_recd = bytes_recd + len(chunk)
#         return ''.join(chunks)
#
# if __name__ == "__main__":
#
#     # s = mysocket(sock=None)
#     # s.connect('localhost', 37988)
#     # s.myreceive()


import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 8888)
# print (>>sys.stderr, 'starting up on %s port %s' % server_address)
sock.connect(server_address)
sock.send(b"fuckyou")