#include <zmq.hpp>
#include <iostream>
#include <sys/types.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <string.h>

//#include "zhelpers.hpp"
#include <string>

int main (int argc, char *argv[])
{
    zmq::context_t context(1);
//    int conf = 1;
//    int hwm = 10;
    //  Socket to receive messages on
    zmq::socket_t subscriber (context, ZMQ_SUB);
    subscriber.setsockopt(ZMQ_SUBSCRIBE, "", 0);
//    subscriber.setsockopt(ZMQ_CONFLATE, &conf, sizeof(conf));
//    subscriber.setsockopt(ZMQ_RCVHWM, &hwm, sizeof(hwm));
    subscriber.connect("tcp://localhost:7777");


    //  Socket to send messages to
    zmq::context_t context2(1);
    zmq::socket_t publisher(context2, ZMQ_PUB);
    publisher.bind("tcp://*:5555");

//    std::string saved_message;
    std::vector<std::string> values;
    zmq::message_t first_message;
    subscriber.recv(&first_message);
    std::string first;
    first.assign(static_cast<char *>(first_message.data()), first_message.size());
    values.push_back(first);

    while (1) {

        zmq::message_t message;
        bool rc;
        if((rc = subscriber.recv(&message, ZMQ_DONTWAIT))==true){
                publisher.send(message);
//                saved_message = message;
                std::string update_string;
                update_string.assign(static_cast<char*>(message.data()), message.size());
                if (sizeof(update_string)>33){
                    values.push_back(update_string);
                    }
//                std::cout<<sizeof(update_string)<<std::endl;
                                std::cout<<"yes"<<std::endl;

        }
        else
        {
                std::string saved_message;
                saved_message = values.back();
                zmq::message_t reply (saved_message.size());
                memcpy (reply.data (), saved_message.c_str(), saved_message.size());
                publisher.send(reply, ZMQ_NOBLOCK);
//                std::cout<<sizeof(saved_message)<<std::endl;
//                std::cout<<"no"<<std::endl;
        }


    }
    return 0;
}