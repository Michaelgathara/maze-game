import sys
import select
import time
import queue

class bot:
    def init(self,start,current_pos,seen,cost,walls):
        self.start=start
        self.current_pos=current_pos
        self.seen=seen
        self.cost=cost
        self.walls=walls

    def walls(self):
        for i in range(0,11):
            self.walls |= {(i,0,i+0,0), (i,11,i+1,11), (0,i,0,i+1), (11,i,11,i+1)}

    def solver(self,goal):
        time.sleep(0.25)
        frontier=queue.PriorityQueue()
        frontier.put((0,self.start))
        while frontier:
            check=frontier.get()
        
        # while True:
        #     while select.select([sys.stdin,],[],[],0.0)[0]:
        #         obs = sys.stdin.readline()
        #         obs = obs.split(" ")
        #         if obs == []: pass
        #         elif obs[0] == "bot":
        #         self.current_pos=(float(obs[1]),float(obs[2]))
        #         pass
start_bot_pos=(0.5,0.5)
current_bot_pos=start_bot_pos
seen_set=set()
cost=0
walls_pos=set()

a_star_bot=bot(start_bot_pos,current_bot_pos,seen_set,cost,walls_pos)
#Should I call walls ?
# a_star_bot.walls()