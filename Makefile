




default:
	clang++ -v -O2 -o server maze-game-server.cpp -ferror-limit=2 -L /usr/local/lib/libGraphicsMagick++.a `GraphicsMagick++-config --cppflags --cxxflags --ldflags --libs`

debug:
	clang++ -v -g -o server maze-game-server.cpp -ferror-limit=2 -L /usr/local/lib/libGraphicsMagick++.a `GraphicsMagick++-config --cppflags --cxxflags --ldflags --libs`

dfsbot:
	make default && ./server 'python3 dfsbot.py'

randobot:
	make default && ./server 'python3 randobot.py'

a_starbot:
	make default && ./server 'python3 a_starbot.py'

stupid:
	make default && ./server 'python3 stupid_bot.py'

huh:
	make default && ./server 'python3 huh_bot.py'

d:
	make default && ./server 'python3 d_bot.py'