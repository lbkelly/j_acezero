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

class Gene:
    """
    The gene class represents the individuals inside the chromosome.
    Each gene will have a value and also a min and max value.
    The min and max value represent the range in which the gene can have legal values.
    """
    def __init__(self, min, max):
        """
        Represents the gene
        :param min: minimum values the gene can have
        :param max: maximum value the gene can have
        """
        self.value = random.uniform(min, max)
        self.min = min
        self.max = max

    def __str__(self):
        return self.value


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

POP = 15
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

    pop = toolbox.population()

    seed1 = [94.0820311628, -3.83082483789, 4192.82077028, 0, 1225.62656806]
    seed2 = [89.4782659787, 12.979966073, 8341.32788961, 4.0506110747, 627.580417707]
    seed3 = [23.5424585658, -24.2420447968, 6876.71780188, 3.85164109202, 1022.73605523]
    seed4 = [21.8943490395, -43.4139647345, 2757.37932662, 3.53570992358, 1576.78975357]
    seed5 = [19.0845352215, 16.8278356614, 9045.44504623, 4.1513290427, 1157.29517053]
    seed6 = [78.8615624369, -3.56944253876, 3577.6184331, 0.681792895222, 1126.38921114]
    seed7 = [5.12763406892, 9.37000095909, 2047.96788888, 0, 880.347944709]
    seed8 = [0.980120974347, -53.1132821889, 0, 0, 754.463563311]
    seed9 = [16.5174154426, 84.8568875558, 3375.53417114, 4.57038314546, 2543.51727949]
    seed10 = [25.9581981794, -8.3422215685, 8469.75252226, 3.1040012365, 1411.21002597]
    seed11 = [100, -12.8639224686, 8117.33377188, 3.91679884808, 2116.13069719]
    seed12 = [84.677486545, 4.71979989461, 5371.82306846, 0.742398485613, 2327.0649098]
    seed13 = [30.3914643877, -27.9426429929, 8684.49085877, 4.95592491826, 1544.17105876]
    seed14 = [63.2334383172, 12.7714283222, 10295.6952369, 4.39109967622, 2398.14575284]
    seed15 = [76.1287028679, -4.35076241639, 5379.19719717, 0.60335430442, 990.663910846]

    seeds = [seed1, seed2, seed3, seed4, seed5, seed6, seed7, seed8, seed9, seed10, seed11, seed12, seed13, seed14, seed15]

    for ind_indx, ind in enumerate(pop):
        for gene_index, gene in enumerate(ind):
            gene.value = seeds[ind_indx][gene_index]

    cp = dict(population=pop, generation=1, rndstate=random.getstate())

    with open("r1_testset.pkl", "wb") as cp_file:
        cPickle.dump(cp, cp_file)

    return pop

if __name__ == "__main__":
    main()