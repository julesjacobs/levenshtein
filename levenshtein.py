class LevenshteinAutomaton:
    def __init__(self, string, n):
        self.string = string
        self.max_edits = n

    def start(self):
        return range(len(self.string)+1)

    def step(self, state, c):
        new_state = [state[0]+1]
        for i in range(len(state)-1):
            cost = 0 if self.string[i] == c else 1
            new_state.append(min(new_state[i]+1, state[i]+cost, state[i+1]+1))
        return [min(x,self.max_edits+1) for x in new_state]

    def is_match(self, state):
        return state[-1] <= self.max_edits

    def can_match(self, state):
        return min(state) <= self.max_edits

    def transitions(self, state):
        return set(c for (i,c) in enumerate(self.string) if state[i] <= self.max_edits)



class SparseLevenshteinAutomaton:
    def __init__(self, string, n):
        self.string = string
        self.max_edits = n

    def start(self):
        return (range(self.max_edits+1), range(self.max_edits+1))

    def step(self, (indices, values), c):
        if indices and indices[0] == 0 and values[0] < self.max_edits:
            new_indices = [0]
            new_values = [values[0] + 1]
        else:
            new_indices = []
            new_values = []

        for j,i in enumerate(indices):
            if i == len(self.string): break
            cost = 0 if self.string[i] == c else 1
            val = values[j] + cost
            if new_indices and new_indices[-1] == i:
                val = min(val, new_values[-1] + 1)
            if j+1 < len(indices) and indices[j+1] == i+1:
                val = min(val, values[j+1] + 1)
            if val <= self.max_edits:
                new_indices.append(i+1)
                new_values.append(val)

        return (new_indices, new_values)

    def is_match(self, (indices, values)):
        return bool(indices) and indices[-1] == len(self.string)

    def can_match(self, (indices, values)):
        return bool(indices)

    def transitions(self, (indices, values)):
        return set(self.string[i] for i in indices if i < len(self.string))



# use the automaton to build a DFA

counter = [0] # list is a hack for mutable lexical scoping
states = {}
transitions = []
matching = []

lev = SparseLevenshteinAutomaton("woof", 10)

def explore(state):
    key = (tuple(state[0]),tuple(state[1])) # lists can't be hashed in Python because they are mutable, so convert to a tuple
    if key in states: return states[key]
    i = counter[0]
    counter[0] += 1
    states[key] = i
    if lev.is_match(state): matching.append(i)
    for c in lev.transitions(state) | set(['*']):
        newstate = lev.step(state, c)
        j = explore(newstate)
        transitions.append((i, j, c))
    return i

explore(lev.start())

transitions.sort(key=lambda (i,j,c): i)

# output to graphviz

print "digraph G {"
for t in transitions:
    print '%s -> %s [label=" %s "]' % t
for i in matching:
    print '%s [style=filled]' % i
print "}"



# test that the two automata are equivalent
# let's hope that they are not both broken in the same way

words = ["banana", "bananas", "cabana", "foobarbazfoobarbaz", "a", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", ""]

for n in [0,1,2,3,4]:
    for word in words:
        dense = LevenshteinAutomaton(word, n)
        sparse = SparseLevenshteinAutomaton(word, n)
        for query in words:
            s_dense = dense.start()
            s_sparse = sparse.start()
            for c in query:
                if word == "banana" and query == "cabana" and n==2: print s_dense
                s_dense = dense.step(s_dense, c)
                s_sparse = sparse.step(s_sparse, c)
                assert dense.is_match(s_dense) == sparse.is_match(s_sparse)
                assert dense.can_match(s_dense) == sparse.can_match(s_sparse)