#!/usr/bin/python3


# code for parity game


from random import seed, randint, sample
from copy import deepcopy
import numpy as np

players=['EVEN','ODD '] # player 0 is Eve (wants even), player 1 is Adam (wants odd)


def priority_smaller(p1, p2):  # returns True if priority p1 is "smaller" than p2 for the natural order relation
    i1 = p1 % 2
    i2 = p2 % 2
    if (i1,i2)==(0,0):
        return (p1<=p2)
    elif (i1,i2)==(1,1):
        return (p2<=p1)
    elif (i1,i2)==(0,1):
        return False
    else:
        return True

def priority_max(l): # returns the max of a list
    m=l[0]
    for i in range(1,len(l)):
        if priority_smaller(m,l[i]):
            m=l[i]
    return m

def priority_min(l): # returns the min of a list
    m=l[0]
    for i in range(1,len(l)):
        if priority_smaller(l[i],m):
            m=l[i]
    return m


class state:

    def __init__(self, nb, player, next_states, priority):
        self.nb = nb
        self.player = player
        self.next_states = next_states
        self.priority = priority

    def print(self, end=''):
        print("State",self.nb, "player:",self.player,players[self.player],"next_states:",self.next_states,"priority:",self.priority, end=end)
        

class parity_game:   
    
    def __init__(self, nb_states, nb_actions, nb_priorities): # init a random parity game

        self.states = [ state( i, #  state number,
                               randint(0,1),   # random player
                               [randint(0, nb_states-1) for a in range(nb_actions)],  # random next states
                               randint(0,nb_priorities-1) )   #  priority
                        for i in range(nb_states) ]

    def print(self):
        
        for state in self.states:
            state.print(end="\n")


    # ZIELONKA ALGORITHM

    def attractor(self, i, U): #  computes the attractor of set U for player i 
        
        oldattr = set()
        attr = U.copy()

        while( attr != oldattr ):

            oldattr = attr.copy()
            
            for state in self.states:
                if state.player==i:
                    for j in state.next_states:
                        if j in attr:
                            attr.add(state.nb)
                            break
                else: # opponent
                    test = map( lambda j: j in attr, state.next_states )
                    if False not in test:
                        attr.add(state.nb)
                        
        return attr


    def copy_and_remove(self, A):  # remove nodes of the set A
        
        g = deepcopy(self)
        
        oldB = set()
        B = A.copy()

        while (B != oldB):

            oldB = B.copy()
            
            for state in g.states.copy():  # (copy is important)
                if state in g.states and state.nb in B:
                    g.states.remove(state)
                else:
                    for j in B:
                        if j in state.next_states:
                            state.next_states.remove(j)
                    if state.next_states == []:
                        B.add(state.nb)      # if no more successor, add node for removal

        return g
    
        
    def solve_zielonka(self):  # Zielonka's algorithm
        
        all_priorities = set ( [ state.priority for state in self.states ] )
        all_states = set( [ state.nb for state in self.states ] )
        
        p = max(all_priorities)
        i = p%2
        
        if p==min( [state.priority for state in self.states  ] ):

            W = [ set(), set() ]
            W[i] = all_states
            return W

        U = set ( [ state.nb  for state in self.states if state.priority==p ] )
        A = self.attractor(i, U)
        if A==all_states:
            W = [ set(), set() ]
            W[i] = all_states
            return W

        g2 = self.copy_and_remove(A)
        W2 = g2.solve_zielonka()

        if W2[1-i] == set():

            W = [ set(), set() ]
            W[i] = all_states
            return W

        B = self.attractor(1-i, W2[1-i])
        if B==all_states:
            W = [ set(), set() ]
            W[1-i] = all_states
            return W

        g3 = self.copy_and_remove(B)
        W3 = g3.solve_zielonka() 

        W = [ set(), set() ]
        W[i] = W3[i]
        W[1-i] = W3[1-i].union(B)
        return W


    # ALGORITHM
    # returns a dict with "optimal priorities"              

    def solve(self, txt="", verbose=True): 
        
        all_priorities = set ( [ state.priority for state in self.states ] )
        all_states = set( [ state.nb for state in self.states ] )
        n = len(all_states)
        
        p = max(all_priorities)
        i = p%2

        if verbose:
            print(txt+"Game:")
            self.print()
            print(txt+"* Max priority",p,players[i])

        # terminal condition (one priority)
            
        if p==min( all_priorities ): # only one priority
            P=dict()
            for i in all_states:
                P[i]=p
            return P

        # solve the p/p-1 parity game


        # recursive call to solve the <=p-1 parity problem


        # propagation
        
    
# Main: test the algorithm vs Zielonka

n=4
a=2
d=n


for i in range(0,10000):

    seed(i)
    g = parity_game(n,a,d)
    
    print("* Seed=",i)    
    g.print()
    
    W = g.solve_zielonka()
    print("Solution (Zielonka):",W,"\n")
    
    P = g.solve(verbose=True)
    W2 = [ set(), set() ]
    for x in range(n):
        W2[ P[x]%2 ].add(x)
        
    print("Solution:",P,W2,"\n\n")
    
    if W!=W2:
        print("STOP")
        exit(1)
