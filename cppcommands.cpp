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

    //  Socket to receive messages on
    zmq::socket_t subscriber (context, ZMQ_SUB);
    subscriber.setsockopt(ZMQ_SUBSCRIBE, "", 0);
    subscriber.connect("tcp://localhost:7777");

    //  Socket to send messages to
    zmq::socket_t publisher(context, ZMQ_PUB);
    publisher.bind("tcp://*:5555");

    // initialise vector of strings
    std::vector<std::string> values;
    zmq::message_t first_message;
    subscriber.recv(&first_message);
    std::string first;
    first.assign(static_cast<char *>(first_message.data()), first_message.size());
    values.push_back(first);

    while (1) {

        zmq::message_t message;
        bool rc;

        // if received send new string
        if((rc = subscriber.recv(&message, ZMQ_DONTWAIT))==true)
        {
                publisher.send(message);
                std::string update_string;
                update_string.assign(static_cast<char*>(message.data()), message.size());

                // save new string into vector
                // when not received update_string becomes size32 empty characters so only save when not that
                if (sizeof(update_string)!=32)
                {
                    values.push_back(update_string);
                }
                std::cout<<"yes"<<std::endl;

        }
        else
        {

                std::string saved_message;
                saved_message = values.back();
                zmq::message_t reply (saved_message.size());
                memcpy (reply.data (), saved_message.c_str(), saved_message.size());
                publisher.send(reply);

        }


    }
    return 0;
}