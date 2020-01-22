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
    std::string update_string;
    zmq::message_t message;


    while (1) {

        bool rc;

        // if received send new string
       if((rc = subscriber.recv(&message))==true)
       {
                subscriber.recv(&message);
                publisher.send(message);
                update_string.assign(static_cast<char*>(message.data()), message.size());
                
                // std::vector<std::string> strVec;
                // strVec.push_back(update_string);
                // save new string into vector
                // when not received update_string becomes size32 empty characters so only save when not that
//                if (sizeof(update_string)!=32)
//                {
                values.push_back(update_string);
//                }
                std::cout<<"dd"<<std::endl;
                std::cout<<message<<std::endl;
                
                std::cout<<"qq"<<std::endl;

                std::cout<<update_string.c_str()<<std::endl;


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
               std::cout<<"no"<<saved_message<<std::endl;
////
////
       }


    }
    return 0;
}