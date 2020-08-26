import helpers
import random
import csv
import os
import sys
import visualization
import hall_off_fame as hof
from deap import tools, base, creator

import itertools
import cPickle

"""
The second chromosome used. Allows all state transitions
"""

__author__ = 'jjwimbridge'


class Gene:
    """
    The template for the genes in the chromosome.
    """
    def __init__(self, min, max, left):

        if left:
            self.value = random.uniform(min, 0)
        else:
            self.value = random.uniform(0, max)

    def __str__(self):
        return self.value

    def set_min_max(self, min, max):
        self.min = min
        self.max = max

# Set up the toolbox from base
toolbox = base.Toolbox()

# set up the fitness component and the chromosome using that fitness
creator.create("fitness", base.Fitness, weights=(1.0,))
creator.create("Tactic", list, fitness=creator.fitness)

# The minimum and maximum values that the three measures can have
MIN_DISTANCE, MAX_DISTANCE = -48152, 48152
MIN_VELOCITY, MAX_VELOCITY = -1000, 1000
MIN_ACCEL, MAX_ACCEL = -100, 100

# need the chromosome to repeat the data 12 times as there are 12 state transitions
CYCLES = 12

# sets the specs for the run
POP = 45

HOF_SIZE = POP

# set evolutionary operators
toolbox.register("mate", tools.cxOnePoint)
toolbox.register("evaluate", helpers.evaluate)


# Initialise all the gene's to be used in the chromosome.
toolbox.register("px_min", Gene, MIN_DISTANCE, MAX_DISTANCE, True)
toolbox.register("px_max", Gene, MIN_DISTANCE, MAX_DISTANCE, False)
toolbox.register("py_min", Gene, MIN_DISTANCE, MAX_DISTANCE, True)
toolbox.register("py_max", Gene, MIN_DISTANCE, MAX_DISTANCE, False)
toolbox.register("pz_min", Gene, MIN_DISTANCE, MAX_DISTANCE, True)
toolbox.register("pz_max", Gene, MIN_DISTANCE, MAX_DISTANCE, False)
toolbox.register("vx_min", Gene, MIN_VELOCITY, MAX_VELOCITY, True)
toolbox.register("vx_max", Gene, MIN_VELOCITY, MAX_VELOCITY, False)
toolbox.register("vy_min", Gene, MIN_VELOCITY, MAX_VELOCITY, True)
toolbox.register("vy_max", Gene, MIN_VELOCITY, MAX_VELOCITY, False)
toolbox.register("vz_min", Gene, MIN_VELOCITY, MAX_VELOCITY, True)
toolbox.register("vz_max", Gene, MIN_VELOCITY, MAX_VELOCITY, False)
toolbox.register("ax_min", Gene, MIN_ACCEL, MAX_ACCEL, True)
toolbox.register("ax_max", Gene, MIN_ACCEL, MAX_ACCEL, False)
toolbox.register("ay_min", Gene, MIN_ACCEL, MAX_ACCEL, True)
toolbox.register("ay_max", Gene, MIN_ACCEL, MAX_ACCEL, False)
toolbox.register("az_min", Gene, MIN_ACCEL, MAX_ACCEL, True)
toolbox.register("az_max", Gene, MIN_ACCEL, MAX_ACCEL, False)

# Initialize the structure of the chromosome
# Sets tactic as a Tactic object and populates it with genes from gene template
toolbox.register("tactic", tools.initCycle, creator.Tactic, (toolbox.px_min,
                                                              toolbox.px_max,
                                                              toolbox.py_min,
                                                              toolbox.py_max,
                                                              toolbox.pz_min,
                                                              toolbox.pz_max,
                                                              toolbox.vx_min,
                                                              toolbox.vx_max,
                                                              toolbox.vy_min,
                                                              toolbox.vy_max,
                                                              toolbox.vz_min,
                                                              toolbox.vz_max,
                                                              toolbox.ax_min,
                                                              toolbox.ax_max,
                                                              toolbox.ay_min,
                                                              toolbox.ay_max,
                                                              toolbox.az_min,
                                                              toolbox.az_max), n=CYCLES)

# create the population initializer
toolbox.register("population", tools.initRepeat, list, toolbox.tactic, POP)

def main():
    i = 0
    test_set = []

    # Load the test set from the pickle file
    with open("checkpoint2.pkl", "r") as cp_file:
        cp = cPickle.load(cp_file)
    test_set = cp["population"]

    # create out file
    text_file = 'test.txt'
    sys.stdout = open(text_file, 'w')

    # Print the 5 best GP inds
    print 'Test set for park states'
    for index, x in enumerate(test_set):
        print index + 1, ':'
        print helpers.list_to_string(x), 'GP: ', x.fitness.values[0]



    # while i < 15:
    #     i+=1
    #     contenders = toolbox.population()
    #
    #     for index, chromosome in enumerate(contenders):
    #         viper_params = []
    #         cobra_params = []
    #         viper_params = toolbox.clone(chromosome)
    #         viper_params = helpers.get_params(viper_params)
    #         params = [viper_params, cobra_params]
    #         scores = helpers.test_evaluate(params, 'straight')
    #         chromosome.fitness.values = (scores[0],)
    #
    #     print 'straight: ', i
    #
    #     for index, chromosome in enumerate(contenders):
    #         viper_params = []
    #         cobra_params = []
    #         viper_params = toolbox.clone(chromosome)
    #         viper_params = helpers.get_params(viper_params)
    #         params = [viper_params, cobra_params]
    #         scores = helpers.test_evaluate(params, 'default')
    #         chromosome.fitness.values = (chromosome.fitness.values[0] + scores[0],)
    #
    #     print 'default: ', i
    #
    #     for index, x in enumerate(contenders):
    #         x.fitness.values = (x.fitness.values[0] / 2,)
    #
    #     contenders = tools.selBest(contenders, 5)
    #
    #     for index, x in enumerate(contenders):
    #         x.fitness.values = (0,)
    #
    #     for pair in itertools.combinations(contenders, 2):
    #         viper = pair[0]
    #         cobra = pair[1]
    #         viper_params = []
    #         cobra_params = []
    #         viper_params = toolbox.clone(viper)
    #         viper_params = helpers.get_params(viper_params)
    #         cobra_params = toolbox.clone(cobra)
    #         cobra_params = helpers.get_params(cobra_params)
    #         params = [viper_params, cobra_params]
    #         scores = helpers.test_evaluate(params, "coev")
    #         viper.fitness.values = (viper.fitness.values[0] + scores[0],)
    #         cobra.fitness.values = (cobra.fitness.values[0] + scores[1],)
    #
    #     for index, x in enumerate(contenders):
    #         x.fitness.values = (x.fitness.values[0] / len(contenders),)
    #
    #     test_set += tools.selBest(contenders, 1)
    #     print 'slot ', i, ' filled.'
    #
    # # Fill the dictionary using the dict(key=value[, ...]) constructor
    # cp = dict(population=test_set, generation=i, rndstate=random.getstate())
    #
    # with open("checkpoint2.pkl", "wb") as cp_file:
    #     cPickle.dump(cp, cp_file)

if __name__ == "__main__":
    main()
