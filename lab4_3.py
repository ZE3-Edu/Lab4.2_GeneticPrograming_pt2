### ####################################### ###
### CMPLXSYS425 - Evolution in silico       ###
### Lab 4.3 -- GP 2.0                       ###
### ####################################### ###

# If you made some improvements to your GPIndividual code in lab4_2,
# you should replace the GPIndividual in the OurGP.py file! Otherwise
# your changes won't be reflected here!

from OurGP import GPNode, GPConstNode, GPVariableNode, GPFunctionNode, GPIndividual
import numpy as np
from matplotlib import pyplot as plt

# Bring our nodes back to life! 
gp_add = GPFunctionNode(arg_count=2, func_name="Add", gp_function=lambda x, y: x+y)
gp_sub = GPFunctionNode(arg_count=2, func_name="Sub", gp_function=lambda x, y: x-y)

gp_const1 = GPConstNode(42)
gp_const2 = GPConstNode(3.14)
gp_var1 = GPVariableNode(variable_name='x')

gp_func_set = [gp_add, gp_sub]
gp_term_set = [gp_const1, gp_const2, gp_var1]


# Let's build a Population class now! 

class GPPopulation:
    # It'll need our node sets and a bit of other info from us
    def __init__(self, pop_size, function_set, terminal_set, max_depth, prob_terminal):
        self.pop_size = pop_size
        self.terminal_set = terminal_set
        self.function_set = function_set
        self.max_depth = max_depth
        self.prob_terminal = prob_terminal
        
        # Grow a population of random individualss
        self.population = [GPIndividual(self.function_set, 
                                        self.terminal_set,
                                        self.prob_terminal, 
                                        self.max_depth) 
                           for _ in range(self.pop_size)]
    # Instead of putting our fitness function code here, 
    # we can do this neat trick of passing a *function* to another function! 
    # And then, we can just call that function here to get the fitness. 
    def update_fitnesses(self, fitness_function):
        fitnesses = []
        for individual in self.population:
            individual.fitness = fitness_function(individual)
            fitnesses.append(individual.fitness)
            
        return fitnesses 
    
    #  We'll use that same trick for the selection_function, so we can swap
    #  in and out different methods you've tried (like proportional selection,
    #  or tournament selection). 
    def do_timestep(self, fitness_function, selection_function, mutation_prob):

        # We'll update every individual's fitness so that the selection function
        # doesn't need to know any details about the fitness calculation
        fitness_list = self.update_fitnesses(fitness_function)

        # Then we can just call the selection_function pop_size times! 
        selected_individuals = [selection_function(self.population) 
                                for _ in range(self.pop_size)]
        
        for individual_idx in range(len(selected_individuals)):
            individual = selected_individuals[individual_idx].deepcopy()
            
            if np.random.random() < mutation_prob:
                individual.mutate()
            
            selected_individuals[individual_idx] = individual
        
        self.population = selected_individuals
        
        return fitness_list

# Now let's write a fitness function and selection function!

# Let's just say that the fitness of our individual is the sum of it's 
# tree evaluated at 10 points between 0 and 1.
def simple_fitness_function(gp_individual):
    x_eval_points = np.linspace(start=0, stop=10, num=10)
    eval_outputs = [gp_individual.evaluate({'x':x}) for x in x_eval_points]

    return np.sum(eval_outputs)

# Our selection function will get the list of individuals
# and should return an organism selected to reproduce

# When this function is called, each individual wll have
# been assigned a fitness value already! But, you'll have
# to write a better (working) selection function.
def bad_selection_function(gp_pop_list):
    return np.random.choice(gp_pop_list)


# ########################################  ###
#    Now we can finally run our GP!         ###
# ########################################  ###
num_generations = 20

gp_pop = GPPopulation(pop_size=100, 
                      function_set=gp_func_set, 
                      terminal_set=gp_term_set,
                      max_depth=6,
                      prob_terminal=0.2)

avg_fitnesses = []

for generation in range(num_generations):
    fitnesses = gp_pop.do_timestep(fitness_function=simple_fitness_function, 
                        selection_function=bad_selection_function,
                        mutation_prob=0.1)
    
    avg_fitnesses.append(np.mean(fitnesses))

plt.plot(avg_fitnesses)
plt.xlabel("Generation")
plt.ylabel("Average Fitness")
plt.show()

### Well, that's not great is it...
### Now it's your turn to implement a better selection function

# ########################################  ###
### Then, try writing a more interesting selection function! 

### What happens when you try to evolve a more complex function?

### See if you can get close to a sin(x) function without any
### trig Function Nodes! 
# ########################################  ###
