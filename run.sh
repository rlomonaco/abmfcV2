clear
fuser -k 5555/tcp 
fuser -k 6666/tcp
fuser -k 7777/tcp  
fuser -k 8889/tcp
fuser -k 9999/tcp 


./socket_server  &
python read_socket.py&
./move_commands &
./chain_commands &
rcsoccersim > log1.txt &
sleep 0.5
./team_usqrd/src/start.sh &
sleep 0.5
./agent2d-3.1.1/src/start.sh > log3.txt
