#include <zmq.hpp>
#include <iostream>
//#include <unistd.h>
#include <string>


//#include "zhelpers.hpp"
//#include <string>

int main ()
{
    zmq::context_t context(1);
    // int conf = 1;
    // int timeout = 100;

    //  Socket to receive messages on
    zmq::socket_t subscriber (context, ZMQ_SUB);
    // subscriber.setsockopt(ZMQ_RCVTIMEO, &timeout, sizeof (timeout));
    subscriber.setsockopt(ZMQ_SUBSCRIBE, "", 0);
    // subscriber.setsockopt(ZMQ_CONFLATE, &conf, sizeof(conf));
    subscriber.connect("tcp://localhost:6666");

    //  Socket to send messages to
    zmq::socket_t publisher(context, ZMQ_PUB);
    publisher.bind("tcp://*:9999");

    // initialise vector of strings
    std::vector<std::string> values;
    values.push_back("yo");

    while (1) {
    
        zmq::message_t message;
        bool rc;

        if((rc = subscriber.recv(&message, ZMQ_DONTWAIT)) == true)
        {

            std::string update_string;
            update_string.assign(static_cast<char *>(message.data()), message.size());
            values[0] = update_string;

            // std::cout<<"oh ma gad"<<std::endl;
            // std::cout<<update_string<<std::endl;
            // std::cout<<"ffaaaaaack"<<std::endl;

            publisher.send(message);
        }

        else
        {
            // get last value from vector of strings
            std::string saved_message;
            saved_message = values.back();

            // turn string into bytes to be sent to bhv_chain_action.cpp file
            zmq::message_t reply (saved_message.size());
            memcpy (reply.data (), saved_message.c_str(), saved_message.size());
            publisher.send(reply);
            // std::cout<<"no"<<saved_message<<std::endl;
        }


    }
    return 0;
}