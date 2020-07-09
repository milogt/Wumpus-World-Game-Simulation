###CISC6525 Artificial Intelligence
###Final Project
###Author: Guo Tian
###Date: Dec.15 2018
from aima.logic import expr, dpll_satisfiable
import pdb
import random
import time
import copy
import numpy
import sys

#modify python's maximum recursive times
sys.setrecursionlimit(10000)

#define action, facing list and corresponding number
action_list = {
    'forward': 0,
    'left': 1,
    'right': 2, 
    'pick': 3,
    }
action_prin = {
    0 : 'forward',
    1 : 'left',
    2 : 'right',
    3 : 'pick'
}

facing_list = {
    'up': 0,
    'right': 1,
    'down': 2,
    'left': 3
    }

map_list = ['G', 'W', 'S', 'P', 'B']

#function that defines the surrounding cells locations
def neighbors(i, j):
    li = set()
    if (i - 1) in range(5):
        li.add((i-1, j))
    if (i + 1) in range(5):
        li.add((i+1, j))
    if (j - 1) in range(5):
        li.add((i, j-1))
    if (j + 1) in range(5):
        li.add((i, j+1))
    return li
#function transfers world map from numeric to text
def return_world(world):
    world_c = numpy.chararray((5, 5))
    world_c[:] = 'e'
    for i in range(5):
        for j in range(5):
            if world[0][i][j]==2 and world[1][i][j]==0 and world[3][i][j]==0:
                world_c[i][j]='G'
            if world[1][i][j]==2 and world[0][i][j]==0 and world[3][i][j]==0:
                world_c[i][j]='W'
            if world[3][i][j]==2 and world[0][i][j]==0 and world[1][i][j]==0:
                world_c[i][j]='P'
            if world[0][i][j]==2 and world[1][i][j]==2 and world[3][i][j]==0:
                world_c[i][j]='G+W'
            if world[0][i][j]==2 and world[1][i][j]==0 and world[3][i][j]==2:
                world_c[i][j]='G+P'
            if world[1][i][j]==2 and world[0][i][j]==0 and world[3][i][j]==2:
                world_c[i][j]='W+P'
    return world_c

class Agent:

    #random locations of wumpus and gold
    def random_location(self):
        r = random.randint(2, 19)
        if r <= 3:
            i = 1
            j = r+1
        else:
        	i = (r + 4) % 5
        	j = (r + 1) % 5

        return (i, j)

    def __init__(self):
        self.alive = False
        self.gold_picked = False
        self.all_pos = set()
        for i in range(5):
            for j in range(5):
                self.all_pos.add((i, j))

	#initial all the parameters and random the wumpus world
    def build_world(self):
        self.alive = True
        self.gold_picked = False
        self.pos = (-1, 0)
        self.facing = facing_list['right']
        self.visited = set()
        self.danger = set()
        self.safe = set()
        self.fringe = set()
        self.plan = [action_list['forward']]
        self.world = numpy.zeros((5, 5, 5))
        self.known_world = numpy.ones((5, 5, 5))
        self.kb = WumpusKB()

    	#random the location of Gold
        i, j = self.random_location()
        self.world[0][i][j] = 2
    	#random the location of Wumpus
        i, j = self.random_location()
        self.world[1][i][j] = 2
    	#locate the cells of stench
        for pos in neighbors(i, j):
            self.world[2][pos[0]][pos[1]] = 2
    
        for i in range(5):
            for j in range(5):
                if not ((i == 0) and (j == 0)):        
            #random the location of pit
                    if random.randint(1, 20) <= 2:
                        self.world[3][i][j] = 2
                #locate the cells of breeze
                        for pos in neighbors(i, j):
                            self.world[4][pos[0]][pos[1]] = 2
        self.paths = []
        self.end = False
        #return self.world
    #function defines the agent
    def wumpus_agent(self, percept):
        if len(self.safe) > 0:
            source = self.safe
        elif len(self.fringe) > 0:
            source = self.fringe
        else:
            source = self.danger
        goal = source.pop()
        self.plan = self.path_plan(self.shortest_path(goal))
        action = self.plan.pop()
        print "action: ", action_prin[action]
        return action
    
    def main_func(self):

        if self.alive and (not self.gold_picked):
            if len(self.plan) > 0:
                action = self.plan.pop()
            else:
                i, j = (self.pos[0], self.pos[1])
                percept = self.world[i][j]
                action = self.wumpus_agent(percept)
            
            self._do(action)
    #find the safe list based on knowledge base        
    def return_safe(self, i, j):
        new = neighbors(i, j) - self.visited
        new -= self.safe
        new -= self.danger
        new_safe = set()
        new_danger = set()
        if (self.world[2][i][j] == 0) and (self.world[4][i][j] == 0):
            self.fringe -= set((i, j))
            new_safe |= new
        else:
            self.fringe |= new
        print "fringe: ", self.fringe
        fringe = self.fringe.copy()
        if len(self.visited) > 1:
            for x in fringe:
                #print(x)
                if self.kb.ask(expr('(P%s%s | W%s%s)' % (x*2))):
                    new_danger.add(x)
                    self.fringe.remove(x) 
                elif self.kb.ask(expr('(~P%s%s & ~W%s%s)' % (x*2))):
                    new_safe.add(x)
                    self.fringe.remove(x)
        if len(new_safe) > 0:
            self.safe |= (new_safe)
        if len(new_danger) > 0:
            self.danger |= new_danger

        print "safe list: ", self.safe
    #function that executes moves for agents and records new positions  
    def _do(self, action):
        facing_dict = {
                facing_list['up']: (0, 1),
                facing_list['right']: (1, 0),
                facing_list['down']: (0, -1),
                facing_list['left']: (-1, 0),
                }
        if action is action_list['forward']:
            dx, dy = facing_dict[self.facing]
            new_pos = (self.pos[0]+dx, self.pos[1]+dy)
            print "new position: ", new_pos
            self.paths.append(new_pos)
            if new_pos in neighbors(*self.pos):

                if new_pos not in self.visited:
                    i, j = new_pos
                    percept = self.world[i][j]
                    print "Perception: ",percept

                    self.visited.add((i, j))
                    if (i, j) in self.safe:
                        self.safe.remove((i, j))
                    self.known_world[i][j] = percept

                    if percept[0] == 2:
                        self.gold_picked = True
                        self._do(action_list['pick'])
                        print "Found the gold!!!"
                        self.end = True
                    elif (percept[1] == 2) or (percept[3] == 2):
                        self.alive = False
                        print "Unfortunately the agent died"
                        self.end=True
                    else:
                        c = 0
                        know = []
                        #save perception of environment into knowledge base
                        for x in percept:
                            if x == 2:
                                know.append("%s%s%s" % (map_list[c], i, j))
                            elif x == 0:
                                know.append("~%s%s%s" % (map_list[c], i, j))
                            c += 1
                        if len(know) > 0:
                            print "Environment perception: ", ' & '.join(know)
                            self.kb.tell(expr(' & '.join(know)))
                        self.return_safe(i, j)
                self.pos = new_pos
                print "Current location: ", self.pos
        elif action is action_list['left']:
            self.facing = (self.facing - 1) % 4
        elif action is action_list['right']:
            self.facing = (self.facing + 1) % 4     
        elif action is action_list['pick']:
            i, j = (self.pos[0], self.pos[1])
            self.world[0][i][j] = 0
            self.gold_picked = True
    #find the shortest path to the goal destination       
    def shortest_path(self, goal):
        g = self.visited
        v = {}
        for x in g:
            v[x] = 625
        v[goal] = 0
        def v_neighbors(i, j, s):
            li = []
            for t in neighbors(i, j):
                 if (t in self.visited) and (t not in s):
                    li.append(t)
            return li
        def get_path(v):
            path = []
            a = self.pos
            t = v[a]
            while t > 1:
                for x in v_neighbors(a[0], a[1], s):
                    if v[x] < t:
                        t = t - 1
                        path.append(x)
                        a = x
                        break
            return path
        s = [goal]
        while (len(s) > 0):
            u = s.pop()
            for x in v_neighbors(u[0], u[1], s):
                if v[x] > v[u] + 1:
                    v[x] = v[u] + 1
                    s.append(x)

        pa = get_path(v)
        pa.append(goal)
        print "Next path: ", pa
        return pa
    #function that returns the actions need be taken to the target path
    def path_plan(self, path):
        plan = []
        prev = self.pos
        prev_facing = self.facing
        for pos in path:
            dx = pos[0] - prev[0]
            dy = pos[1] - prev[1]
            dy_dict = {
                -1: 'down',
                1: 'up',
                0: 'up' #dummy item
                }
            dx_dict = {
                -1: 'left',
                1: 'right',
                0: dy_dict[dy]
                }
            facing = facing_list[dx_dict[dx]]
            d = facing - prev_facing
            if d != 0:
                c = abs(d)
                if c > 2:
                    d = -d
                    c = c % 2
                if d < 0:
                    direction = action_list['left']
                elif d > 0:
                    direction = action_list['right']
                plan.extend([direction] * c)
                prev_facing = facing
            plan.append(action_list['forward'])
            prev = pos
        plan.reverse()
        #print "plan: ", plan
        return plan

class WumpusKB():
    #A KB for wumpus world

    def __init__(self, sentence=None):
        self.k = expr('~P00 & ~W00')

        li = []        
        for i in range(5):
            for j in range(5):
                for l, r in (('B', 'P'), ('S', 'W')):
                    left = "%s%s%s" % (l, i, j)
                    right_list = []
                    for s, t in neighbors(i, j):
                        right_list.append("%s%s%s" % (r, s, t))
                    li.append("(%s <=> (%s))" % \
                              (left, ' | '.join(right_list)))
        e = expr(' & '.join(li))
        self.tell(e)

        # one and only one wumpus
        li = ['W%s%s' % (i, j) for i in range(5) for j in range(5)]
        e = expr(' | '.join(li))
 
        self.tell(e)


        li = ['(~W%s%s | ~W%s%s)' % \
              (i, j, x, y)
              for i in range(5) \
              for j in range(5) \
              for x in range(5) \
              for y in range(5) \
              if not ((i == x) and (j == y))]
        e = expr(' & '.join(li))

        self.tell(e)
    #function that save perception to knowledge base
    def tell(self, s):
        self.k &= s
    #function that extracts information from truth table
    def ask(self, s):
        print "===================="
        print "Check Knowledge Base: ", s
        start = time.time()
        r = dpll_satisfiable(self.k & ~s)
        #print "cost: ", time.time() - start
        if r is False:
            return True
        else:
            return False
#main function that runs the game and saves records to a log file
if __name__ == '__main__':
	b = Agent()
	paths = []
	pick = []
	steps = []
	#modify the number in the parentheses to run games multiple times
	for i in range(2):
		maps = []
		b.build_world()
		while not b.end:
			b.main_func()
		pick.append(b.gold_picked)
		maps.append(return_world(b.world))
		paths.append(b.paths)
		steps.append(len(b.paths))
		print(maps)
	with open("logs.txt", 'w+') as f:
		for i in range(len(paths)):
			f.write("Result: {}\n".format('Win' if pick[i] else 'Die'))
			f.write("Paths:" + "->".join([str(j) for j in paths[i]]) + '\n\n')
			#f.write()
		f.write("win rate: {}/{}({:.0f}%), average steps: {:.2f}".format(sum(pick), len(pick), sum(pick)*100.0/len(pick), numpy.mean(steps)))


