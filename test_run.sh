clear
fuser -k 5555/tcp 
fuser -k 6666/tcp
fuser -k 7777/tcp  
fuser -k 8889/tcp
fuser -k 9999/tcp 


./python_interface/socket_server  &
python python_interface/read_socket.py &
./python_interface/move_commands &
./python_interface/chain_commands &
cd texts_from_run &
sleep 0.2
rcsoccersim > texts_from_run/log1.txt &
sleep 0.5
./team_usqrd/src/start.sh > texts_from_run/log2.txt &
#sleep 0.5
#./agent2d-3.1.1/src/start.sh > texts_from_run/log3.txt
