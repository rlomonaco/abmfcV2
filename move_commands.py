import socket
import zmq
import datetime

class move_commands:

    def __init__(self):
        '''
        established connection from receiving end
        '''
        # connect zmq to publish to bhv_basic_move
        context = zmq.Context()
        self.publisher = context.socket(zmq.PUB)
        address = "tcp://*:5555"
        self.publisher.bind(address)

        # connect zmq to subscribe to read_socket.py
        context = zmq.Context()
        self.subscriber = context.socket(zmq.SUB)
        # self.subscriber.setsockopt(zmq.SNDHWM, 10)
        self.subscriber.connect("tcp://localhost:7777")
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, "")

        self.message = ""

    def receive_py(self):
        '''
        receive message from read_socket.py
        '''
        message = self.subscriber.recv_string()
        return message

    def send_message(self, msg):
        '''
        send commands to bhv files in team_usqrd
        '''
        self.publisher.send_string(msg)

    def main(self):

        self.message = "0 0,0 0,-30 -25,-20 -25,-10 -25,-50 -25,-40 -25,-30 -25,-20 -25,-10 -25,0 -25"

        while True:
            # while (datetime.datetime.now().microsecond - start) < 100:
            # start = datetime.datetime.now().microsecond
            self.message = sc.receive_py()
            # print(datetime.datetime.now().microsecond - start)
                # self.message = message
                # print("received: "+self.message)
            self.send_message(self.message)
            # print("sent: " + self.message)
            start = datetime.datetime.now()
            # if len(self.message)<1:
            #     break

if __name__ == "__main__":

    sc = move_commands()
    sc.main()
    # import time
    # message = " "
    # msg = 1
    # while len(message) > 0:
    #     # start = datetime.datetime.now()
    #     # message = sc.receive_py()
    #     # print(datetime.datetime.now()-start)
    #     print(msg)
    #     sc.send_message(str(msg))
    #     msg+=1
    #     time.sleep(1)




    print('done')