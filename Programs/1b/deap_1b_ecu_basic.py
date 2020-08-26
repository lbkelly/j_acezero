import write_chromosome as wc
import helpers as helper
import random
import csv
import sys
import visualization
import hall_off_fame as hof
from deap import tools, base, creator

"""
The Genetic Algorithm used for the ECU basic(Park) agent for part of 1b.

This GA script generates the gene, chromosome and runs the evolution using the DEAP library.
This program make's a call to a evaluate method in the helper class which calls Ace0 to return the fitness score.

"""

__author__ = 'lbkelly'

# needed to write out the chromosome values to file
chromosome_parameters = wc.WriteChromosome()


class Gene:
    """
    The gene class represents the individuals inside the chromosome.
    Each gene will have a value and also a min and max value.
    The min and max value represent the range in which the gene can have legal values.
    The gene's are initialized with the values between min and 0 OR 0 and max.
    """
    def __init__(self, min, max, left):
        """
        Represents the gene

        :param min: minimum values the gene can have
        :param max: maximum value the gene can have
        :param left: if true, it is an initial value between the min and 0, if false, it is between 0 and max
        """
        if left:
            self.value = random.uniform(min, 0)
        else:
            self.value = random.uniform(0, max)
        self.min = min
        self.max = max

    def __str__(self):
        return self.value

    def set_min_max(self, min, max):
        self.min = min
        self.max = max


class ParkEcuGA:
    def __init__(self):
        # access to the DEAP toolset
        self.toolbox = base.Toolbox()

        # Lists for the plots
        self.plot_best_fitness = []
        self.plot_average_fitness = []

        # create our initial population as a list "population"
        self.population = ''

        # how many repetitions to run the simulation for to get a fitness score
        self.repetitions = 5

        # these values are used for the gene initialization and mutation range clipping
        # min and max difference in distance between the two fighters
        self.MIN_DISTANCE, self.MAX_DISTANCE = -48152, 48152
        # min and max difference in the velocity between the two fighters
        self.MIN_VELOCITY, self.MAX_VELOCITY = -1000, 1000
        # min and max difference in acceleration between the two fighters
        self.MIN_ACCELERATION, self.MAX_ACCELERATION = -100, 100

        # how many cycles the chromosome will repeat the data, we want only 42 cycle to happen because there is
        # 42 transitions
        self.CYCLES = 42

        # how many chromosomes in each population
        self.POP = 100

        # how many generations to run the algorithm
        self.GENERATIONS = 500

        # crossover and mutation probabilities
        self.CROSSOVER_PROBABILITY = 0.6
        self.MUTATION_PROBABILITY = 1.0

        # how many individuals to keep in the hall fame
        self.HOF_SIZE = 10

        # parameters used to track algorithm stagnation/ termination
        self.temp_best_fitness = 0
        self.converge_tracker_2 = 0
        self.converge_stagnant_fitness = 500

        self.converge_tracker = 0
        self.converge_tracker_max = 10

        self.isConverged = False

        # how many processors to use, if using multi processing
        self.num_of_processors = 5

    # set up the initial generation
    def setup(self, seed):
        # creates the fitness function and '1.0' stipulates its a max fitness function
        creator.create("fitness", base.Fitness, weights=(1.0,))
        # create a chromosome and assign the fitness function
        creator.create("Tactic", list, fitness=creator.fitness)

        # set the randomized seed for experimentation duplication
        random.seed(seed)

        # initialize the gene's to be used in the chromosome
        self.toolbox.register("px_min", Gene, self.MIN_DISTANCE, self.MAX_DISTANCE, True)
        self.toolbox.register("px_max", Gene, self.MIN_DISTANCE, self.MAX_DISTANCE, False)
        self.toolbox.register("py_min", Gene, self.MIN_DISTANCE, self.MAX_DISTANCE, True)
        self.toolbox.register("py_max", Gene, self.MIN_DISTANCE, self.MAX_DISTANCE, False)
        self.toolbox.register("pz_min", Gene, self.MIN_DISTANCE, self.MAX_DISTANCE, True)
        self.toolbox.register("pz_max", Gene, self.MIN_DISTANCE, self.MAX_DISTANCE, False)
        self.toolbox.register("vx_min", Gene, self.MIN_VELOCITY, self.MAX_VELOCITY, True)
        self.toolbox.register("vx_max", Gene, self.MIN_VELOCITY, self.MAX_VELOCITY, False)
        self.toolbox.register("vy_min", Gene, self.MIN_VELOCITY, self.MAX_VELOCITY, True)
        self.toolbox.register("vy_max", Gene, self.MIN_VELOCITY, self.MAX_VELOCITY, False)
        self.toolbox.register("vz_min", Gene, self.MIN_VELOCITY, self.MAX_VELOCITY, True)
        self.toolbox.register("vz_max", Gene, self.MIN_VELOCITY, self.MAX_VELOCITY, False)
        self.toolbox.register("ax_min", Gene, self.MIN_ACCELERATION, self.MAX_ACCELERATION, True)
        self.toolbox.register("ax_max", Gene, self.MIN_ACCELERATION, self.MAX_ACCELERATION, False)
        self.toolbox.register("ay_min", Gene, self.MIN_ACCELERATION, self.MAX_ACCELERATION, True)
        self.toolbox.register("ay_max", Gene, self.MIN_ACCELERATION, self.MAX_ACCELERATION, False)
        self.toolbox.register("az_min", Gene, self.MIN_ACCELERATION, self.MAX_ACCELERATION, True)
        self.toolbox.register("az_max", Gene, self.MIN_ACCELERATION, self.MAX_ACCELERATION, False)

        # Structure initializer
        # This defines tactic to be an object of class Tactic (our chromosome) populated by the different gene's
        # as there are 42 transitions, we repeat this gene sequence 42 OR cycles times to get the required length
        self.toolbox.register("tactic", tools.initCycle, creator.Tactic, (self.toolbox.px_min,
                                                                          self.toolbox.px_max,
                                                                          self.toolbox.py_min,
                                                                          self.toolbox.py_max,
                                                                          self.toolbox.pz_min,
                                                                          self.toolbox.pz_max,
                                                                          self.toolbox.vx_min,
                                                                          self.toolbox.vx_max,
                                                                          self.toolbox.vy_min,
                                                                          self.toolbox.vy_max,
                                                                          self.toolbox.vz_min,
                                                                          self.toolbox.vz_max,
                                                                          self.toolbox.ax_min,
                                                                          self.toolbox.ax_max,
                                                                          self.toolbox.ay_min,
                                                                          self.toolbox.ay_max,
                                                                          self.toolbox.az_min,
                                                                          self.toolbox.az_max), n=self.CYCLES)


        # the population of tactics (chromosomes), stored as a list and of size POP
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.tactic, self.POP)

        # create our initial population as a list "population"
        self.population = self.toolbox.population()

        # Operator registration
        # 2 point cross over to create child
        self.toolbox.register("mate", tools.cxTwoPoint)

        # register a mutation operator
        self.toolbox.register("mutate", helper.gaussian, mu=0, sigma=1.0, indpb=0.01)

        # Use SUS selection
        self.toolbox.register("select", tools.selStochasticUniversalSampling)

        # use our pre written evaluation function
        self.toolbox.register("evaluate", helper.multi_evaluate)

    # run the generations
    def run_algorithm(self, seed):
        # Set up hall of fame to keep track of the top chromosomes
        # custom hall of fame to track the generation it was found
        hall_of_fame = hof.HallOfFame(self.HOF_SIZE)
        # standard hall of fame that comes with DEAP
        hall_of_fame_with_dupes = hof.HallOfFameStandard(self.HOF_SIZE)

        # write out all text to a file
        file_name = str(seed) + '_with_HOF.txt'
        sys.stdout = open(file_name, 'w')

        print 'Seed:', seed

        # track the current generation
        i = 0
        while i < self.GENERATIONS and not self.isConverged:
            i += 1
            print('--------------------------------' + 'Generation: ' + str(i) + '-----------------------------------')
            # evaluate each chromosome in the population and assign its fitness score
            for index, x in enumerate(self.population):
                # update the chromosome, writes out to JSON tactics file
                chromosome_parameters.update_ecu_basic_chromosome(x)
                # use Ace0 to evaluate the chromosome
                x.fitness.values = helper.multi_evaluate(self.num_of_processors)

            # Select the best chromosome from this generation and display it
            best_chromosome = tools.selBest(self.population, 10)[0]

            print "Best chromosome is: ", best_chromosome.fitness.values

            # check if the best chromosome value has changed
            if float(best_chromosome.fitness.values[0]) == self.temp_best_fitness:
                self.converge_tracker_2 += 1
                if self.converge_tracker_2 >= self.converge_stagnant_fitness:
                    print 'CONVERGED due to stagnant fit'
                    self.isConverged = True
            else:
                self.converge_tracker_2 = 0

            self.temp_best_fitness = best_chromosome.fitness.values[0]

            # Get the over all fitness values
            sum_fits = sum(ind.fitness.values[0] for ind in self.population)
            average_fitness = sum_fits / self.POP
            print 'Generation average fitness: ', average_fitness

            csv_name = str(seed) + '_output.csv'
            f = open(csv_name, 'ab')
            writer = csv.writer(f)
            writer.writerow((str(i), str(best_chromosome.fitness.values[0]), str(average_fitness)))
            f.close()

            # save best and average fitness to plot lists
            self.plot_best_fitness.append(best_chromosome.fitness.values)
            self.plot_average_fitness.append(average_fitness)

            # Update the hall of fame to track the best chromosomes from each generation
            hall_of_fame.update(self.population, i)
            hall_of_fame_with_dupes.update(self.population)

            print ('-----------------------------------Hall Of Fame at Gen ' + str(i) + '-----------------------------------')
            hall_of_fame.print_hof()

            # this is where we evolve the population
            # Select the next generation individuals
            offspring = self.toolbox.select(self.population, len(self.population))
            # Clone the selected individuals so we can apply crossover
            offspring = list(map(self.toolbox.clone, offspring))

            # Apply crossover on the offspring
            for child1, child2 in zip(offspring[::2], offspring[::-2]):
                if random.random() < self.CROSSOVER_PROBABILITY:
                    # mate the two children
                    self.toolbox.mate(child1, child2)

            # Apply mutation on the offspring
            for mutant in offspring:
                if random.random() < self.MUTATION_PROBABILITY:
                    for index, x in enumerate(mutant):
                        mutant[index].value = helper.convert_range(mutant[index].value, mutant[index].min,
                                                                   mutant[index].max)

                    self.toolbox.mutate(mutant)

                    for index, x in enumerate(mutant):
                        mutant[index].value = helper.change_back(mutant[index].value, mutant[index].min,
                                                                 mutant[index].max)
                        # check if the mutated value is outside the min/max
                        helper.bounds_check(mutant[index])

            # The population is entirely replaced by the offspring
                self.population[:] = offspring

            # check to see if the avg fitness is the same as the best fitness
            if float(best_chromosome.fitness.values[0]) - average_fitness < 0.0001:
                self.converge_tracker += 1
                if self.converge_tracker >= self.converge_tracker_max:
                    print 'CONVERGED due to best = avg'
                    self.isConverged = True
            else:
                self.converge_tracker = 0

            # elitism, carry over the best chromosome from this generation
            self.population[0] = hall_of_fame[0]

        # print the hall of fame to file so we can access the chromosomes
        print ('-------------------------------------Hall Of Fame Regular----------------------------------------')
        for chromosomes in hall_of_fame_with_dupes:
            print 'Chromosome: ',   helper.list_to_string(chromosomes), 'Fitness: ', chromosomes.fitness

        print ('-------------------------------------Hall Of Fame with Gen----------------------------------------')
        hall_of_fame.print_hof()

        title = 'Seed: ' + str(seed)

        # save the chart to an image file
        visualization.draw_plot(title, self.plot_average_fitness, self.plot_best_fitness, 'average per generation',
                                'best fitness', 'average per generation', 'best fitness', 0, 250, 150, seed)

        # delete the created objects so we can loop and automate the GA process for many seeds
        del creator.fitness
        del creator.Tactic

    def run(self, seed):
        self.setup(seed)
        self.run_algorithm(seed)
