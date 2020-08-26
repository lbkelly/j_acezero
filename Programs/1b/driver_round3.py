import round_three
import cProfile
import cPickle
import random
# from helpers import Gene as Gene
import os
import csv
import datetime
import seed
from pathos.multiprocessing import freeze_support


"""
Driver script to run the test DEAP projects.
This is used to automate running many seeds of the GA in a row.
"""


def main():
    """ Are the simulation scripts pointing to right agents??? Even the straight and default?
        ------------------------------------------------------------------------------------------"""

    date_time = datetime.datetime.now().strftime("%m-%d_%I%M%p")
    number_of_experiments = 1
    mut_rate = 0.002
    cross_prob = 0.6
    pop_size = 40
    hof_size = 10
    gens = 600
    selection = 'SUS'
    elitism = 1
    algorithm = 'cean'
    rec_fits = 1
    seeded_pop = 0

    # TURN FS & HOF ON/OFF
    FS = 0
    HOF = 0

    changes = int(raw_input("Change the parameters? (1 or 0): "))
    if changes == 1:
        number_of_experiments = int(raw_input("No of Exp's: "))
        mchange = int(raw_input("Change probabilties?: (1 or 0): "))
        if mchange == 1:
            mut_rate = float(raw_input("Mut rate: "))
            cross_prob = float(raw_input("Cross rate: "))
        pop_size = int(raw_input("Pop size: "))
        hof_size = int(raw_input("HOF size: "))
        gens = int(raw_input("Gens: "))
        selection = raw_input("SUS or RANKED?: ")
        elitism = int(raw_input("Elitism?: "))
        algorithm = 'cean'
        rec_fits = 1
        seeded_pop = int(raw_input("Seeded pop? (1 or 0): "))

        # TURN FS & HOF ON/OFF
        FS = 0
        HOF = int(raw_input("HOF Evals? (1 or 0): "))

    init_seed = seed.seed
    init_seed = 456
    random.seed(init_seed)

    run_specs = {"mut_rate": mut_rate, "cross_prob": cross_prob, "pop_size": pop_size,
                 "hof_size": hof_size, "gens": gens, "FS": FS, "HOF": HOF, "selector": selection, "elitism": elitism, "algorithm": algorithm, "rec_fits": rec_fits, "seeded_pop": seeded_pop}

    # seed = 731 #random.randint(1, 1001)

    # Load the test set from the pickle file
    with open("r3_test_set.pkl", "r") as cp_file:
        cp = cPickle.load(cp_file)
    test_set = cp["population"]

    # Make new folder for experiemnt results
    save_path = os.getcwd()
    folder_string = date_time + '/' + algorithm + '/'
    folder = os.path.join(save_path, folder_string)
    if not os.path.isdir(folder):
        os.makedirs(folder)

    lowdown = open(folder_string + 'lowdown.txt', 'w')
    lowdown.write('Round 2: ')

    run_specs['folder'] = folder_string

    # csv_stats = folder_string + 'performance_measures' + '.csv'
    # statistics = open(csv_stats, 'ab')
    # stat_writer = csv.writer(statistics)

    # stat_writer.writerow(('seed', 'blue rel', 'blue EBGP', 'blue EAGP', 'red rel', 'red EBGP', 'red EAGP'))

    seeds = []
    for u in xrange(31):
        seeds.append(random.randint(0, 10000))

    seed_index = raw_input("Input the experiment seed index (1-30): ")
    seed_index = int(seed_index) - 1

    # seed_index = int(raw_input("Input the experiment seed : "))


    for i in xrange(number_of_experiments):
       # round_three.run(seeds[seed_index], i, run_specs, test_set)
        round_three.run(456, i, run_specs, test_set)

        # stat_writer.writerow(stats)
        seed_index += 1



    # statistics.close()

if __name__ == "__main__":
    freeze_support()
    main()
    # cProfile.run("main()")
