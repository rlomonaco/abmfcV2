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
socket.bind("tcp://*:8889")

while True:
    message = socket.send_string("yo")
    # print("received: "+ message)
    # sleep(5)
