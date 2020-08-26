import helpers
import random
import csv
import os
import sys
import visualization
import hall_off_fame as hof
from deap import tools, base, creator
from helpers import Gene1 as Gene
from datetime import datetime
# import population_initializer as pop_init
import cPickle


__author__ = 'jwimbridge'

toolbox = base.Toolbox()

# set up the fitness component and the chromosome using that fitness
creator.create("fitness", base.Fitness, weights=(1.0,))
creator.create("Tactic", list, fitness=creator.fitness)

# The minimum and maximum values that the three measures can have
min_turn_range, max_turn_range = 0.1, 100
min_turn_angle, max_turn_angle = -90, 90
min_displ, max_displ = 0, 180000
min_conv_range, max_conv_range = 0, 30
min_closer_range, max_closer_range = 500, 3000

# need the chromosome to repeat the data 12 times as there are 12 state transitions
CYCLES = 1

"""____SET UP ANY LISTS FOR TRACKING DATA HERE___"""


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
    stats_rel_b = []
    stats_bgp_b = []
    stats_agp_b = []
    stats_rel_r = []
    stats_bgp_r = []
    stats_agp_r = []

    # set evolutionary operators
    toolbox.register("mutate", helpers.gaussian, mu=0, sigma=1.0, indpb=IND_MUT_PROB)
    toolbox.register("mate", tools.cxOnePoint)
    toolbox.register("evaluate", helpers.evaluate)
    if SELECTOR == 'SUS':
        toolbox.register("select", helpers.selStochasticUniversalSampling)
    elif SELECTOR == 'RANKED':
        toolbox.register("select", helpers.selRanked)

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

    # create the population initializer
    toolbox.register("population", tools.initRepeat, list, toolbox.tactic, POP)

    """<------------------------------------- START ---------------------------------------->"""

    if SEEDED == 1:
        print " no seeded pop"
    else:
        # initialize populations
        blue_pop = toolbox.population()
        red_pop = toolbox.population()

    # initialize hall of fame
    blue_hof = hof.HallOfFame(HOF_SIZE)
    red_hof = hof.HallOfFame(HOF_SIZE)

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

    # reset random seed to clock time
    algseed = datetime.now()
    random.seed(algseed)
    algseed = random.randint(0, 10001)
    random.seed(algseed)
    print 'Algorithm seed: ', algseed

    # create csv writer and file for fitness and initial/final population output
    csv_fits = sub_folder_string + 'relative_fitness.csv'
    fits = open(csv_fits, 'ab')
    fit_writer = csv.writer(fits)

    # csv writer for outputting all fitnesses of blue population
    blue_pop_fits = sub_folder_string + 'blue_all_fits.csv'
    blue_fits_file = open(blue_pop_fits, 'ab')
    blue_fits_writer = csv.writer(blue_fits_file)

    # do the same for red ^^^
    red_pop_fits = sub_folder_string + 'red_all_fits.csv'
    red_fits_file = open(red_pop_fits, 'ab')
    red_fits_writer = csv.writer(red_fits_file)

    blue_gp = sub_folder_string + 'blue_gp.csv'
    blue_gp_file = open(blue_gp, 'ab')
    blue_gp_writer = csv.writer(blue_gp_file)
    blue_gp_writer.writerow(['best', 'avg'])

    blue_chromosomes = sub_folder_string + 'blue_best.txt'
    blue_best_file = open(blue_chromosomes, 'w')

    red_gp = sub_folder_string + 'red_gp.csv'
    red_gp_file = open(red_gp, 'ab')
    red_gp_writer = csv.writer(red_gp_file)
    red_gp_writer.writerow(['best', 'avg'])

    red_chromosomes = sub_folder_string + 'red_best.txt'
    red_best_file = open(red_chromosomes, 'w')

    print "<-----INITIAL BLUE----->"
    for b, ind in enumerate(blue_pop):
        print "Chromosome ", str(b), ': '
        print helpers.list_to_string(ind)

    print "<-----INITIAL RED----->"
    for r, ind in enumerate(red_pop):
        print "Chromosome ", str(r), ': '
        print helpers.list_to_string(ind)


    # create csv writer and file for GP data
    # csv_fits = sub_folder_string + 'Gen_performance.csv'
    # gp = open(csv_fits, 'ab')
    # gp_writer = csv.writer(gp)
    # set up headings for graph csv
    fit_writer.writerow(('Generation', 'BestB', 'AvgB', 'WorstB', 'BestR', 'AvgR', 'WorstR'))
    # set up GP headings
    # gp_writer.writerow(('Generation', 'BestB_GP', 'AvgB_GP', 'BestR_GP', 'AvgR_GP'))

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

        """------------GET BEST---------------------"""

        blue_best_file.write("<------------ GEN " + str(i) + "--------------->\n")
        red_best_file.write("<------------ GEN " + str(i) + "--------------->\n")
        best_blue = tools.selBest(blue_pop, 5)
        best_red = tools.selBest(red_pop, 5)

        for index, b in enumerate(best_blue):
            blue_best_file.write("Chromsome [" + str(index) + "]: " + "(" + str(b.fitness.values[0]) + ")" + helpers.list_to_string(b) + "\n")

        for index, r in enumerate(best_red):
            red_best_file.write("Chromsome [" + str(index) + "]: " + "(" + str(r.fitness.values[0]) + ")" + helpers.list_to_string(r) + "\n")

        """ <---------------- Gen Perf ---------------->"""
        # cloned so the GP can be calculated without wiping relative scores
        blue_copy = list(map(toolbox.clone, best_blue))
        red_copy = list(map(toolbox.clone, best_red))

        # Reset fitness scores to zero so they can be accumulated each generation
        for index, x in enumerate(blue_copy):
            x.fitness.values = (0.0,)

        for index, y in enumerate(red_copy):
            y.fitness.values = (0.0,)

        blue_copy = helpers.sum_pop_v_hof_evals(blue_copy, test_set)
        red_copy = helpers.sum_pop_v_hof_evals(red_copy, test_set)
        sum_gp_b = 0.0
        sum_gp_r = 0.0
        for index_x, x in enumerate(blue_copy):
            x.fitness.values = (x.fitness.values[0] / len(test_set),)
            sum_gp_b += x.fitness.values[0]
        for index_y, y in enumerate(red_copy):
            y.fitness.values = (y.fitness.values[0] / len(test_set),)
            sum_gp_r += y.fitness.values[0]

        avg_gp_b = sum_gp_b / len(blue_copy)
        avg_gp_r = sum_gp_r / len(red_copy)
        best_gp_b = tools.selBest(blue_copy, 1)[0].fitness.values[0]
        best_gp_r = tools.selBest(red_copy, 1)[0].fitness.values[0]
        blue_gp_writer.writerow([best_gp_b, avg_gp_b])
        red_gp_writer.writerow([best_gp_r, avg_gp_r])

        del blue_copy
        del red_copy

        """<----------OUTPUT INFO TO TEXT FILE---------->"""
        # BLUE
        best_blue_ind = tools.selBest(blue_pop, 1)[0]
        print 'Best Blue fitness score: ', best_blue_ind.fitness.values[0]
        print 'Best blue chromosome: ', helpers.list_to_string(best_blue_ind)

        worst_blue_ind = tools.selWorst(blue_pop, 1)[0]
        print "Worst Blue fitness: ", worst_blue_ind.fitness.values[0]
        print "Worst Blue chromosome: ", helpers.list_to_string(worst_blue_ind)

        # get the average fitness of the generation
        sum_fits = sum(ind.fitness.values[0] for ind in blue_pop)
        avg_blue_fitness = sum_fits / POP
        print "Generation average Blue fitness: ", avg_blue_fitness

        # RED
        # get best chromosome and output
        best_red_ind = tools.selBest(red_pop, 1)[0]
        print "Best Red fitness: ", best_red_ind.fitness.values[0]
        print 'Best Red chromosome: ', helpers.list_to_string(best_red_ind)

        # get worst and display
        worst_red_ind = tools.selWorst(red_pop, 1)[0]
        print "Worst Red fitness: ", worst_red_ind.fitness.values[0]
        print "Worst Red chromosome: ", helpers.list_to_string(worst_red_ind)

        # get the average fitness of the generation
        sum_fits = sum(ind.fitness.values[0] for ind in red_pop)
        avg_red_fitness = sum_fits / POP
        print "Generation average red fitness: ", avg_red_fitness

        # Write best avg & worst to fits_csv
        fit_writer.writerow(
            (i, best_blue_ind.fitness.values[0], avg_blue_fitness, worst_blue_ind.fitness.values[0],
             best_red_ind.fitness.values[0], avg_red_fitness, worst_red_ind.fitness.values[0]))

        # if i % 5 == 0 or i == 1:
        #     # Fill the dictionary using the dict(key=value[, ...]) constructor
        #     cp = dict(population=blue_pop, generation=i, rndstate=random.getstate())
        #
        #     with open(sub_folder_string + "zgeneration" + str(i) + ".pkl", "wb") as cp_file:
        #         cPickle.dump(cp, cp_file)

        stats_rel_b.append(best_blue_ind.fitness.values[0])
        stats_bgp_b.append(best_gp_b)
        stats_agp_b.append(avg_gp_b)
        stats_rel_r.append(best_red_ind.fitness.values[0])
        stats_bgp_r.append(best_gp_r)
        stats_agp_r.append(avg_gp_r)

        if i > 10:
            stats_rel_b.pop(0)
            stats_bgp_b.pop(0)
            stats_agp_b.pop(0)
            stats_rel_r.pop(0)
            stats_bgp_r.pop(0)
            stats_agp_r.pop(0)

        # if i > GENS-10:
        #     stats_rel_b.append(best_blue_ind.fitness.values[0])
        #     stats_bgp_b.append(best_gp_b)
        #     stats_agp_b.append(avg_gp_b)
        #     stats_rel_r.append(best_red_ind.fitness.values[0])
        #     stats_bgp_r.append(best_gp_r)
        #     stats_agp_r.append(avg_gp_r)

        if i == GENS:
            break

        """<------------HALL OF FAME UPDATE----------->"""
        blue_hof.update(tools.selBest(blue_pop, 1), i)
        red_hof.update(tools.selBest(red_pop, 1), i)

        """<--------------------BEGIN EVOLUTION------------------>"""
        # Select offspring for next generation
        if ELITISM == 1:
            blue_offspring = toolbox.select(blue_pop, POP-1, POP)
            red_offspring = toolbox.select(red_pop, POP-1, POP)
        else:
            blue_offspring = toolbox.select(blue_pop, POP, POP)
            red_offspring = toolbox.select(red_pop, POP, POP)

        # Clone the offspring so we can evolve
        blue_offspring = list(map(toolbox.clone, blue_offspring))
        red_offspring = list(map(toolbox.clone, red_offspring))
        random.shuffle(blue_offspring)
        random.shuffle(red_offspring)

        # CROSSOVER
        blue_cross_count = 0
        # Blue
        for child1, child2 in zip(blue_offspring[::2], blue_offspring[1::2]):
            if random.random() < CROSS_PROB:
                # MATE
                toolbox.mate(child1, child2)
                blue_cross_count += 1
        # Red
        red_cross_count = 0
        for child1, child2 in zip(red_offspring[::2], red_offspring[1::2]):
            if random.random() < CROSS_PROB:
                # MATE
                toolbox.mate(child1, child2)
                red_cross_count += 1
        print "blue crossover count: ", str(blue_cross_count)
        print "red crossover count: ", str(red_cross_count)

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
            elite_blue = toolbox.clone(tools.selBest(blue_pop, 1))
            elite_red = toolbox.clone(tools.selBest(red_pop, 1))
            blue_offspring += elite_blue
            red_offspring += elite_red
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

    fits.close()
    blue_fits_file.close()
    red_fits_file.close()
    red_best_file.close()
    blue_best_file.close()
    blue_gp_file.close()
    red_gp_file.close()

    stats = [seed, sum(stats_rel_b)/10, sum(stats_bgp_b)/10, sum(stats_agp_b)/10, sum(stats_rel_r)/10, sum(stats_bgp_r)/10, sum(stats_agp_r)/10]

    # stats = {"blue_est_avg_gp": blue_est_avg_gp, "blue_est_best_gp": blue_est_best_gp,
    #          "red_est_avg_gp": red_est_avg_gp, "red_est_best_gp": red_est_best_gp}


    return stats

def run(seed, i, run_specs, test_set):
    stats = main(seed, i, run_specs, test_set)
    return stats

# if __name__ == "__main__":
#     main(12)