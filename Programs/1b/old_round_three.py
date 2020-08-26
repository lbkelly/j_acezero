import helpers
import random
import csv
import os
import sys
import visualization
import hall_off_fame as hof
from deap import tools, base, creator
from helpers import Gene as Gene
from datetime import datetime
import population_initializer as pop_init
import cPickle

"""
The second chromosome used. Allows all state transitions
"""

__author__ = 'jjwimbridge'


# class Gene:
#     """
#     The template for the genes in the chromosome.
#     """
#     def __init__(self, min, max, left):
#
#         if left:
#             self.value = random.uniform(min, 0)
#         else:
#             self.value = random.uniform(0, max)
#
#     def __str__(self):
#         return self.value
#
#     def set_min_max(self, min, max):
#         self.min = min
#         self.max = max

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
CYCLES = 42

"""____SET UP ANY LISTS FOR TRACKING DATA HERE___"""
plot_best_fitness = []
plot_average_fitness = []
plot_worst_fitness = []

blue_diversity = []
red_diversity = []
blue_est_best_gp = []
red_est_best_gp = []
blue_est_avg_gp = []
red_est_avg_gp = []

def main(seed, exp_no, run_specs, test_set):
    # set the randomized seed for experimentation duplication
    random.seed(seed)
    # set experiment number
    experiment = exp_no
    # assign the test set for GP
    test_set = test_set

    # sets the specs for the run
    POP = run_specs['pop_size']
    GENS = run_specs['gens']
    HOF_SIZE = run_specs['hof_size']
    CROSS_PROB = run_specs['cross_prob']
    MUT_PROB = 1.0
    IND_MUT_PROB = run_specs['mut_rate']
    SELECTOR = run_specs['selector']
    ELITISM = run_specs['elitism']
    alg = run_specs['algorithm']
    REC_FITS = run_specs['rec_fits']
    SEEDED = run_specs['seeded_pop']

    # sets hof and fs on/off
    FS = run_specs['FS']
    HOF = run_specs['HOF']

    """____SET UP ANY LISTS FOR TRACKING DATA HERE___"""
    plot_best_fitness = []
    plot_average_fitness = []
    plot_worst_fitness = []

    blue_est_best_gp = []
    red_est_best_gp = []
    blue_est_avg_gp = []
    red_est_avg_gp = []

    # set evolutionary operators
    toolbox.register("mutate", helpers.gaussian, mu=0, sigma=0.2, indpb=IND_MUT_PROB)
    toolbox.register("mate", tools.cxOnePoint)
    toolbox.register("evaluate", helpers.evaluate)
    if SELECTOR == 'SUS':
        toolbox.register("select", tools.selStochasticUniversalSampling)
    elif SELECTOR == 'RANKED':
        toolbox.register("select", helpers.selRanked)

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

    """<------------------------------------- START ---------------------------------------->"""

    if SEEDED == 1:
        blue_pop = pop_init.run()
        red_pop = pop_init.run()
        # Load the test set from the pickle file
        # with open("biased_blue_pop.pkl", "r") as cp_file:
        #     cp = cPickle.load(cp_file)
        # blue_pop = cp["population"]
        # with open("biased_red_pop.pkl", "r") as cp_file:
        #     cp = cPickle.load(cp_file)
        # red_pop = cp["population"]
    else:
        # initialize populations
        blue_pop = toolbox.population()
        red_pop = toolbox.population()

    # initialize hall of fame
    blue_hof = hof.HallOfFame(HOF_SIZE)
    red_hof = hof.HallOfFame(HOF_SIZE)

    # reset random seed to clock time
    algseed = datetime.now()
    random.seed(algseed)
    algseed = random.randint(0, 1001)
    random.seed(algseed)
    print 'Algorithm seed: ', algseed

    # get working folder for this set of runs
    folder_string = run_specs['folder']

    # Make new folder for experiemnt results
    save_path = os.getcwd()
    sub_folder_string = folder_string + str(exp_no) + '_Seed_' + str(seed) + '/'
    folder = os.path.join(save_path, sub_folder_string)
    if not os.path.isdir(folder):
        os.makedirs(folder)

    # create out file
    text_file = sub_folder_string + 'results.txt'
    sys.stdout = open(text_file, 'w')

    # create csv writer and file for fitness and initial/final population output
    csv_fits = sub_folder_string + 'relative_fitness.csv'
    fits = open(csv_fits, 'ab')
    fit_writer = csv.writer(fits)

    # create csv writer and file for detailed results for graph output
    # csv_pops = sub_folder_string + 'populations.csv'
    # pops = open(csv_pops, 'ab')
    # pops_writer = csv.writer(pops)

    # csv writer for outputting all fitnesses of blue population
    blue_pop_fits = sub_folder_string + 'blue_all_fits.csv'
    blue_fits_file = open(blue_pop_fits, 'ab')
    blue_fits_writer = csv.writer(blue_fits_file)

    # do the same for red ^^^
    red_pop_fits = sub_folder_string + 'red_all_fits.csv'
    red_fits_file = open(red_pop_fits, 'ab')
    red_fits_writer = csv.writer(red_fits_file)

    # create csv writer and file for GP data
    csv_fits = sub_folder_string + 'Gen_performance.csv'
    gp = open(csv_fits, 'ab')
    gp_writer = csv.writer(gp)
    # set up headings for graph csv
    fit_writer.writerow(('Generation', 'BestB', 'AvgB', 'WorstB', 'BestR', 'AvgR', 'WorstR'))
    # set up GP headings
    gp_writer.writerow(('Generation', 'BestB_GP', 'AvgB_GP', 'BestR_GP', 'AvgR_GP'))

    print 'Seed: ', seed

    i = 0
    while i <= GENS:
        i += 1
        print('--------------------------------' + 'Generation: ' + str(i) + '-----------------------------------')

        """ ----------------------------------- EVALUATE THE POPULATIONS --------------------------------------- """

        # Reset fitness scores to zero so they can be accumulated each generation
        for index, x in enumerate(blue_pop):
            x.fitness.values = (0.0,)

        for index, y in enumerate(red_pop):
            y.fitness.values = (0.0,)

        """<----------RELATIVE FITNESS EVALUATIONS--------->"""
        # Evaluate the populations and return with summed fitness scores of all engagements
        # THIS FITNESS SCORE NEEDS TO BE AVERAGED AFTER HOF EVALS
        blue_pop, red_pop = helpers.sum_pop_v_pop_evals(blue_pop, red_pop)

        """<----------HALL OF FAME EVALUATIONS--------->"""
        # check hof not empty, if not, loop through and evaluate
        # Only if HOF is turned on
        if HOF == 1:
            if len(red_hof) != 0:
                blue_pop = helpers.sum_pop_v_hof_evals(blue_pop, red_hof)

            if len(blue_hof) != 0:
                red_pop = helpers.sum_pop_v_hof_evals(red_pop, blue_hof)

        """<-------AVERAGE THE FITNESS SCORES------>"""
        # average the accumulated fitness scores by size of population and also output fitnesses to csv
        blue_fits_row = []
        blue_fits_row.append(i)
        for index, x in enumerate(blue_pop):
            if HOF == 1:
                x.fitness.values = (x.fitness.values[0] / (POP + len(red_hof)),)
            else:
                x.fitness.values = (x.fitness.values[0] / POP,)
            blue_fits_row.append(x.fitness.values[0])

        red_fits_row = []
        red_fits_row.append(i)
        for index, y in enumerate(red_pop):
            if HOF == 1:
                y.fitness.values = (y.fitness.values[0] / (POP + len(blue_hof)),)
            else:
                y.fitness.values = (y.fitness.values[0] / POP,)
            red_fits_row.append(y.fitness.values[0])

        if REC_FITS == 1:
            blue_fits_writer.writerow(blue_fits_row)
            red_fits_writer.writerow(red_fits_row)

        """------------Generalisation Performance---------------------"""
        # EVERY 5TH GEN RECORD STATS
        # if i % 5 == 0 or i == 1:
        #     # CLONE THE POPS SO GP CAN BE CALCULATED WITHOUT AFFECTING FITNESS SCORES
        #     blue_copy = list(map(toolbox.clone, blue_pop))
        #     red_copy = list(map(toolbox.clone, red_pop))
        #     blue_copy = tools.selBest(blue_copy, 5)
        #     red_copy = tools.selBest(red_copy, 5)
        #     # Get generalisation performance of two populations
        #     blue_copy = helpers.sum_pop_v_hof_evals(blue_copy, test_set)
        #     for index_x, x in enumerate(blue_copy):
        #         x.fitness.values = (x.fitness.values[0] / len(test_set),)
        #
        #     red_copy = helpers.sum_pop_v_hof_evals(red_copy, test_set)
        #     for index_x, x in enumerate(red_copy):
        #         x.fitness.values = (x.fitness.values[0] / len(test_set),)
        #
        #     # create variables for estimated best and average GPs
        #     nBest_blue = tools.selBest(blue_copy, 5)
        #     blue_ebgp = tools.selBest(nBest_blue, 1)
        #     blue_est_best_gp.append(blue_ebgp[0].fitness.values[0])
        #     blue_eagp_tally = []
        #     for index, x in enumerate(nBest_blue):
        #         blue_eagp_tally.append(x.fitness.values[0])
        #     blue_avg = sum(blue_eagp_tally) / len(nBest_blue)
        #     blue_est_avg_gp.append(blue_avg)
        #
        #     nBest_red = tools.selBest(red_copy, 5)
        #     red_ebgp = tools.selBest(nBest_red, 1)
        #     red_est_best_gp.append(red_ebgp[0].fitness.values[0])
        #     red_eagp_tally = []
        #     for index, x in enumerate(nBest_red):
        #         red_eagp_tally.append(x.fitness.values[0])
        #     red_avg = sum(red_eagp_tally) / len(nBest_red)
        #     red_est_avg_gp.append(red_avg)

        """<----------OUTPUT INFO TO TEXT FILE---------->"""
        # BLUE
        best_blue_ind = tools.selBest(blue_pop, 1)[0]
        print 'Best Blue fitness score: ', best_blue_ind.fitness.values[0]
        print 'Best blue chromosome: ', helpers.list_to_string(best_blue_ind)

        worst_blue_ind = tools.selWorst(blue_pop, 1)[0]
        print "Worst Blue fitness: ", worst_blue_ind.fitness.values[0]

        # get the average fitness of the generation
        sum_fits = sum(ind.fitness.values[0] for ind in blue_pop)
        avg_blue_fitness = sum_fits / POP
        print "Generation average Blue fitness: ", avg_blue_fitness

        # if i % 5 == 0 or i == 1:
        #     print 'Performance Measures:'
        #     # output the GP and diversity of the generation
        #     print 'Blue Estimated Average GP: ', blue_avg
        #     print 'Blue Estimated Best GP: ', blue_ebgp[0].fitness.values[0]
        #
        #     #Print the 5 best GP inds
        #     print 'Top Blue GP performers'
        #     for index, x in enumerate(nBest_blue):
        #         print index+1, ':'
        #         print helpers.list_to_string(x), 'GP: ', x.fitness.values[0]

        # RED
        # get best chromosome and output
        best_red_ind = tools.selBest(red_pop, 1)[0]
        print "Best Red fitness: ", best_red_ind.fitness.values[0]
        print 'Best Red chromosome: ', helpers.list_to_string(best_red_ind)

        # get worst and display
        worst_red_ind = tools.selWorst(red_pop, 1)[0]
        print "Worst Red fitness: ", worst_red_ind.fitness.values[0]

        # get the average fitness of the generation
        sum_fits = sum(ind.fitness.values[0] for ind in red_pop)
        avg_red_fitness = sum_fits / POP
        print "Generation average red fitness: ", avg_red_fitness

        # if i % 5 == 0 or i == 1:
        #     print 'Performance Measures:'
        #     # output the GP and diversity of the generation
        #     print 'Red Estimated Average GP: ', red_avg
        #     print 'Red Estimated Best GP: ', red_ebgp[0].fitness.values[0]
        #
        #     # Print the 5 best GP inds
        #     print 'Top red GP performers'
        #     for index, x in enumerate(nBest_red):
        #         print index + 1, ':'
        #         print helpers.list_to_string(x), 'GP: ', x.fitness.values[0]

        # Write best avg & worst to fits_csv
        fit_writer.writerow(
            (i, best_blue_ind.fitness.values[0], avg_blue_fitness, worst_blue_ind.fitness.values[0],
             best_red_ind.fitness.values[0], avg_red_fitness, worst_red_ind.fitness.values[0]))

        # if i % 5 == 0 or i == 1:
        #     # save the GP values to the GP file
        #     gp_writer.writerow((i, blue_ebgp[0].fitness.values[0], blue_avg, red_ebgp[0].fitness.values[0], red_avg))

        # if i % 5 == 0 or i == 1:
        #     # Fill the dictionary using the dict(key=value[, ...]) constructor
        #     cp = dict(population=blue_pop, generation=i, rndstate=random.getstate())
        #
        #     with open(sub_folder_string + "zgeneration" + str(i) + ".pkl", "wb") as cp_file:
        #         cPickle.dump(cp, cp_file)

        if i == GENS:
            break

        """<------------HALL OF FAME UPDATE----------->"""
        blue_hof.update(tools.selBest(blue_pop, 1), i)
        red_hof.update(tools.selBest(red_pop, 1), i)



        """<------------FITNESS SHARING------------>"""
        """ NEEDS TO BE FIXED IN HELPERS TO USE NEW CHROMOSOME """
        #MUST BE LAST THING BEFORE EVOLUTION HAPPENS
        # if FS == 1:
        #     blue_pop = helpers.share_fitness(blue_pop, 0.2)
        #     red_pop = helpers.share_fitness(red_pop, 0.2)

        """<--------------------BEGIN EVOLUTION------------------>"""
        # Select offspring for next generation
        if ELITISM == 1:
            blue_offspring = toolbox.select(blue_pop, POP-1)
            red_offspring = toolbox.select(red_pop, POP-1)
        else:
            blue_offspring = toolbox.select(blue_pop, POP)
            red_offspring = toolbox.select(red_pop, POP)

        # Clone the offspring so we can evolve
        blue_offspring = list(map(toolbox.clone, blue_offspring))
        red_offspring = list(map(toolbox.clone, red_offspring))

        # CROSSOVER
        # Blue
        for child1, child2 in zip(blue_offspring[::2], blue_offspring[1::2]):
            if random.random() < CROSS_PROB:
                # MATE
                toolbox.mate(child1, child2)
            # Red
        for child1, child2 in zip(red_offspring[::2], red_offspring[1::2]):
            if random.random() < CROSS_PROB:
                # MATE
                toolbox.mate(child1, child2)

        # MUTATION
        for mutant in blue_offspring:
            if random.random() < MUT_PROB:
                # MUTATE
                for index, x in enumerate(mutant):
                    mutant[index].value = helpers.convert_range(mutant[index].value, mutant[index].min,
                                                                mutant[index].max)

                toolbox.mutate(mutant)

                for index, x in enumerate(mutant):
                    mutant[index].value = helpers.change_back(mutant[index].value, mutant[index].min,
                                                              mutant[index].max)
                    helpers.bounds_check(mutant[index])

        for mutant in red_offspring:
            if random.random() < MUT_PROB:
                # MUTATE
                for index, x in enumerate(mutant):
                    mutant[index].value = helpers.convert_range(mutant[index].value, mutant[index].min,
                                                                mutant[index].max)

                toolbox.mutate(mutant)

                for index, x in enumerate(mutant):
                    mutant[index].value = helpers.change_back(mutant[index].value, mutant[index].min,
                                                              mutant[index].max)
                    helpers.bounds_check(mutant[index])

        if ELITISM == 1:
            blue_offspring += tools.selBest(blue_pop, 1)
            red_offspring += tools.selBest(red_pop, 1)

        # REPLACE
        blue_pop[:] = blue_offspring
        red_pop[:] = red_offspring

        print ('-------------------------------------Hall Of Fame Regular----------------------------------------')
        print "BLUE: "
        # for chromosomes in blue_hof:
        #     print 'Chromosome: ', helpers.list_to_string(chromosomes), 'Fitness: ', chromosomes.fitness.values
        if len(blue_hof) != 0:
            blue_hof.print_hof()

        print "RED: "
        # for chromosomes in red_hof:
        #     print 'Chromosome: ', helpers.list_to_string(chromosomes), 'Fitness: ', chromosomes.fitness.values
        if len(red_hof) != 0:
            red_hof.print_hof()

        print "Generation ", i, " complete."

    print ('-------------------------------------Hall Of Fame Regular----------------------------------------')
    print "BLUE: "
    # for chromosomes in blue_hof:
    #     print 'Chromosome: ', helpers.list_to_string(chromosomes), 'Fitness: ', chromosomes.fitness.values
    if len(blue_hof) != 0:
        blue_hof.print_hof()

    print "RED: "
    # for chromosomes in red_hof:
    #     print 'Chromosome: ', helpers.list_to_string(chromosomes), 'Fitness: ', chromosomes.fitness.values
    if len(red_hof) != 0:
        red_hof.print_hof()

    print ('-------------------------------------Stats----------------------------------------')
    print 'Seed: ', seed
    print 'Selection: ', SELECTOR
    print("Pop size: " + str(POP))
    print("Generations: " + str(GENS))
    print("Crossover Prob: " + str(CROSS_PROB))
    print("Mutation Prob: " + str(IND_MUT_PROB))
    print 'Elitism: ', ELITISM
    print 'Hall of Fame: ', HOF
    print 'Fitness Sharing: ', FS
    print 'Algorithm: ', alg

    # Print the 5 best GP inds
    # print 'Top 5 Blue GP performers:'
    # for index, x in enumerate(nBest_blue):
    #     print index + 1, ':'
    #     print helpers.list_to_string(x), 'GP: ', x.fitness.values[0]

    # Print the 5 best GP inds
    # print 'Top red GP performers:'
    # for index, x in enumerate(nBest_red):
    #     print index + 1,":"
    #     print helpers.list_to_string(x), 'GP: ', x.fitness.values[0]


    # pops_writer.writerow(('Final Blue population fitness scores',))
    # for index, x in enumerate(blue_pop):
    #     pops_writer.writerow(x.fitness.values)
    # pops_writer.writerow(('Final Red population fitness scores',))
    # for index, y in enumerate(red_pop):
    #     pops_writer.writerow(y.fitness.values)



    # blue_est_avg_gp = sum(blue_est_avg_gp) / len(blue_est_avg_gp)
    # red_est_avg_gp = sum(red_est_avg_gp) / len(red_est_avg_gp)
    #
    # blue_est_best_gp = sum(blue_est_best_gp) / len(blue_est_best_gp)
    # red_est_best_gp = sum(red_est_best_gp) / len(red_est_best_gp)

    fits.close()
    # pops.close()
    blue_fits_file.close()
    red_fits_file.close()

    # stats = {"blue_est_avg_gp": blue_est_avg_gp, "blue_est_best_gp": blue_est_best_gp,
    #          "red_est_avg_gp": red_est_avg_gp, "red_est_best_gp": red_est_best_gp}


    return #stats

def run(seed, i, run_specs, test_set):
    main(seed, i, run_specs, test_set)
    return

# if __name__ == "__main__":
#     main(12)