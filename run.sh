#!/bin/sh

./socket_server &
./socket2_server &
python read_socket.py &
python testfile.py &
rcsoccersim &
sleep 0.5
./team_usqrd/src/start.sh > log1.txt &
sleep 0.5
./agent2d-3.1.1/src/start.sh 
