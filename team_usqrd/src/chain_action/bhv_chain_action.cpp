// -*-c++-*-

/*
 *Copyright:

 Copyright (C) Hiroki SHIMORA, Hidehisa AKIYAMA

 This code is free software; you can redistribute it and/or
 modify it under the terms of the GNU Lesser General Public
 License as published by the Free Software Foundation; either
 version 2.1 of the License, or (at your option) any later version.

 This library is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 Lesser General Public License for more details.

 You should have received a copy of the GNU Lesser General Public
 License along with this library; if not, write to the Free Software
 Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

 *EndCopyright:
 */

//////////////////////////////////////////////////////////////////////
/*
actions
Shoot: Body_ForceShoot
Dribble: Bhv_NormalDribble
Hold: Body_HoldBall
Pass: Bhv_PassKickFindReceiver
Move: Body_GoToPoint
NoAction
*/
//////////////////////////////////////////////////////////////////////
#ifdef HAVE_CONFIG_H
#include <config.h>
#endif

#include "bhv_chain_action.h"

#include "action_chain_holder.h"
#include "action_chain_graph.h"
#include "action_state_pair.h"
#include "field_analyzer.h"

#include "bhv_pass_kick_find_receiver.h"
#include "bhv_normal_dribble.h"
#include "body_force_shoot.h"

#include "neck_turn_to_receiver.h"

#include <rcsc/action/bhv_scan_field.h>
#include <rcsc/action/body_clear_ball.h>
#include <rcsc/action/body_go_to_point.h>
#include <rcsc/action/body_hold_ball.h>
#include <rcsc/action/body_turn_to_point.h>
#include <rcsc/action/neck_scan_field.h>
#include <rcsc/action/neck_turn_to_goalie_or_scan.h>

#include <rcsc/action/kick_table.h>

#include <rcsc/player/intercept_table.h>
#include <rcsc/player/soccer_intention.h>
#include <rcsc/player/player_agent.h>
#include <rcsc/common/server_param.h>
#include <rcsc/common/logger.h>

/*
//===================================================================
//  Socket
//===================================================================
*/
#include <zmq.hpp>

#include <iostream>
// #include <sys/types.h>
#include <unistd.h>
// #include <sys/socket.h>
// #include <netdb.h>
// #include <arpa/inet.h>
// #include <string.h>
// // #include <string>

using namespace rcsc;

namespace {

class IntentionTurnTo
    : public SoccerIntention {
private:
    int M_step;
    Vector2D M_target_point;

public:

    IntentionTurnTo( const Vector2D & target_point )
        : M_step( 0 ),
          M_target_point( target_point )
      { }

    bool finished( const PlayerAgent * agent );

    bool execute( PlayerAgent * agent );

private:

};

/*-------------------------------------------------------------------*/
/*!

 */
bool
IntentionTurnTo::finished( const PlayerAgent * agent )
{
    ++M_step;

    dlog.addText( Logger::TEAM,
                  __FILE__": (finished) step=%d",
                  M_step );

    if ( M_step >= 2 )
    {
        dlog.addText( Logger::TEAM,
                      __FILE__": (finished) time over" );
        return true;
    }

    const WorldModel & wm = agent->world();

    //
    // check kickable
    //

    if ( ! wm.self().isKickable() )
    {
        dlog.addText( Logger::TEAM,
                      __FILE__": (finished) no kickable" );
        return true;
    }

    //
    // check opponent
    //

    if ( wm.existKickableOpponent() )
    {
        dlog.addText( Logger::TEAM,
                      __FILE__": (finished) exist kickable opponent" );
        return true;
    }

    if ( wm.interceptTable()->opponentReachCycle() <= 1 )
    {
        dlog.addText( Logger::TEAM,
                      __FILE__": (finished) opponent may be kickable" );
        return true;
    }

    //
    // check next kickable
    //

    double kickable2 = std::pow( wm.self().playerType().kickableArea()
                                 - wm.self().vel().r() * ServerParam::i().playerRand()
                                 - wm.ball().vel().r() * ServerParam::i().ballRand()
                                 - 0.15,
                                 2 );
    Vector2D self_next = wm.self().pos() + wm.self().vel();
    Vector2D ball_next = wm.ball().pos() + wm.ball().vel();

    if ( self_next.dist2( ball_next ) > kickable2 )
    {
        // unkickable if turn is performed.
        dlog.addText( Logger::TEAM,
                      __FILE__": (finished) unkickable at next cycle" );
        return true;
    }

    return false;
}

/*-------------------------------------------------------------------*/
/*!

 */
bool
IntentionTurnTo::execute( PlayerAgent * agent )
{
    dlog.addText( Logger::TEAM,
                  __FILE__": (intention) facePoint=(%.1f %.1f)",
                  M_target_point.x, M_target_point.y );
    agent->debugClient().addMessage( "IntentionTurnToForward" );

    Body_TurnToPoint( M_target_point ).execute( agent );
    agent->setNeckAction( new Neck_ScanField() );

    return true;
}

}

/*-------------------------------------------------------------------*/
/*!

 */
Bhv_ChainAction::Bhv_ChainAction( const ActionChainGraph & chain_graph )
    : M_chain_graph( chain_graph )
{

}

/*-------------------------------------------------------------------*/
/*!

 */
Bhv_ChainAction::Bhv_ChainAction()
    : M_chain_graph( ActionChainHolder::i().graph() )
{

}

/*-------------------------------------------------------------------*/
/*!

 */
bool
Bhv_ChainAction::execute( PlayerAgent * agent)
{
    dlog.addText( Logger::TEAM,
                  __FILE__": Bhv_ChainAction" );

    // std::cout<<"agent_num: "<<agent->world().self().unum()<<std::endl;


    if ( doTurnToForward( agent ) )
    {
        return true;
    }

    const ServerParam & SP = ServerParam::i();
    const WorldModel & wm = agent->world();
    
    // std::cout<< wm.self().unum() << std::endl;

    const CooperativeAction & first_action = M_chain_graph.getFirstAction();

    ActionChainGraph::debug_send_chain( agent, M_chain_graph.getAllChain() );

    const Vector2D goal_pos = SP.theirTeamGoalPos();
    agent->setNeckAction( new Neck_TurnToReceiver( M_chain_graph ) );


    // std::cout<< first_action << std::endl;

    /*
        Hold,
        Dribble,
        Pass,
        Shoot,
        Clear,
        Move,

        NoAction,
    */

// ============================================================================
// ZMQ Subscriber
// ============================================================================
      std::string server_address = "tcp://localhost:9999";
      // Create a subscriber socket
      zmq::context_t context(1);

      zmq::socket_t subscriber (context, ZMQ_SUB);
      subscriber.setsockopt(ZMQ_SUBSCRIBE, "", 0);
      subscriber.connect(server_address);

      //  Read envelope with address
      zmq::message_t update;
      subscriber.recv(&update);

      // Read as a string
      std::string update_string;
      update_string.assign(static_cast<char *>(update.data()), update.size());
      // update_string.erase(0,7);
      std::cout<<"received: "<<update_string<<std::endl;

// ============================================================================ 
      // Split Text
// ============================================================================

      // define empty vec & string stream
      std::vector<double> vect;
      std::stringstream ss(update_string);

      // loop through string stream
      for (int i; ss >> i;) 
      {
          vect.push_back(i);
          // std::cout<<i<<std::endl;   
          if (ss.peek() == ','){
            // std::cout<<"ignored"<<std::endl;
            ss.ignore();
          }
              
      }
      int index = agent -> world().self().unum();
      int on_off, option, pass_target, player_num;
      double pos_x;
      double pos_y;
      on_off = vect[0];
      // bool received_from_py = false;

      player_num = vect[1];
      std::cout<<"yo:"<<player_num<<index<<std::endl;
      if (on_off ==  1 && player_num == index)
      {
      option = vect[2];
      pos_x = vect[3];
      pos_y = vect[4];
      std::cout<<"python controlled"<<std::endl;
      pass_target = vect[5];
      }
      else if (player_num != index)
      {
        std::cout<<"bhv controlled"<<std::endl;

        option = 1;
        pos_x = NULL;
        pos_y = NULL;

      }
      else
      {
        std::cout<<"no control"<<std::endl;

        option = first_action.category();
        pos_x = NULL;
        pos_y = NULL;
      }

    // int move = 0;
    std::cout<<"ball pos: "<<wm.ball().pos()<<std::endl;
    std::cout<<"current pos: "<<wm.self().pos()<<std::endl;

    // int option = std::stoi(std::string(buf, bytesReceived).at(0));
    switch ( option ) { 
    // switch (first_action.category()) {
    case CooperativeAction::Shoot:
        {
            dlog.addText( Logger::TEAM,
                          __FILE__" (Bhv_ChainAction) shoot" );
            if ( Body_ForceShoot().execute( agent ) )
            {
                agent->setNeckAction( new Neck_TurnToGoalieOrScan() );

                return true;
            }

            break;
        }

    case CooperativeAction::Dribble:
        {
            std::cout<<"dribble"<<std::endl;
            if ( wm.gameMode().type() != GameMode::PlayOn
                 && ! wm.gameMode().isPenaltyKickMode() )
            {
                agent->debugClient().addMessage( "CancelChainDribble" );
                dlog.addText( Logger::TEAM,
                              __FILE__" (Bhv_ChainAction) cancel dribble" );
                return false;
            }

            // const Vector2D & dribble_target = first_action.targetPoint();
            Vector2D dribble_pos = Vector2D(pos_x, pos_y);

            dlog.addText( Logger::TEAM,
                          __FILE__" (Bhv_ChainAction) dribble target=(%.1f %.1f)",
                          dribble_pos.x, dribble_pos.y );

            NeckAction::Ptr neck;
            double goal_dist = goal_pos.dist( dribble_pos );
            if ( goal_dist < 18.0 )
            {
                int count_thr = 0;
                if ( goal_dist < 13.0 )
                {
                    count_thr = -1;
                }
                agent->debugClient().addMessage( "ChainDribble:LookGoalie" );
                neck = NeckAction::Ptr( new Neck_TurnToGoalieOrScan( count_thr ) );
            }

            if ( Bhv_NormalDribble(dribble_pos, first_action, neck ).execute( agent ) )
            {

                return true;
            }
            break;
        }

    case CooperativeAction::Hold:
        {
            if ( wm.gameMode().type() != GameMode::PlayOn )
            {
                agent->debugClient().addMessage( "CancelChainHold" );
                dlog.addText( Logger::TEAM,
                              __FILE__" (Bhv_ChainAction) cancel hold" );
                return false;
            }

            if ( wm.ball().pos().x < -SP.pitchHalfLength() + 8.0
                 && wm.ball().pos().absY() < SP.goalHalfWidth() + 1.0 )
            {
                agent->debugClient().addMessage( "ChainHold:Clear" );
                dlog.addText( Logger::TEAM,
                              __FILE__" (Bhv_ChainAction) cancel hold. clear ball" );
                Body_ClearBall().execute( agent );
                agent->setNeckAction( new Neck_ScanField() );
                

                return true;
            }

            agent->debugClient().addMessage( "hold" );
            dlog.addText( Logger::TEAM,
                          __FILE__" (Bhv_ChainAction) hold" );

            Body_HoldBall().execute( agent );
            agent->setNeckAction( new Neck_ScanField() );


            return true;
            break;
        }

    case CooperativeAction::Pass:
        {   
            std::cout<<"pass"<<std::endl;

            Vector2D pass_pos = Vector2D(pos_x,pos_y);

            // dlog.addText( Logger::ACTION_CHAIN,
            //     "__ %d: pass (%s[%d]) t=%d from[%d](%.2f %.2f)-to[%d](%.2f %.2f)",
            //     0, "strictLead", first_action.index(), 10,
            //     wm.self().unum(),
            //     wm.ball().pos().x, wm.ball().pos().y,
            //     pass_target,
            //     pass_pos.x, pass_pos.y );
            agent->setNeckAction( new Neck_ScanField() );

            dlog.addText( Logger::TEAM,
                          __FILE__" (Bhv_ChainAction) pass" );
            Bhv_PassKickFindReceiver( M_chain_graph, pass_pos, pass_target).execute( agent );
            
            
            return true;
            break;
        }

    case CooperativeAction::Move:
        {
            dlog.addText( Logger::TEAM,
                          __FILE__" (Bhv_ChainAction) move" );

            if ( Body_GoToPoint( first_action.targetPoint(),
                                 1.0,
                                 SP.maxDashPower() ).execute( agent ) )
            {
                agent->setNeckAction( new Neck_ScanField() );
                

                return true;
            }

            break;
        }

    case CooperativeAction::NoAction:
        {
            std::cout<<"No Action"<<std::endl;

            dlog.addText( Logger::TEAM,
                          __FILE__" (Bhv_ChainAction) no action" );


            return true;
            break;
        }

    default:
        dlog.addText( Logger::TEAM,
                      __FILE__" (Bhv_ChainAction) invalid category" );

        break;

    }

    return false;

}


/*-------------------------------------------------------------------*/
/*!

 */
bool
Bhv_ChainAction::doTurnToForward( PlayerAgent * agent )
{
    const WorldModel & wm = agent->world();

    if ( wm.gameMode().type() != GameMode::PlayOn )
    {
        return false;
    }

    Vector2D face_point( 42.0, 0.0 );

    const double body_angle_diff = ( ( face_point - wm.self().pos() ).th() - wm.self().body() ).abs();
    if ( body_angle_diff < 110.0 )
    {
        dlog.addText( Logger::TEAM,
                      __FILE__" (doTurnToForward) already facing the forward direction. angle_diff=%.1f",
                      body_angle_diff );
        return false;
    }

    dlog.addText( Logger::TEAM,
                  __FILE__" (doTurnToForward) angle_diff=%.1f. try turn",
                  body_angle_diff );

    // const double opponent_dist_thr = ( wm.self().pos().x > ServerParam::i().theirPenaltyAreaLineX() - 2.0
    //                                    && wm.self().pos().absY() > ServerParam::i().goalHalfWidth()
    //                                    ? 2.7
    //                                    : 4.0 );
    const double opponent_dist_thr = 4.0;

    const PlayerPtrCont::const_iterator o_end = wm.opponentsFromSelf().end();
    for ( PlayerPtrCont::const_iterator o = wm.opponentsFromSelf().begin();
          o != o_end;
          ++o )
    {
        double dist = (*o)->distFromSelf();
        dist -= bound( 0, (*o)->posCount(), 3 ) * (*o)->playerTypePtr()->realSpeedMax();

        if ( dist < opponent_dist_thr )
        {
            dlog.addText( Logger::TEAM,
                      __FILE__" (doTurnToForward) exist opponent" );
            return false;
        }

        if ( dist > 10.0 )
        {
            break;
        }
    }

    // TODO: find the best scan target angle
    face_point.y = wm.self().pos().y * 0.5;


    double kickable2 = std::pow( wm.self().playerType().kickableArea()
                                 - wm.self().vel().r() * ServerParam::i().playerRand()
                                 - wm.ball().vel().r() * ServerParam::i().ballRand()
                                 - 0.2,
                                 2 );
    Vector2D self_next = wm.self().pos() + wm.self().vel();
    Vector2D ball_next = wm.ball().pos() + wm.ball().vel();

    if ( self_next.dist2( ball_next ) < kickable2 )
    {
        Body_TurnToPoint( face_point ).execute( agent );
        agent->setNeckAction( new Neck_ScanField() );
        return true;
    }


    Vector2D ball_vel = getKeepBallVel( agent->world() );

    if ( ! ball_vel.isValid() )
    {
        dlog.addText( Logger::TEAM,
                      __FILE__": (doKeepBall) no candidate." );

        return false;
    }

    //
    // perform first kick
    //

    Vector2D kick_accel = ball_vel - wm.ball().vel();
    double kick_power = kick_accel.r() / wm.self().kickRate();
    AngleDeg kick_angle = kick_accel.th() - wm.self().body();

    dlog.addText( Logger::TEAM,
                  __FILE__": (doTurnToForward) "
                  " ballVel=(%.2f %.2f)"
                  " kickPower=%.1f kickAngle=%.1f",
                  ball_vel.x, ball_vel.y,
                  kick_power,
                  kick_angle.degree() );

    if ( kick_power > ServerParam::i().maxPower() )
    {
        dlog.addText( Logger::TEAM,
                      __FILE__": (doTurnToForward) over kick power" );
        Body_HoldBall( true,
                       face_point ).execute( agent );
        agent->setNeckAction( new Neck_ScanField() );
    }
    else
    {
        agent->doKick( kick_power, kick_angle );
        agent->setNeckAction( new Neck_ScanField() );
    }

    agent->debugClient().addMessage( "Chain:Turn:Keep" );
    agent->debugClient().setTarget( face_point );

    //
    // set turn intention
    //

    dlog.addText( Logger::TEAM,
                  __FILE__": (doTurnToFoward) register intention" );
    agent->setIntention( new IntentionTurnTo( face_point ) );

    return true;
}

/*-------------------------------------------------------------------*/
/*!

 */
Vector2D
Bhv_ChainAction::getKeepBallVel( const WorldModel & wm )
{
    static GameTime s_update_time( 0, 0 );
    static Vector2D s_best_ball_vel( 0.0, 0.0 );

    if ( s_update_time == wm.time() )
    {
        return s_best_ball_vel;
    }
    s_update_time = wm.time();

    //
    //
    //

    const int ANGLE_DIVS = 12;

    const ServerParam & SP = ServerParam::i();
    const PlayerType & ptype = wm.self().playerType();
    const double collide_dist2 = std::pow( ptype.playerSize()
                                           + SP.ballSize(),
                                           2 );
    const double keep_dist = ptype.playerSize()
        + ptype.kickableMargin() * 0.5
        + ServerParam::i().ballSize();

    const Vector2D next_self_pos
        = wm.self().pos() + wm.self().vel();
    const Vector2D next2_self_pos
        = next_self_pos
        + wm.self().vel() * ptype.playerDecay();

    //
    // create keep target point
    //

    Vector2D best_ball_vel = Vector2D::INVALIDATED;
    int best_opponent_step = 0;
    double best_ball_speed = 1000.0;


    for ( int a = 0; a < ANGLE_DIVS; ++a )
    {
        Vector2D keep_pos
            = next2_self_pos
            + Vector2D::from_polar( keep_dist,
                                    360.0/ANGLE_DIVS * a );
        if ( keep_pos.absX() > SP.pitchHalfLength() - 0.2
             || keep_pos.absY() > SP.pitchHalfWidth() - 0.2 )
        {
            continue;
        }

        Vector2D ball_move = keep_pos - wm.ball().pos();
        double ball_speed = ball_move.r() / ( 1.0 + SP.ballDecay() );

        Vector2D max_vel
            = KickTable::calc_max_velocity( ball_move.th(),
                                            wm.self().kickRate(),
                                            wm.ball().vel() );
        if ( max_vel.r2() < std::pow( ball_speed, 2 ) )
        {
            continue;
        }

        Vector2D ball_next_next = keep_pos;

        Vector2D ball_vel = ball_move.setLengthVector( ball_speed );
        Vector2D ball_next = wm.ball().pos() + ball_vel;

        if ( next_self_pos.dist2( ball_next ) < collide_dist2 )
        {
            ball_next_next = ball_next;
            ball_next_next += ball_vel * ( SP.ballDecay() * -0.1 );
        }

#ifdef DEBUG_PRINT
        dlog.addText( Logger::TEAM,
                      __FILE__": (getKeepBallVel) %d: ball_move th=%.1f speed=%.2f max=%.2f",
                      a,
                      ball_move.th().degree(),
                      ball_speed,
                      max_vel.r() );
        dlog.addText( Logger::TEAM,
                      __FILE__": __ ball_next=(%.2f %.2f) ball_next2=(%.2f %.2f)",
                      ball_next.x, ball_next.y,
                      ball_next_next.x, ball_next_next.y );
#endif

        //
        // check opponent
        //

        int min_step = 1000;
        for ( PlayerPtrCont::const_iterator o = wm.opponentsFromSelf().begin();
              o != wm.opponentsFromSelf().end();
              ++o )
        {
            if ( (*o)->distFromSelf() > 10.0 )
            {
                break;
            }

            int o_step = FieldAnalyzer::predict_player_reach_cycle( *o,
                                                                    ball_next_next,
                                                                    (*o)->playerTypePtr()->kickableArea(),
                                                                    0.0, // penalty distance
                                                                    1, // body count thr
                                                                    1, // default turn step
                                                                    0, // wait cycle
                                                                    true );

            if ( o_step <= 0 )
            {
                break;
            }

            if ( o_step < min_step )
            {
                min_step = o_step;
            }
        }
#ifdef DEBUG_PRINT
        dlog.addText( Logger::TEAM,
                      __FILE__": (getKeepBallVel) %d: keepPos=(%.2f %.2f)"
                      " ballNext2=(%.2f %.2f) ballVel=(%.2f %.2f) speed=%.2f o_step=%d",
                      a,
                      keep_pos.x, keep_pos.y,
                      ball_next_next.x, ball_next_next.y,
                      ball_vel.x, ball_vel.y,
                      ball_speed,
                      min_step );
#endif
        if ( min_step > best_opponent_step )
        {
            best_ball_vel = ball_vel;
            best_opponent_step = min_step;
            best_ball_speed = ball_speed;
        }
        else if ( min_step == best_opponent_step )
        {
            if ( best_ball_speed > ball_speed )
            {
                best_ball_vel = ball_vel;
                best_opponent_step = min_step;
                best_ball_speed = ball_speed;
            }
        }
    }

    s_best_ball_vel = best_ball_vel;
    return s_best_ball_vel;
}
