// -*-c++-*-

/***************************************************************************
                            serializermonitor.cpp
                  Class for serializing data to monitors
                             -------------------
    begin                : 2007-11-22
    copyright            : (C) 2007 by The RoboCup Soccer Server
                           Maintenance Group.
    email                : sserver-admin@lists.sourceforge.net
***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU LGPL as published by the Free Software  *
 *   Foundation; either version 3 of the License, or (at your option) any  *
 *   later version.                                                        *
 *                                                                         *
 ***************************************************************************/



/*
//===================================================================
//  Socket
//===================================================================
*/
#include <iostream>
#include <sys/types.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <string.h>
#include <string>


// #include "zhelpers.hpp"
#include <zmq.hpp>
#include <chrono>  // for high_resolution_clock

//===================================================================

#ifdef HAVE_CONFIG_H
#include <config.h>
#endif

#include "serializermonitor.h"

#include "param.h"
#include "utility.h"
#include "object.h"
#include "player.h"
#include "team.h"
#include "xpmholder.h"

namespace rcss {

/*
//===================================================================
//
//  SerializerMonitorStdv1
//
//===================================================================
*/

SerializerMonitorStdv1::SerializerMonitorStdv1( const SerializerCommon::Ptr common )
    : SerializerMonitor( common )
{

}

SerializerMonitorStdv1::~SerializerMonitorStdv1()
{

}

const
SerializerMonitor::Ptr
SerializerMonitorStdv1::create()
{
    SerializerCommon::Creator cre_common;
    if ( ! SerializerCommon::factory().getCreator( cre_common, 8 ) )
    {
        return SerializerMonitor::Ptr();
    }

    SerializerMonitor::Ptr ptr( new SerializerMonitorStdv1( cre_common() ) );
    return ptr;
}

void
SerializerMonitorStdv1::serializeTeamGraphic( std::ostream & os,
                                              const Side side,
                                              const unsigned int x,
                                              const unsigned int y,
                                              const XPMHolder & xpm ) const
{
    os << "(team_graphic_"
       << ( side == LEFT ? "l" : "r" )
       << " (" << x << " " << y << " "
       << xpm << ")";
}


/*
//===================================================================
//
//  SerializerMonitorStdv3
//
//===================================================================
*/

const double SerializerMonitorStdv3::PREC = 0.0001;
const double SerializerMonitorStdv3::DPREC = 0.001;

SerializerMonitorStdv3::SerializerMonitorStdv3( const SerializerCommon::Ptr common )
    : SerializerMonitorStdv1( common )
{

}

SerializerMonitorStdv3::~SerializerMonitorStdv3()
{

}

const
SerializerMonitor::Ptr
SerializerMonitorStdv3::create()
{
    SerializerCommon::Creator cre_common;
    if ( ! SerializerCommon::factory().getCreator( cre_common, 8 ) )
    {
        return SerializerMonitor::Ptr();
    }

    SerializerMonitor::Ptr ptr( new SerializerMonitorStdv3( cre_common() ) );
    return ptr;
}


void
SerializerMonitorStdv3::serializeTeam( std::ostream & os,
                                       const int time,
                                       const Team & team_l,
                                       const Team & team_r ) const
{
    os << "(team " << time
       << ' ' << ( team_l.name().empty() ? "null" : team_l.name().c_str() )
       << ' ' << ( team_r.name().empty() ? "null" : team_r.name().c_str() )
       << ' ' << team_l.point()
       << ' ' << team_r.point();

    if ( team_l.penaltyTaken() > 0 || team_r.penaltyTaken() > 0 )
    {
        os << ' ' << team_l.penaltyPoint()
           << ' ' << team_l.penaltyTaken() - team_l.penaltyPoint()
           << ' ' << team_r.penaltyPoint()
           << ' ' << team_r.penaltyTaken() - team_r.penaltyPoint();
    }
    os << ')';

}

void
SerializerMonitorStdv3::serializePlayMode( std::ostream & os,
                                           const int time,
                                           const PlayMode pmode ) const
{
    static const char * playmode_strings[] = PLAYMODE_STRINGS;

    os << "(playmode " << time
       << ' ' << playmode_strings[pmode]
       << ')';
}


void
SerializerMonitorStdv3::serializeShowBegin( std::ostream & os,
                                            const int time ) const
{
    os << "(show " << time;
}   

void
SerializerMonitorStdv3::serializeShowEnd( std::ostream & os ) const
{
    os << ')';
}

void
SerializerMonitorStdv3::serializePlayModeId( std::ostream & os,
                                             const PlayMode pmode ) const
{
    os << " (pm " << pmode << ')';
}

void
SerializerMonitorStdv3::serializeScore( std::ostream & os,
                                        const Team & team_l,
                                        const Team & team_r ) const
{
    os << " (tm"
       << ' ' << ( team_l.name().empty() ? "null" : team_l.name().c_str() )
       << ' ' << ( team_r.name().empty() ? "null" : team_r.name().c_str() )
       << ' ' << team_l.point()
       << ' ' << team_r.point();

    if ( team_l.penaltyTaken() > 0 || team_r.penaltyTaken() > 0 )
    {
        os << ' ' << team_l.penaltyPoint()
           << ' ' << team_l.penaltyTaken() - team_l.penaltyPoint()
           << ' ' << team_r.penaltyPoint()
           << ' ' << team_r.penaltyTaken() - team_r.penaltyPoint();
    }
    os << ')';
}

void
SerializerMonitorStdv3::serializeBall( std::ostream & os,
                                       const Ball & ball ) const
{
    os << " (" << BALL_NAME_SHORT
       << ' ' << Quantize( ball.pos().x, PREC )
       << ' ' << Quantize( ball.pos().y, PREC )
       << ' ' << Quantize( ball.vel().x, PREC )
       << ' ' << Quantize( ball.vel().y, PREC )
       << ')';
}

void
SerializerMonitorStdv3:: serializePlayerBegin( std::ostream & os,
                                               const Player & player ) const
{
    os << " ("
       << '(' << SideStr( player.side() ) << ' ' << player.unum() << ')'
       << ' ' << player.playerTypeId()
       << ' ' << std::hex << std::showbase
       << player.state()
       << std::dec << std::noshowbase;
}

void
SerializerMonitorStdv3::serializePlayerEnd( std::ostream & os ) const
{
    os << ')';
}

void
SerializerMonitorStdv3::serializePlayerPos( std::ostream & os,
                                                const Player & player ) const
{
    os << ' ' << Quantize( player.pos().x, PREC )
       << ' ' << Quantize( player.pos().y, PREC )
       << ' ' << Quantize( player.vel().x, PREC )
       << ' ' << Quantize( player.vel().y, PREC )
       << ' ' << Quantize( Rad2Deg( player.angleBodyCommitted() ), DPREC )
       << ' ' << Quantize( Rad2Deg( player.angleNeckCommitted() ), DPREC );
}

void
SerializerMonitorStdv3::serializePlayerArm( std::ostream & os,
                                            const Player & player ) const
{
    if ( player.arm().isPointing() )
    {
        os << ' ' << Quantize( player.arm().dest().getX(), PREC )
           << ' ' << Quantize( player.arm().dest().getY(), PREC );
//         rcss::geom::Vector2D arm_dest;
//         if ( player.arm().getRelDest( rcss::geom::Vector2D( player.pos().x,
//                                                             player.pos().y ),
//                                       0.0,
//                                       arm_dest ) )
//         {
//             os << ' ' << Quantize( arm_dest.getMag(), PREC )
//                << ' ' << Quantize( Rad2Deg( arm_dest.getHead() ), DPREC );
//         }
    }
}

void
SerializerMonitorStdv3::serializePlayerViewMode( std::ostream & os,
                                                 const Player & player ) const
{
    os << " (v "
       << ( player.highQuality() ? "h " : "l " )
       << Quantize( Rad2Deg( player.visibleAngle() ), DPREC ) << ')';
}

void
SerializerMonitorStdv3::serializePlayerStamina( std::ostream & os,
                                                const Player & player ) const
{
    os << " (s "
       << player.stamina() << ' '
       << player.effort() << ' '
       << player.recovery() << ')';
}

void
SerializerMonitorStdv3::serializePlayerFocus( std::ostream & os,
                                              const Player & player ) const
{
    if ( player.isEnabled()
         && player.getFocusTarget() != NULL )
    {
        os << " (f "
           << SideStr( player.getFocusTarget()->side() ) << ' '
           << player.getFocusTarget()->unum() << ')';
    }
}

void
SerializerMonitorStdv3::serializePlayerCounts( std::ostream & os,
                                               const Player & player ) const
{
     os << " (c "
        << player.kickCount() << ' '
        << player.dashCount() << ' '
        << player.turnCount() << ' '
        << player.catchCount() << ' '
        << player.moveCount() << ' '
        << player.turnNeckCount() << ' '
        << player.changeViewCount() << ' '
        << player.sayCount() << ' '
        << player.tackleCount() << ' '
        << player.arm().getCounter() << ' '
        << player.attentiontoCount() << ')';
}



// =====================================================================================
// New Addition
// =====================================================================================


void
SerializerMonitorStdv3::printShow( std::ostream &, const int time ) const
{
    std::cout<<"show: "<<time<<std::endl;
}


void
SerializerMonitorStdv3::ballPositionOutput( std::ostream &, const Ball & ball
                                                ) const
{
  std::cout<<"ball_x: "<<ball.pos().x<<", ball_y: "<<ball.pos().y<<", ball_vx: "<<ball.vel().x<<", ball_vy: "
  <<ball.vel().y<<std::endl;
}

void
SerializerMonitorStdv3::playerPositionOutput( std::ostream &, const Player & player ) const
{
  std::cout<<"side: "<<player.side()<<", num:"<<player.unum()<<", x:"<<player.pos().x<<", y:"<<player.pos().y
  <<", vel_x:"<<player.vel().x<<", vel_y:"<<player.vel().y<<std::endl;
}

void
SerializerMonitorStdv3::SocketStadiumOutput( std::ostream &,
                                        const int time,
                                        const Team & team_l,
                                        const Team & team_r,
                                        const Ball & ball ) const
  {
    // std::cout<<time<<std::endl;

         //  Create a socket
   int sock = socket(AF_INET, SOCK_STREAM, 0);

   //  Create a hint structure for the server we're connecting with
   int port = 8889;
   std::string ipAddress = "127.0.0.1";

   sockaddr_in hint;
   hint.sin_family = AF_INET;
   hint.sin_port = htons(port);
   inet_pton(AF_INET, "127.0.0.1", &hint.sin_addr);

   //  Connect to the server on the socket
   int connectRes = connect(sock, (sockaddr*)&hint, sizeof(hint));

   //  While loop:
   // char buf[4096];
   std::string message = "show:" + std::to_string(time)
             +"\nteam_l:" + std::to_string(team_l.point())
             + "\nteam_r:" + std::to_string(team_r.point())
             + "\nball_x:" + std::to_string(ball.pos().x)+ ", ball_y:" + std::to_string(ball.pos().y)
             + ", ball_vx:" + std::to_string(ball.vel().y)+ ", ball_vy:" + std::to_string(ball.vel().y);

    send(sock, message.c_str(), message.size() + 1, 0);
   close(sock);
 
}


void
SerializerMonitorStdv3::SocketPlayerOutput( std::ostream &, const Player & player ) const
  {

    //  Create a socket
   int sock = socket(AF_INET, SOCK_STREAM, 0);

   //  Create a hint structure for the server we're connecting with
   int port = 8889;
   std::string ipAddress = "127.0.0.1";

   sockaddr_in hint;
   hint.sin_family = AF_INET;
   hint.sin_port = htons(port);
   inet_pton(AF_INET, "127.0.0.1", &hint.sin_addr);

   //  Connect to the server on the socket
   int connectRes = connect(sock, (sockaddr*)&hint, sizeof(hint));

   //  While loop:
   // char buf[4096];
   std::string message = "\nside: " + std::to_string(player.side()) + ", num:" + std::to_string(player.unum()) 
                          + ", x:" + std::to_string(player.pos().x) + ", y:" + std::to_string(player.pos().y) 
                          + ", vel_x:" + std::to_string(player.vel().x) + ", vel_y:" + std::to_string(player.vel().y) 
                          + ", kick_count:" + std::to_string(player.kickCount()) + ", stamina:" + std::to_string(player.stamina()) 
                          + ", staminaCapacity:" + std::to_string(player.staminaCapacity());

    send(sock, message.c_str(), message.size() + 1, 0);
   close(sock);


}




/*
//===================================================================
//
//  SerializerMonitorStdv4
//
//===================================================================
*/

SerializerMonitorStdv4::SerializerMonitorStdv4( const SerializerCommon::Ptr common )
    : SerializerMonitorStdv3( common )
{

}

SerializerMonitorStdv4::~SerializerMonitorStdv4()
{

}

const
SerializerMonitor::Ptr
SerializerMonitorStdv4::create()
{
    SerializerCommon::Creator cre_common;
    if ( ! SerializerCommon::factory().getCreator( cre_common, 15 ) )
    {
        return SerializerMonitor::Ptr();
    }

    SerializerMonitor::Ptr ptr( new SerializerMonitorStdv4( cre_common() ) );
    return ptr;
}

void
SerializerMonitorStdv4::serializePlayerStamina( std::ostream & os,
                                                const Player & player ) const
{
    os << " (s "
       << player.stamina() << ' '
       << player.effort() << ' '
       << player.recovery() << ' '
       << player.staminaCapacity() << ')';
}


namespace {
RegHolder v1 = SerializerMonitor::factory().autoReg( &SerializerMonitorStdv1::create, 1 );
RegHolder v2 = SerializerMonitor::factory().autoReg( &SerializerMonitorStdv1::create, 2 );
RegHolder v3 = SerializerMonitor::factory().autoReg( &SerializerMonitorStdv3::create, 3 );
RegHolder v4 = SerializerMonitor::factory().autoReg( &SerializerMonitorStdv4::create, 4 );
}

}
