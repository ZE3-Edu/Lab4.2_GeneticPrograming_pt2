###############################################
### CMPLXSYS425 - Evolution in silico       ###
### GP Base Classes                         ###
### ####################################### ###

import numpy as np
from matplotlib import pyplot

# This is the code from the Jupyter Notebook 

# Base Class for our GP Node objects
class GPNode:
    def __init__(self, node_type=None):
        self.parent = None
        self.node_type = node_type
        self.children = []
        self.depth = 0

    def add_child(self, child_node):
        child_node.depth = self.depth+1
        self.children.append(child_node)
        child_node.parent = self

# Const Nodes hold a constant value
class GPConstNode(GPNode):
    def __init__(self, value=None):
        super().__init__(node_type="Const")
        self.const_value = value
    
    def evaluate(self, input_state):
        return self.const_value
        
    def pretty_print(self, indents=0):
        print('  '*indents + str(self.const_value) 
              + ' : ' + str(self.depth))
        
    def deepcopy(self):
        new_node = GPConstNode(value=self.const_value)
        new_node.depth = self.depth;
        return new_node
        
# Variable node
class GPVariableNode(GPNode):
    def __init__(self, variable_name=None):
        super().__init__(node_type="Variable")
        self.variable_name = variable_name
    
    def evaluate(self, input_state):
        return input_state[self.variable_name]
    
    def pretty_print(self, indents=0):
        print('  '*indents + str(self.variable_name)
              + ' : ' + str(self.depth))
        
    def deepcopy(self):
        new_node = GPVariableNode(variable_name = self.variable_name)
        new_node.depth = self.depth
        return new_node

# Function Node Base Class
class GPFunctionNode(GPNode):
    def __init__(self, arg_count, func_name=None, gp_function=None):
        super().__init__(node_type="Function")
        self.argument_count = arg_count
        self.gp_function = gp_function
        self.function_name = func_name
        
    def evaluate(self, input_state): 
        assert self.argument_count == len(self.children), \
        'Number of child nodes must match argument count'

        child_results = [c.evaluate(input_state) for c in self.children]
        return self.gp_function(*child_results)

    def pretty_print(self, indents=0):
        print('  '*indents + str(self.function_name) 
              + ' : ' + str(self.depth))
        
        for child in self.children:
            child.pretty_print(indents+1)
        
    def deepcopy(self):
        new_node = GPFunctionNode(self.argument_count, 
                                   self.function_name, 
                                   self.gp_function)
        new_node.depth = self.depth
        
        for child in self.children:
            new_node.add_child(child.deepcopy())
        
        return new_node

# Individiual Expression Tree Organism
class GPIndividual:
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
