from deap import tools, base, creator
from helpers import Gene1 as Gene
import helpers
import random
import cPickle
import csv
from pathos.multiprocessing import freeze_support
import sys

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

def main():
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
    toolbox.register("population", tools.initRepeat, list, toolbox.tactic, 5)

    # set evolutionary operators
    toolbox.register("mate", tools.cxOnePoint)
    toolbox.register("mutate", helpers.gaussian, mu=0, sigma=0.2, indpb=IND_MUT_PROB)
    toolbox.register("select", tools.selStochasticUniversalSampling)
    toolbox.register("evaluate", helpers.evaluate)

    test_set = []

    teststring = raw_input("which test set?: ")
    freq = int(raw_input("Frequency: "))

    text_file = 'best/best_agents.txt'
    sys.stdout = open(text_file, 'w')
    # startat = int(raw_input("start from index what? 1, 11 or 21: "))

    with open(teststring, "r") as cp_file:
        cp = cPickle.load(cp_file)
    test_set = cp["population"]

    iteration = 1
    endat = 30

    while iteration <= endat:
        path = 'best/'
        # r"C:\Users\jarry\Desktop\r2_final\r2_final\SNV\2SNV1-3\cean\0_Seed_8176"
        # path = r"C:\Users\jarry\Desktop\r1_final\r1_final\SNV\SNV6-10\cean\2_Seed_2807"

        best = toolbox.population()
        gen = 0

        # path = raw_input("File path: ")
        # Open the file with read only permit
        f = open(path + str(iteration) + 'blue_best.txt')
        # use readline() to read the first line
        line = f.readline()

        gp = path + '/' + str(iteration) + 'new_gp.csv'
        gp_file = open(gp, 'ab')
        gp_writer = csv.writer(gp_file)
        gp_writer.writerow(['best', 'avg'])


        while line:
            if line[0] == "<":
                gen += 1
                agents = []
                line = f.readline()
                if gen % freq == 0 or gen == 1:
                    line = line.split(')', 1)[1]
                    line = line.replace(' ', '')
                    line = line[:-3]
                    ind1 = line.split(',')
                    ind1 = [float(i) for i in ind1]
                    agents.append(ind1)
                    line = f.readline()
                if gen % freq == 0 or gen == 1:
                    line = line.split(')', 1)[1]
                    line = line.replace(' ', '')
                    line = line[:-3]
                    ind2 = line.split(',')
                    ind2 = [float(i) for i in ind2]
                    agents.append(ind2)
                    line = f.readline()
                if gen % freq == 0 or gen == 1:
                    line = line.split(')', 1)[1]
                    line = line.replace(' ', '')
                    line = line[:-3]
                    ind3 = line.split(',')
                    ind3 = [float(i) for i in ind3]
                    agents.append(ind3)
                    line = f.readline()
                if gen % freq == 0 or gen == 1:
                    line = line.split(')', 1)[1]
                    line = line.replace(' ', '')
                    line = line[:-3]
                    ind4 = line.split(',')
                    ind4 = [float(i) for i in ind4]
                    agents.append(ind4)
                    line = f.readline()
                if gen % freq == 0 or gen == 1:
                    line = line.split(')', 1)[1]
                    line = line.replace(' ', '')
                    line = line[:-3]
                    ind5 = line.split(',')
                    ind5 = [float(i) for i in ind5]
                    agents.append(ind5)

                    for ind_indx, ind in enumerate(best):
                        for gene_index, gene in enumerate(ind):
                            gene.value = agents[ind_indx][gene_index]

                    for index, x in enumerate(best):
                        x.fitness.values = (0.0,)

                    helpers.sum_pop_v_hof_evals(best, test_set)

                    sum_gp = 0.0

                    for index_x, x in enumerate(best):
                        x.fitness.values = (x.fitness.values[0] / len(test_set),)
                        sum_gp += x.fitness.values[0]

                    agp = sum_gp / len(best)

                    bgp = tools.selBest(best, 1)[0]


                    gp_writer.writerow([bgp.fitness.values[0], agp])



            # use realine() to read next line
            line = f.readline()
            if '' == line:
                beststring = ''
                for gene_index, gene in enumerate(bgp):
                    beststring = beststring + str(gene.value) + ', '

                print 'best GP for index ' + str(iteration) + ': (' + str(bgp.fitness.values[0]) + ') ' + beststring

        f.close()
        gp_file.close()
        iteration += 1

if __name__ == "__main__":
    freeze_support()
    main()