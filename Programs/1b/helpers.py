import json
import math
import decimal
import random
from collections import Sequence
from itertools import repeat
from os import path
from operator import attrgetter
import numpy as np
import itertools
from concurrent.futures import ProcessPoolExecutor as Executor
from concurrent.futures import as_completed
from deap import tools, base


import ace_zero
import utils as ut

from pathos.multiprocessing import _ProcessPool as Pool
from contextlib import closing

toolbox = base.Toolbox()

"""
A script that contains methods that will help the the DEAP
application.

"""

__author__ = 'lbkelly'


def multi_evaluate(repetitions):
    """
    To be called when a chromosome needs to be evaluated.
    Ace0 will provide the fitness score.

    :param repetitions: number of times for the simulation to run
    :return: a fitness score for the chromosome as a float
    """
    # hold the total fitness
    total_fitness = 0

    # process pool operator creates/ submits as many process's as we need to evaluate the chromosome
    with Executor(max_workers=5) as executor:
        processes = [executor.submit(ace_zero.return_fitness_ace_zero) for x in range(repetitions)]
        # as the processes are completed, they are summed up
        for f in as_completed(processes):
            try:
                total_fitness += f.result()
            except ValueError:
                print 'Multiprocessing error'

    return total_fitness / repetitions,


def evaluate(parameters):

    viper_params = parameters[0]
    cobra_params = parameters[1]

    return ace_zero.return_fitness_ace_zero(viper_params, cobra_params)


def pathos_multi_evaluate(params):
    with closing(Pool()) as pool:
        value = pool.map(ace_zero.return_fitness_ace_zero, params)
        pool.terminate()
    return value


def sum_pop_v_pop_evals_old(blue_pop, red_pop):
    """
    takes blue and red pop, gets scores of all combinations, appends the score
    to the existing fitness score, returns populations with fitness scores calculated by summing all engagement scores
    (needs to be averaged). Some fitness score must exist before calling.
    :param blue_pop:
    :param red_pop:
    :return:
    """

    temp_blue_population = []
    temp_red_population = []

    size = len(blue_pop)

    # write the parameter values to json file for AceZero and then evaluate
    for index, x in enumerate(blue_pop):
        # update and write to JSON tactical file for (BLUE AGENT)
        # chromosome_parameters.update_blue_chromosome(x[0].value, x[1].value, x[2].value, x[3].value, x[4].value)
        viper_params = (x[0].value, x[1].value, x[2].value, x[3].value, x[4].value)
        temp_blue_population.append(viper_params)

    for ind, y in enumerate(red_pop):
        # update and write to JSON tactical file for (RED AGENT)
        # chromosome_parameters.update_red_chromosome(y[0].value, y[1].value, y[2].value, y[3].value, y[4].value)
        cobra_params = (y[0].value, y[1].value, y[2].value, y[3].value, y[4].value)
        temp_red_population.append(cobra_params)

    combined_params = itertools.product(temp_blue_population, temp_red_population)

    # evaluate with acezero
    scores = pathos_multi_evaluate(combined_params)

    deconstructed = zip(*scores)
    # print deconstructed[0]
    #
    new_blue = deconstructed[0]
    new_red = deconstructed[1]

    final_blue = []
    final_red = []

    for x in xrange(size):
        temp = sum(new_blue[x * size: x * size + size:])
        final_blue.append(temp)


    for x in xrange(size):
        temp = sum(new_red[x::size])
        final_red.append(temp)


    for j, x in enumerate(blue_pop):
        x.fitness.values = x.fitness.values[0] + final_blue[j],


    for j, x in enumerate(red_pop):
        x.fitness.values = x.fitness.values[0] + final_red[j],

    return blue_pop, red_pop


def sum_pop_v_pop_evals(blue_pop, red_pop):
    """
    takes blue and red pop, gets scores of all combinations, appends the score
    to the existing fitness score, returns populations with fitness scores calculated by summing all engagement scores
    (needs to be averaged). Some fitness score must exist before calling.
    :param blue_pop:
    :param red_pop:
    :return:
    """

    temp_blue_population = []
    temp_red_population = []

    size = len(blue_pop)

    # write the parameter values to json file for AceZero and then evaluate
    for index, x in enumerate(blue_pop):
        # update and write to JSON tactical file for (BLUE AGENT)
        # chromosome_parameters.update_blue_chromosome(x[0].value, x[1].value, x[2].value, x[3].value, x[4].value)
        ind = toolbox.clone(x)
        viper_params = get_params(ind)
        #viper_params = (x[0].value, x[1].value, x[2].value, x[3].value, x[4].value)
        temp_blue_population.append(viper_params)

    for ind, y in enumerate(red_pop):
        # update and write to JSON tactical file for (RED AGENT)
        # chromosome_parameters.update_red_chromosome(y[0].value, y[1].value, y[2].value, y[3].value, y[4].value)
        ind = toolbox.clone(y)
        cobra_params = get_params(ind)
        temp_red_population.append(cobra_params)

    combined_params = itertools.product(temp_blue_population, temp_red_population)

    # evaluate with acezero
    scores = pathos_multi_evaluate(combined_params)

    deconstructed = zip(*scores)
    # print deconstructed[0]
    #
    new_blue = deconstructed[0]
    new_red = deconstructed[1]

    final_blue = []
    final_red = []

    for x in xrange(size):
        temp = sum(new_blue[x * size: x * size + size:])
        final_blue.append(temp)


    for x in xrange(size):
        temp = sum(new_red[x::size])
        final_red.append(temp)


    for j, x in enumerate(blue_pop):
        x.fitness.values = x.fitness.values[0] + final_blue[j],


    for j, x in enumerate(red_pop):
        x.fitness.values = x.fitness.values[0] + final_red[j],

    return blue_pop, red_pop

def sum_pop_v_hof_evals(pop, hof):
    """
    takes blue and red pop, gets scores of all combinations, appends the score
    to the existing fitness score, returns populations with fitness scores calculated by summing all engagement scores
    (needs to be averaged). Some fitness score must exist before calling.
    :param blue_pop:
    :param red_pop:
    :return:
    """

    temp_blue_population = []
    temp_red_population = []

    size = len(pop)

    # write the parameter values to json file for AceZero and then evaluate
    for index, x in enumerate(pop):
        # update and write to JSON tactical file for (BLUE AGENT)
        # chromosome_parameters.update_blue_chromosome(x[0].value, x[1].value, x[2].value, x[3].value, x[4].value)
        ind = toolbox.clone(x)
        viper_params = get_params(ind)
        #viper_params = (x[0].value, x[1].value, x[2].value, x[3].value, x[4].value)
        temp_blue_population.append(viper_params)

    for ind, y in enumerate(hof):
        # update and write to JSON tactical file for (RED AGENT)
        # chromosome_parameters.update_red_chromosome(y[0].value, y[1].value, y[2].value, y[3].value, y[4].value)
        ind = toolbox.clone(y)
        cobra_params = get_params(ind)
        #cobra_params = (y[0].value, y[1].value, y[2].value, y[3].value, y[4].value)
        temp_red_population.append(cobra_params)

    combined_params = itertools.product(temp_blue_population, temp_red_population)

    # evaluate with acezero
    scores = pathos_multi_evaluate(combined_params)

    deconstructed = zip(*scores)
    # print deconstructed[0]
    #
    new_blue = deconstructed[0]
    new_red = deconstructed[1]

    final_blue = []
    final_red = []


    for x in xrange(size):
        temp = sum(new_blue[x * len(hof): x * len(hof) + len(hof):])
        final_blue.append(temp)

    for j, x in enumerate(pop):
        x.fitness.values = x.fitness.values[0] + final_blue[j],

    return pop


def test_evaluate(params, agent):
    """
    To be called when a chromosome needs to be evaluated.
    Ace0 will provide the fitness score.

    :param repetitions: number of times for the simulation to run
    :return: a fitness score for the chromosome as a float
    """
    # avg_fitness = 0
    # for x in xrange(repetitions):
    #     avg_fitness += ace_zero.return_fitness_ace_zero()
    # return avg_fitness / repetitions,

    return ace_zero.return_fitness_ace_zero(params, agent)

def convert_range(x, min_range, max_range):
    """
    This is used to convert any gene value to a range between 0 - 1.
    We need the gene ranges to be between 0 - 1 for the gaussian mutation.

    :param x: the original value of the gene
    :param min_range: the min value of the gene
    :param max_range: the max value of the gene
    :return: the normalized value for the gene
    """
    return float((x - min_range)) / float((max_range - min_range))


def change_back(x, min_range, max_range):
    """
    This changed normalized values back to their original value.

    :param x: the original value of the gene
    :param min_range: the min value of the gene
    :param max_range: the max value of the gene
    :return: the rescaled value for the gene
    """
    return float(x * (max_range - min_range)) + min_range


def bounds_check(obj):
    """
    Checks the value after a gene has been mutated.
    If the value is too high/ too low, it will be clipped at the
    min/max value. This is to stop illegal gene values after mutation.

    :param obj: the gene
    :return: none
    """
    if obj.value < obj.min:
        dif = obj.min - obj.value
        obj.value = obj.min + dif
    elif obj.value > obj.max:
        dif = obj.max - obj.value
        obj.value = obj.max + dif


def gaussian(individual, mu, sigma, indpb):
    """
    Customised extended gaussian mutation, the default DEAP method doesn't operate on gene's
    if they are represented by a class.

    :param individual: the chromosome
    :param mu: mean value
    :param sigma: standard deviation
    :param indpb: probability that a gene will get mutated
    :return: the mutated choromosome
    """
    size = len(individual)
    if not isinstance(mu, Sequence):
        mu = repeat(mu, size)
    elif len(mu) < size:
        raise IndexError("mu must be at least the size of individual: %d < %d" % (len(mu), size))
    if not isinstance(sigma, Sequence):
        sigma = repeat(sigma, size)
    elif len(sigma) < size:
        raise IndexError("sigma must be at least the size of individual: %d < %d" % (len(sigma), size))

    for i, m, s in zip(xrange(size), mu, sigma):
        if random.random() < indpb:
            individual[i].value += random.gauss(m, s)


    return individual,


def list_to_string(chromosome):
    """
    Converts each gene value in a chromosome to a string. This is to make it easy to print.

    :param chromosome: The chromosome that will be printed to console
    :return: the gene values as a string
    """
    string = ''
    for i in chromosome:
        string += (str(i.value) + ', ')
    return string


def save_chromosome_to_file(parameters, rel_path):
    """
    Saves out the parameters to a JSON file

    :param parameters: values for the chromosome
    :param rel_path: the file path to save the values into
    :return: None
    """
    try:
        file_path = path.relpath(rel_path)
        temp = json.dumps(parameters)
        with open(file_path, "w") as f:
            f.write(temp)
    except IOError:
        print "File you are writing too doesn't exist"


def euler_angle_rotation(x_angle, y_angle, z_angle, position):
    """
    Rotates the position on the heading, yaw and pitch by the given angles
    :param x_angle: the x angle value to rotate by
    :param y_angle: the y angle value to rotate by
    :param z_angle: the z angle value to rotate by
    :param position: the position to rotate
    :return: an array of the values that represent the newly rotated position
    """
    rotation_matrix = np.matrix([[math.cos(z_angle) * math.cos(y_angle),  math.cos(z_angle) * math.sin(y_angle) * math.sin(x_angle) - math.sin(z_angle) * math.cos(x_angle),  math.cos(z_angle) * math.sin(y_angle) * math.cos(x_angle) + math.sin(z_angle) * math.sin(x_angle)],
                                 [math.sin(z_angle) * math.cos(y_angle),  math.sin(z_angle) * math.sin(y_angle) * math.sin(x_angle) + math.cos(z_angle) * math.cos(x_angle),  math.sin(z_angle) * math.sin(y_angle) * math.cos(x_angle) - math.cos(z_angle) * math.sin(x_angle)],
                                 [-1 * math.sin(y_angle),                 math.cos(y_angle) * math.sin(x_angle),                                                              math.cos(y_angle) * math.cos(x_angle)]])

    position_matrix = np.matrix([[position[0]], [position[1]], [position[2]]])
    rotated_position = np.matmul(rotation_matrix, position_matrix)
    return np.asarray(rotated_position)


def transition_condition(fighter1, fighter2, parameters):
    """
    This is the logic need to transform from one state to another.

    :param fighter1: The attacking fighter
    :param fighter2:  The opponent fighter
    :param parameters: The logical parameters from the chromosome
    :return:
    """
    # get the difference between the two fighters (position, velocity and acceleration)
    difference = ut.delta_parameter(fighter1, fighter2)

    # store the differences as x, y, z so it can be rotated to the attackers orientation
    position = [difference[0], difference[1], difference[2]]
    velocity = [difference[3], difference[4], difference[5]]
    acceleration = [difference[6], difference[7], difference[8]]

    # the positions need to be rotated by the heading, pitch and roll of the attacking fighter
    changed_position = euler_angle_rotation(-1 * math.radians(fighter1[11]),
                                 math.radians(-1 * fighter1[10]),
                                 math.radians(-1 * fighter1[9]), position)
    changed_velocity = euler_angle_rotation(-1 * math.radians(fighter1[11]),
                                                    math.radians(-1 * fighter1[10]),
                                                    math.radians(-1 * fighter1[9]), velocity)
    changed_acceleration = euler_angle_rotation(-1 * math.radians(fighter1[11]),
                                                    math.radians(-1 * fighter1[10]),
                                                    math.radians(-1 * fighter1[9]), acceleration)

    # if Px, Py, Pz, Vx, Vy, Vz, Ax, Ay, Az are between these parameters, the transition is legal
    # Altitude and direction are decoupled. We don't rotate the z position hence "difference[2]"
    if parameters[0] < float(changed_position[0]) < parameters[1] and \
        parameters[2] < float(changed_position[1]) < parameters[3] and \
        parameters[4] < float(difference[2]) < parameters[5]and \
        parameters[6] < float(changed_velocity[0]) < parameters[7] and \
        parameters[8] < float(changed_velocity[1]) < parameters[9] and \
        parameters[10] < float(difference[5]) < parameters[11] and \
        parameters[12] < float(changed_acceleration[0]) < parameters[13] and \
        parameters[14] < float(changed_acceleration[1]) < parameters[15] and \
        parameters[16] < float(difference[8]) < parameters[17]:
        return True
    else:
        return False

def selRankedOld(individuals, k):
    """ Select k individuals with weight for selection based on rank """
    s_inds = sorted(individuals, key=attrgetter("fitness"))
    sum_ranks = 0
    for i in s_inds:
        sum_ranks += s_inds.index(i)+1

    distance = sum_ranks / float(k)
    start = random.uniform(0, distance)
    points = [start + i * distance for i in xrange(k)]

    chosen = []
    for p in points:
        i = 0
        sum_ = 1
        while sum_ < p:
            i += 1
            sum_ += s_inds.index(s_inds[i])+1
        chosen.append(s_inds[i])

    return chosen

def share_fitness_old(pop, niche_rad):
    nr = niche_rad
    for index, x in enumerate(pop):
        ci = 1.0
        for i, y in enumerate(pop):
            # get distance if not the same individual
            if index != i:
                # the sum of the distances between gene values
                ind_dist_sum = 0.0
                for g, gene in enumerate(x):
                    ind_dist_sum = ind_dist_sum + (gene.value - y[g].value)**2
            else:
                continue
            # get the euclidean distance between x and y by sqrt sum
            eucl_dist = math.sqrt(ind_dist_sum)
            if eucl_dist <= nr:
                ci = ci + (1 - (eucl_dist / nr)**1)
        if ci != 0.0 or ci != 0:
            x.fitness.values = x.fitness.values[0] / ci,

    return pop

def share_fitness(pop, niche_rad):
    nr = niche_rad
    for index, x in enumerate(pop):
        ci = 1.0
        for i, y in enumerate(pop):
            # get distance if not the same individual
            if index != i:
                # the sum of the distances between gene values
                ind_dist_sum = 0.0
                for g, gene in enumerate(x):
                    if g == 0:
                        ind_dist_sum = ind_dist_sum + ((gene.value / 100) - (y[g].value / 100)) ** 2
                    elif g == 1:
                        turn_angle_a = (gene.value + 90) / 180
                        turn_angle_b = (y[g].value + 90) / 180
                        ind_dist_sum = ind_dist_sum + (turn_angle_a - turn_angle_b) ** 2
                    elif g == 2:
                        displ_a = gene.value / 180000
                        displ_b = y[g].value / 180000
                        ind_dist_sum = ind_dist_sum + (displ_a - displ_b) ** 2
                    elif g == 3:
                        conv_a = gene.value / 30
                        conv_b = y[g].value / 30
                        ind_dist_sum = ind_dist_sum + (conv_a - conv_b) ** 2
                    elif g == 4:
                        closer_a = (gene.value - 500) / 2500
                        closer_b = (y[g].value - 500) / 2500
                        ind_dist_sum = ind_dist_sum + (closer_a - closer_b) ** 2
            else:
                continue
            # get the euclidean distance between x and y by sqrt sum
            eucl_dist = math.sqrt(ind_dist_sum)
            if eucl_dist <= nr:
                ci = ci + (1 - (eucl_dist / nr)**1)
        if ci != 0.0 or ci != 0:
            x.fitness.values = x.fitness.values[0] / ci,

    return pop

def get_diversityold(pop):
    Dj_sum = 0
    D = 0
    for index_i, i in enumerate(pop):
        for index_j, j in enumerate(pop):
            if index_i != index_j:
                gene_dif = 0.0
                for g, gene in enumerate(i):
                    gene_dif = gene_dif + (gene.value - j[g].value)**2
            else:
                continue

            gene_dif = math.sqrt(gene_dif)

            Dj_sum = Dj_sum + gene_dif
    D = (Dj_sum/len(pop)) / len(pop)
    D = D / 100

    return D

def get_diversity(pop):
    Dj_sum = 0
    D = 0
    for index_i, i in enumerate(pop):
        for index_j, j in enumerate(pop):
            if index_i != index_j:
                gene_dif = 0.0
                for g, gene in enumerate(i):
                    if g == 0:
                        gene_dif = gene_dif + ((gene.value / 100) - (j[g].value / 100)) ** 2
                    elif g == 1:
                        turn_angle_a = (gene.value + 90) / 180
                        turn_angle_b = (j[g].value + 90) / 180
                        gene_dif = gene_dif + (turn_angle_a - turn_angle_b) ** 2
                    elif g == 2:
                        displ_a = gene.value / 180000
                        displ_b = j[g].value / 180000
                        gene_dif = gene_dif + (displ_a - displ_b) ** 2
                    elif g == 3:
                        conv_a = gene.value / 30
                        conv_b = j[g].value / 30
                        gene_dif = gene_dif + (conv_a - conv_b) ** 2
                    elif g == 4:
                        closer_a = (gene.value - 500) / 2500
                        closer_b = (j[g].value - 500) / 2500
                        gene_dif = gene_dif + (closer_a - closer_b) ** 2
            else:
                continue

            gene_dif = math.sqrt(gene_dif)

            Dj_sum = Dj_sum + gene_dif
    D = (Dj_sum/len(pop)) / len(pop)

    return D

def get_params(ind):

    if len(ind) > 5:
        parameter = [ind[x:x+18] for x in range(0, len(ind), 18)]
        for i, gene in enumerate(parameter):
            for j, val in enumerate(gene):
                gene[j] = val.value
    else:
        parameter = []
        for gene in ind:
            parameter.append(gene.value)

    del ind
    return parameter

def get_one_param(ind):

    if len(ind) > 5:
        parameter = [ind[x:x+18] for x in range(0, len(ind), 18)]
    else:
        parameter = ind

    return parameter

class Gene1:
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

class Gene:
    """
    The template for the genes in the chromosome.
    """
    def __init__(self, min, max, left):

        self.min = min
        self.max = max
        if left:
            self.value = random.uniform(min, 0)
        else:
            self.value = random.uniform(0, max)

    def __str__(self):
        return self.value

    def set_min_max(self, min, max):
        self.min = min
        self.max = max


def selRanked(individuals, k, size):
    """Select *k* individuals from the input *individuals* using *k*
    spins of a roulette. The selection is made by looking only at the first
    objective of each individual. The list returned contains references to
    the input *individuals*.

    :param individuals: A list of individuals to select from.
    :param k: The number of individuals to select.
    :returns: A list of selected individuals.

    This function uses the :func:`~random.random` function from the python base
    :mod:`random` module.

    .. warning::
       The roulette selection by definition cannot be used for minimization
       or when the fitness can be smaller or equal to 0.
    """
    s_inds = sorted(individuals, key=attrgetter("fitness"))
    s_inds_prob = list(map(toolbox.clone, s_inds))
    sum_ranks = sum(s_inds.index(ind) for ind in s_inds)
    p = 1.1

    fit_range = 0.0
    for index, ind in enumerate(s_inds_prob):
        fit = (((2-p)/size) + (((2*index)*(p-1))/(size*(size-1))))
        ind.fitness.values = fit,
        fit_range += ind.fitness.values[0]

    chosen = []
    chosen_string = 'selected: '
    for i in xrange(k):
        u = random.random()
        sum_ = 0
        for ind in s_inds_prob:
            sum_ += ind.fitness.values[0]
            if sum_ > u:
                chosen.append(s_inds[s_inds_prob.index(ind)])
                chosen_string += str(s_inds_prob.index(ind)) + ', '
                break
    print chosen_string
    del s_inds_prob

    return chosen

def selStochasticUniversalSampling(individuals, k, size):
    """Select the *k* individuals among the input *individuals*.
    The selection is made by using a single random value to sample all of the
    individuals by choosing them at evenly spaced intervals. The list returned
    contains references to the input *individuals*.

    :param individuals: A list of individuals to select from.
    :param k: The number of individuals to select.
    :return: A list of selected individuals.

    This function uses the :func:`~random.uniform` function from the python base
    :mod:`random` module.
    """
    s_inds = sorted(individuals, key=attrgetter("fitness"), reverse=True)
    sum_fits = sum(ind.fitness.values[0] for ind in individuals)

    distance = sum_fits / float(k)
    start = random.uniform(0, distance)
    points = [start + i*distance for i in xrange(k)]

    chosen = []
    chosen_string = 'selected: '
    for p in points:
        i = 0
        sum_ = s_inds[i].fitness.values[0]
        while sum_ < p:
            i += 1
            sum_ += s_inds[i].fitness.values[0]
        chosen.append(s_inds[i])
        chosen_string += str(i) + ', '

    print chosen_string

    return chosen