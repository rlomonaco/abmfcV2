# abm-fc

agent2d-3.1.1 and team_usqrd is almost identical otherthan:

1. action_chain_graph.h & action_chain_graph.cpp
2. bhv_chain_action.h & bhv_chain_action.cpp
3. bhv_basic_move.h & bhv_basic_move.cpp
	- currently not used but needed for movment

rcssserver-15.6.0 has two files altered:

1. serializemonitor.h & serializemonitor.cpp
2. dispender.h & dispender.cpp

In order to introduce python interface using zmq server package.

All python related files are located in python_interface.

Run program with run.sh
