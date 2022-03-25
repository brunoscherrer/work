#!/usr/bin/python3


# code for parity game


from random import seed, randint, sample
from copy import deepcopy
import numpy as np

players=['EVEN','ODD '] # player 0 is Eve (wants even), player 1 is Adam (wants odd)


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

    def solve_2v(self,p): # solve problem for which we know that the "value" is p or <=p-1

        W = [ set(), set() ]
        
        i=p%2

        g = deepcopy(self)

        while True:
            
            all_states = set( [ state.nb for state in g.states ] )
            U = set ( [state.nb  for state in g.states if state.priority==p ] )
            A = g.attractor(i, U)
            
            if A==all_states:
                W[i] = W[i].union(all_states)
                return W
            
            B = all_states.difference(A)
            C = g.attractor(1-i,B)
            W[1-i] = W[1-i].union(C)
            g = g.copy_and_remove(C)
                

    
    def solve(self, verbose=False):
        
        W = [ set(), set() ]
        
        all_priorities = sorted (  list( set ( [ state.priority for state in self.states ] ) ) , reverse=True )
        all_states = set( [ state.nb for state in self.states ] )

        g = deepcopy(self)

        if verbose:
            print("List of priorities", all_priorities)
        
        for p in all_priorities:

            remaining_priorities =  set ( [ state.priority for state in g.states ] )
            if p in remaining_priorities:
            
                i = p%2
            
                W1 = g.solve_2v(p)
                
                if verbose:
                    print("States winning with priority",p,":",W1[i])

                W[i] = W[i].union(W1[i])
                    
                if W[0].union(W[1])==all_states:
                    break

                g = g.copy_and_remove(W1[i])
            
                if verbose:
                    print("Current solution:",W)
                    print("Current model:")
                    g.print()
 
        
        return ( W )
         



    
# Main: test the algorithm vs Zielonka

n=3
a=2
d=n


for i in range(0,10000):

    seed(i)
    g = parity_game(n,a,d)
    
    print("* Seed=",i)    
    g.print()
    
    W = g.solve_zielonka()
    print("Solution (Zielonka):",W,"\n")
    
    W2 = g.solve(verbose=True)
    print("Solution:",W2,"\n\n")
    
    if W!=W2:
        print("STOP")
        exit(1)
