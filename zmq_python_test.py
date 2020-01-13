#import zmq
#
# context = zmq.Context()
# socket = context.socket(zmq.PUB)
# context = zmq.Context()
# socket = context.socket(zmq.PUB)
# socket.bind("tcp://*:4004")
# while True:
#   command = input("insert command ")
#   if (command=='c'):
#         topic = "CALL".encode("ascii")
#         data = "blabla".encode("ascii")
#         socket.send_multipart([topic,data])

# ========================================================================================================

import zmq
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:6666")

while True:
    msg = "hello"
    socket.send_string(msg)
    # print("sent "+ msg)
    # sleep(5)
