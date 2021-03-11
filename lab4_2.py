
###############################################
### CMPLXSYS425 - Evolution in silico       ###
### Lab 4.2 -- GP 2.0                       ###
### ####################################### ###

### ####################################### ###
### NOTE: Feel free to delete the comments  ###
### anywhere that you don't need them!      ###
### ####################################### ###

#Import our GPNodes from the last lab! 
from OurGP import GPNode, GPConstNode, GPVariableNode, GPFunctionNode
import numpy as np

# Now let's build a class for our GP Individuals! 

class GPIndividual:
    # This is the beef of the individual code. We're growing random 
    # trees with a bit of extra sauce. 
    # We've defined a prob_terminal value that determines how 
    # likely it is that we select a terminal when choosing a random GP node. 
    # We're also limiting the depth of the trees we grow, because this is 
    # Python after all. 
    def grow_random(self, cur_node=None, cur_depth=0):
        if (np.random.random() < self.prob_terminal 
            or cur_depth == self.max_genotype_depth-1):
            new_node = np.random.choice(self.terminal_set).deepcopy()
            new_node.parent = cur_node
            new_node.depth = cur_depth
        else:
            new_node = np.random.choice(self.function_set).deepcopy()
            new_node.depth = cur_depth
            new_node.parent = cur_node
            for i in range(new_node.argument_count):
                new_node.add_child(self.grow_random(cur_node=new_node, 
                                                    cur_depth=cur_depth+1))
        return new_node
    
    
    # prob_terminal and max_depth have default parameters but you 
    # can use them to control how big the trees can get and how
    # likely you are to pick function/terminal nodes when growing
    # and mutating trees. 
    def __init__(self, function_set, terminal_set, 
                 prob_terminal=0.2, max_depth=5):
        self.max_genotype_depth = max_depth
        self.fitness = None
        self.function_set = function_set
        self.terminal_set = terminal_set
        self.prob_terminal = prob_terminal
        
        self.genotype = self.grow_random()
        
        
    def pretty_print(self):
        self.genotype.pretty_print()
        
        
    def deepcopy(self):
        new_individual = GPIndividual(self.function_set, 
                                      self.terminal_set, 
                                      self.prob_terminal, 
                                      self.max_genotype_depth)
        new_individual.genotype = self.genotype.deepcopy()
        return new_individual
    
    
    # This function just visits each node in the genome, growing
    # the list of nodes as it encounters children. 

    # This is useful to do something to every node, or pick one randomly. 
    def visit_genotype_nodes(self, cur_node=None):
        if cur_node == None: 
            cur_node = self.genotype
            
        node_list = [cur_node]
        visitor_index = 0
        
        while visitor_index < len(node_list):
            if len(node_list[visitor_index].children) > 0:
                node_list.extend(node_list[visitor_index].children)
            visitor_index += 1
            
        return node_list
        
    
    def evaluate(self, input_state):
        #evaluate the genotype
        return self.genotype.evaluate(input_state)
        
        
    def mutate(self):
        # get a list of nodes...
        genotype_nodes = self.visit_genotype_nodes()
        # and pick one! 
        random_node = np.random.choice(genotype_nodes)
        
        # There is a lot that could be done better to this mutation function!
        # See some ideas in Lecture 11.

        if random_node.parent == None:
            #We've picked the root, so just grow a whole new genotype
            self.genotype = self.grow_random()
        else:
            #generate a new subtree using the random node's parent
            #as the parent for this subtree
            new_node = self.grow_random(random_node.parent, random_node.depth)
            #remove old node, add new node to parent's list of children
            random_node.parent.children.remove(random_node)
            random_node.parent.add_child(new_node)

### ####################################### ###
### Now, to build an individual we'll need  ###
### to build our library of nodes!          ###
### ####################################### ###

# I'm using something you might not have seen before, it's the bit
# starting with lambda x,y.
# This is called an anonymous function because it doesn't ever get a name
# and you can think of it like a miniture version of "def function(params):".
gp_add = GPFunctionNode(arg_count=2, func_name="Add", gp_function=lambda x, y: x+y)
gp_sub = GPFunctionNode(arg_count=2, func_name="Sub", gp_function=lambda x, y: x-y)

gp_const1 = GPConstNode(42)
gp_const2 = GPConstNode(3.14)
gp_var1 = GPVariableNode(variable_name='x')

gp_func_set = [gp_add, gp_sub]
gp_term_set = [gp_const1, gp_const2, gp_var1]

# Now let's finally build a random individual!
gp_ind = GPIndividual(function_set=gp_func_set, terminal_set=gp_term_set)
gp_ind.pretty_print()

print( gp_ind.evaluate({'x':2.5}) )
# Try running this growth 10ish times to see the kinds of trees you get!
# Did you get any that had only a terminal node? 

# When you've made your way through this code and feel like you have a 
# good sense for what's going on, move on to lab4_3.py! 

# Oh, and don't forget to change the .replit file to 
# run lab4_3.py instead of 4_2!