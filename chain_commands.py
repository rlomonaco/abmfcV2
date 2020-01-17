import zmq
import datetime


class chain_commands:

    def __init__(self):
        '''
        established connection from receiving end
        '''

        # connect zmq to publish to bhv_chain_action
        context = zmq.Context()
        self.publisher = context.socket(zmq.PUB)
        address = "tcp://*:6666"
        self.publisher.bind(address)

        # connect zmq to subscribe to read_socket.py
        context = zmq.Context()
        self.subscriber = context.socket(zmq.SUB)
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, "")
        self.subscriber.connect("tcp://localhost:9999")

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

        self.message = "10,2,-50,0"  # player_num, action(pass), x, y

        start = datetime.datetime.now().microsecond
        while True:
            # while (datetime.datetime.now().microsecond - start) < 100:
            self.message = sc.receive_py()
            # self.message = message
                # print("received: "+self.message)

            self.send_message(self.message)
            # print("sent: " + self.message)
            # start = datetime.datetime.now()

            # if len(self.message)<1:
            #     break

if __name__ == "__main__":

    sc = chain_commands()
    sc.main()


    print('done')