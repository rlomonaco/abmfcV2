// --c++--

/*
 *Copyright:

 Copyright (C) Hidehisa AKIYAMA

 This code is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 3, or (at your option)
 any later version.

 This code is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this code; see the file COPYING.  If not, write to
 the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.

 *EndCopyright:
 */

/////////////////////////////////////////////////////////////////////

#ifdef HAVE_CONFIG_H
#include <config.h>
#endif

#include "bhv_basic_move.h"

#include "strategy.h"

#include "bhv_basic_tackle.h"

#include <rcsc/action/basic_actions.h>
#include <rcsc/action/body_go_to_point.h>
#include <rcsc/action/body_intercept.h>
#include <rcsc/action/neck_turn_to_ball_or_scan.h>
#include <rcsc/action/neck_turn_to_low_conf_teammate.h>

#include <rcsc/player/player_agent.h>
#include <rcsc/player/debug_client.h>
#include <rcsc/player/intercept_table.h>

#include <rcsc/common/logger.h>
#include <rcsc/common/server_param.h>

#include "neck_offensive_intercept_neck.h"

/*
//===================================================================
//  Socket
//===================================================================
*/
#include <string>
#include <sstream>
#include <zmq.hpp>
#include <iostream>
#include <unistd.h>

//#include <sys/types.h>
//#include <sys/socket.h>
//#include <netdb.h>
//#include <arpa/inet.h>
//#include <string.h>


using namespace rcsc;


//-------------------------------------------------------------------//
/*!

 */
bool
Bhv_BasicMove::execute( PlayerAgent * agent )
{

     dlog.addText( Logger::TEAM,
                  __FILE__": Bhv_BasicMove" );

    //-----------------------------------------------
    // tackle
    if ( Bhv_BasicTackle( 0.8, 80.0 ).execute( agent ) )
    {
        return true;
    }

    const WorldModel & wm = agent->world();


   //--------------------------------------------------------//
    // chase ball
    const int self_min = wm.interceptTable()->selfReachCycle();
    const int mate_min = wm.interceptTable()->teammateReachCycle();
    const int opp_min = wm.interceptTable()->opponentReachCycle();

    // if(self_min == 0 || mate_min ==0)
    // {
    //     std::cout<<"ourball"<<std::endl;
    // }
    // else if(opp_min == 0)
    // {
    //     std::cout<<"their ball"<<std::endl;
    // }
    

    if ( ! wm.existKickableTeammate()
         && ( self_min <= 3
              || ( self_min <= mate_min
                   && self_min < opp_min + 3 )
              )
         )
    {
        dlog.addText( Logger::TEAM,
                      __FILE__": intercept" );
        Body_Intercept().execute( agent );
        agent->setNeckAction( new Neck_OffensiveInterceptNeck() );

        return true;
    }


// =================================================================
// zmq listener
// =================================================================


    Vector2D move_pos;
    int confl = 1;

    std::string server_address = "tcp://localhost:5555";

    // Create a subscriber socket
    zmq::context_t context(1);

    zmq::socket_t subscriber (context, ZMQ_SUB);
    subscriber.setsockopt(ZMQ_CONFLATE, &confl, sizeof(confl));
    subscriber.setsockopt(ZMQ_SUBSCRIBE, "", 0);
    subscriber.connect(server_address);

    //  Read received messages
    zmq::message_t update;
    subscriber.recv(&update);

    // Read as a string
    std::string update_string;
    update_string.assign(static_cast<char *>(update.data()), update.size());
    // update_string.erase(0, 6); //remove "move: " in order to process


// =================================================================
// Split Text
// =================================================================
    // split into vector of strings
    std::stringstream ss(update_string);
    std::string token, PlayerCoord;

    std::vector<std::string> AllCoords;
    while(std::getline(ss, token, ',')) {
        AllCoords.push_back(token);
    }

    if (AllCoords[0] == "1"){

    std::size_t index = agent -> world().self().unum();
    PlayerCoord = AllCoords[index];


    // split into coordinates x and y
    // define empty vec & string stream
    std::vector<double> coord;
    std::stringstream cc(PlayerCoord);

    // loop through string stream
    for (double i; cc >> i;)
    {
        coord.push_back(i);
        // std::cout<<i<<std::endl;   
        if (cc.peek() == ' '){
          // std::cout<<"ignored"<<std::endl;
          cc.ignore();
        }
            
    }

    double x, y;
    x = coord[0];
    y = coord[1];
    move_pos = Vector2D(x,y);

    std::cout<<"bhv: "<<update_string<<std::endl;
    }
    else
    {
        const Vector2D target_point = Strategy::i().getPosition( wm.self().unum() );
        move_pos = target_point;
    }
    // std::cout<<move_pos<<std::endl;
    

    const double dash_power = Strategy::get_normal_dash_power( wm );

    double dist_thr = wm.ball().distFromSelf() * 0.1;
    if ( dist_thr < 1.0 ) dist_thr = 1.0;

    dlog.addText( Logger::TEAM,
                  __FILE__": Bhv_BasicMove target=(%.1f %.1f) dist_thr=%.2f",
                  // target_point.x, target_point.y,
                  move_pos.x, move_pos.y,
                  dist_thr );

    agent->debugClient().addMessage( "BasicMove%.0f", dash_power );
    // agent->debugClient().setTarget( target_point );
    agent->debugClient().setTarget( move_pos );

    // agent->debugClient().addCircle( target_point, dist_thr );
    agent->debugClient().addCircle( move_pos, dist_thr );

    // if ( ! Body_GoToPoint( target_point, dist_thr, dash_power
    if ( ! Body_GoToPoint( move_pos, dist_thr, dash_power

                           ).execute( agent ) )
    {
        Body_TurnToBall().execute( agent );
    }

    if ( wm.existKickableOpponent()
         && wm.ball().distFromSelf() < 18.0 )
    {
        agent->setNeckAction( new Neck_TurnToBall() );
    }
    else
    {
        agent->setNeckAction( new Neck_TurnToBallOrScan() );
    }

    return true;
}
