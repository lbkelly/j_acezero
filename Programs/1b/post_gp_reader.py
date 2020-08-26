from deap import tools, base, creator
from helpers import Gene as Gene
import helpers
import random
import cPickle
import csv
from pathos.multiprocessing import freeze_support
import sys

# Set up the toolbox from base
toolbox = base.Toolbox()

# set up the fitness component and the chromosome using that fitness
creator.create("fitness", base.Fitness, weights=(1.0,))
creator.create("Tactic", list, fitness=creator.fitness)

# The minimum and maximum values that the three measures can have
MIN_DISTANCE, MAX_DISTANCE = -48152, 48152
MIN_VELOCITY, MAX_VELOCITY = -1000, 1000
MIN_ACCEL, MAX_ACCEL = -100, 100




def main():
    # set evolutionary operators
    toolbox.register("mutate", helpers.gaussian, mu=0, sigma=0.2, indpb=0.002)
    toolbox.register("mate", tools.cxTwoPoint)
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

    round = int(raw_input("round?: "))
    if round == 2:
        # need the chromosome to repeat the data 12 times as there are 12 state transitions
        CYCLES = 12
    else:
        # need the chromosome to repeat the data 42 times as there are 12 state transitions
        CYCLES = 42

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
    #
    # # create the population initializer
    toolbox.register("population", tools.initRepeat, list, toolbox.tactic, 5)

    test_set = []


    teststring = raw_input("which test set?: ")
    freq = int(raw_input("Frequency: "))
    startat = int(raw_input("start from index what? 1, 11 or 21: "))

    with open(teststring, "r") as cp_file:
        cp = cPickle.load(cp_file)
    test_set = cp["population"]

    text_file = 'best/best_agents.txt'
    sys.stdout = open(text_file, 'w')

    iteration = startat

    endat = startat + 9


    while iteration <= endat:

        path = 'best/'

        # path = r"C:\Users\jarry\Desktop\r2_final\r2_final\SNV\2SNV1-3\cean\0_Seed_8176"
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