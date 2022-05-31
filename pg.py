#!/usr/bin/python3


# code for parity game / optimal priority


from random import seed, randint, sample
from copy import deepcopy
import numpy as np

# 

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

    def print(self, end='',txt=''):
        print(txt+"State",self.nb, "player:",self.player,players[self.player],"next_states:",self.next_states,"priority:",self.priority, end=end)
        

class parity_game:   
    
    def __init__(self, nb_states, nb_actions, nb_priorities): # init a random parity game

        self.states = [ state( i, #  state number,
                               randint(0,1),   # random player
                               [randint(0, nb_states-1) for a in range(nb_actions)],  # random next states
                               randint(1,nb_priorities) )   #  priority
                        for i in range(nb_states) ]

    def print(self,txt=''):
        
        for state in self.states:
            state.print(end="\n",txt=txt)


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
                        while True:
                            if j not in state.next_states:
                                break
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


    # ALGORITHM optimal priority (through Zielonka)

    def optimal_priority(self, pmax=np.infty, txt="", verbose=False): 
        
        all_priorities = set ( [ state.priority for state in self.states  if state.priority<=pmax ] )
        all_states = set( [ state.nb for state in self.states ] )
        n = len(all_states)
        
        p = max(all_priorities)
        i = p%2

        P = dict()
        
        if verbose:
            print(txt+"Game:")
            self.print()
            print(txt+"* Max priority",p,players[i])

        # terminal condition

        if p==min( all_priorities ): # only one priority

            for s in all_states:
                P[s]=p

            return P

        # solve the (p, <=p-1) parity game
        
        g = deepcopy(self)
        for state in g.states:
            if state.priority<p:
                state.priority=p-1

        W = g.solve_zielonka()

        for s in W[i]:
            P[s]=p

        if W[i]==all_states:
            return P
            
        g2 = self.copy_and_remove(W[i])
        P2 = g2.optimal_priority(pmax=p-1, verbose=verbose)

        for s in W[1-i]:
            P[s]=P2[s]

        return P
        


    def solve(self, txt="", verbose=True):

        all_priorities = set ( [ state.priority for state in self.states ] )
        all_states = set( [ state.nb for state in self.states ] )
        n = len(all_states)
        
        p = max(all_priorities)
        i = p%2

        W = [ set(), set() ]
        
        if verbose:
            print(txt+"Game to solve:")
            self.print(txt)
            print(txt+"* Max priority",p,players[i])

        # Terminal condition
        
        if p==min( all_priorities ): # only one priority

            W[i]=all_states
            if verbose:
                print(txt+"Terminal condition 1 with W =",W)
            return W

        # Form and solve the (p, <=p-1) parity game
        
        g2 = deepcopy(self)

        for state in g2.states:
            if state.priority<p:
                state.priority=p-1
        
        W2 = g2.solve_zielonka()
        A = W2[i]

        if verbose:
            print(txt+"A =",A)
        
        if A==all_states:
            W[i]=A
            return W

        g2 = g2.copy_and_remove(A)
        
        
        for state in g2.states:
            if state.priority==p:
                state.priority=[1,-1][i]
            else:
                state.priority=0
                
        # Find the limiting cycles with value 0

        C = set()
        
        while True:

            all_states2 = set( [ state.nb for state in g2.states ] )

            N = n
            v = dict()
            for state in g2.states:
                v[state.nb]=0

            for t in range(N):
                v2 = v.copy()
                for state in g2.states:
                    l = [ v2[s2] for s2 in state.next_states ]
                    if state.player==0: # EVEN/MAX
                        v[state.nb] = state.priority + max(l)
                    else: # ODD/MIN
                        v[state.nb] = state.priority + min(l)


            B = set( [ i for i in all_states2 if v[i]==0 ] )
            C = C.union(B)
            
            if verbose:
                print(txt+"B =",B)

            D = g2.attractor(1-i,B)
            if D==all_states2:
                break

            g2 = g2.copy_and_remove(D)

        if verbose:
            print("C =",C)
                
        # Terminal condition 2
                        
        Cc = all_states.difference(C)
        g3 = self.copy_and_remove(Cc)

        W3 = g3.solve_zielonka() # for testing
        #        W3 = g3.solve(txt+"   ",verbose)

        if verbose:
            print(txt+"W3 =",W3)
            
        # propagation on from C to G4

        if verbose:
            print(txt+"Propagation")

        g4 = deepcopy(self)
        g4 = g4.copy_and_remove(A)
            
        v = dict()
        for state in g4.states:
            if state.nb in W3[i]:
                v[state.nb]=[1,-1][i]
            elif state.nb in W3[1-i]:
                v[state.nb]=[-1,1][i]
            else:
                v[state.nb]=0
            
        while True:
            if verbose:
                print(txt,v)
            v2 = v.copy()
            for state in g4.states:
                if state.nb not in C:
                    l = [ v2[s2] for s2 in state.next_states if v2[s2] in [-1,1] ]
                    while 0 in l:
                        l.remove(0)
                    if l!=[]:
                        if state.player==0: # EVEN/MAX
                            v[state.nb] = max(l)
                        else: # ODD/MIN
                            v[state.nb] = min(l)
            if v==v2:
                break
                        
        W[0] = set( [ s for s in v if v[s]==1 ] ) 
        W[1] = set( [ s for s in v if v[s]==-1 ] )
        W[i] = W[i].union(A)
        
        if verbose:
            print(txt+"Return W =",W)
        
        return W


    
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
    
    P2 = g.optimal_priority()
    W2 = [ set(), set() ]
    for i in range(n):
        W2[ P2[i]%2 ].add(i)
    
    print("Solution (optimal priority):",P2,W2,"\n\n")
    
    if W!=W2:
        print("STOP")
        exit(1)

    W3 = g.solve()

    print("Solution (solve):",W3,"\n\n")

    if W2!=W3:
        print("STOP")
        exit(1)
