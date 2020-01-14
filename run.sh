./socket_server > log1.txt &
python read_socket.py &
python move_commands.py &
python chain_commands.py &
rcsoccersim > log2.txt &
sleep 0.5
./team_usqrd/src/start.sh  &
sleep 0.5
./agent2d-3.1.1/src/start.sh > log3.txt
