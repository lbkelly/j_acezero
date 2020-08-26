import write_chromosome as writer
import write_initial_values as initial_vals
import helpers
import random
import visualization
import datetime
import sys
import csv
import hall_off_fame as hof
from deap import tools, base, creator, algorithms
import os
import math
import itertools
import cPickle
from helpers import Gene as Gene

# class Gene:
#     """
#     The gene class represents the individuals inside the chromosome.
#     Each gene will have a value and also a min and max value.
#     The min and max value represent the range in which the gene can have legal values.
#     """
#     def __init__(self, min, max):
#         """
#         Represents the gene
#         :param min: minimum values the gene can have
#         :param max: maximum value the gene can have
#         """
#         self.value = random.uniform(min, max)
#         self.min = min
#         self.max = max
#
#     def __str__(self):
#         return self.value


creator.create("fitness", base.Fitness, weights=(1.0,))
creator.create("Tactic", list, fitness=creator.fitness)

toolbox = base.Toolbox()

min_turn_range, max_turn_range = 0.1, 100
min_turn_angle, max_turn_angle = -90, 90
min_displ, max_displ = 0, 180000
min_conv_range, max_conv_range = 0, 30
min_closer_range, max_closer_range = 500, 3000

# sets hof and fs on/off
FS = 0
HOF = 0

POP = 45
GENS = 10
REPS = 1

CROSS_PROB = 0.6
MUT_PROB = 1.0
IND_MUT_PROB = 0.1
HOF_SIZE = POP

CYCLES = 1

# create gene templates
toolbox.register("turn_range", Gene, min_turn_range, max_turn_range)
toolbox.register("turn_angle", Gene, min_turn_angle, max_turn_angle)
toolbox.register("desired_displ", Gene, min_displ, max_displ)
toolbox.register("conv_range", Gene, min_conv_range, max_conv_range)
toolbox.register("no_closer_range", Gene, min_closer_range, max_closer_range)
# create chromosome template
toolbox.register("tactic", tools.initCycle, creator.Tactic, (toolbox.turn_range,
                                                             toolbox.turn_angle,
                                                             toolbox.desired_displ,
                                                             toolbox.conv_range,
                                                             toolbox.no_closer_range), n=CYCLES)
# create population template
toolbox.register("population", tools.initRepeat, list, toolbox.tactic, POP)

# set evolutionary operators
toolbox.register("mate", tools.cxOnePoint)
toolbox.register("mutate", helpers.gaussian, mu=0, sigma=0.2, indpb=IND_MUT_PROB)
toolbox.register("select", tools.selStochasticUniversalSampling)
toolbox.register("evaluate", helpers.evaluate)

def main():
    i = 0
    test_set = []

    with open("checkpoint3.pkl", "r") as cp_file:
        cp = cPickle.load(cp_file)
    test_set = cp["population"]

    for index, x in enumerate(test_set):
        print helpers.list_to_string(x)
    # while i < 15:
    #     i += 1
    #     contenders = toolbox.population()
    #
    #     for index, x in enumerate(contenders):
    #         viper_params = (x[0].value, x[1].value, x[2].value, x[3].value, x[4].value)
    #         cobra_params = (x[0].value, x[1].value, x[2].value, x[3].value, x[4].value)
    #         scores = helpers.test_evaluate(viper_params, cobra_params, "straight")
    #         x.fitness.values = (scores[0], )
    #
    #     for index, x in enumerate(contenders):
    #         viper_params = (x[0].value, x[1].value, x[2].value, x[3].value, x[4].value)
    #         cobra_params = (x[0].value, x[1].value, x[2].value, x[3].value, x[4].value)
    #         scores = helpers.test_evaluate(viper_params, cobra_params, "default")
    #         x.fitness.values = (x.fitness.values[0] + scores[0], )
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
    #         viper_params = (viper[0].value, viper[1].value, viper[2].value, viper[3].value, viper[4].value)
    #         cobra_params = (cobra[0].value, cobra[1].value, cobra[2].value, cobra[3].value, cobra[4].value)
    #         scores = helpers.test_evaluate(viper_params, cobra_params, "coev")
    #         viper.fitness.values = (viper.fitness.values[0] + scores[0],)
    #         cobra.fitness.values = (cobra.fitness.values[0] + scores[1],)
    #
    #     for index, x in enumerate(contenders):
    #         x.fitness.values = (x.fitness.values[0] / len(contenders),)
    #
    #     test_set += tools.selBest(contenders, 1)
    #
    # # Every two generations, save the algorithm state to a dictionary and "pickle" (serialize) out to a file
    #
    # # Fill the dictionary using the dict(key=value[, ...]) constructor
    # cp = dict(population=test_set, generation=i, rndstate=random.getstate())
    #
    # with open("checkpointpppp.pkl", "wb") as cp_file:
    #     cPickle.dump(cp, cp_file)


if __name__ == "__main__":
    main()