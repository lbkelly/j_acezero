import write_chromosome as wc
import write_initial_values as initial_values
import helpers as helper
import random
import visualization
import datetime
import sys
import hall_off_fame as hof
from deap import tools, base, creator

"""
The Genetic Algorithm used for the ECU basic(Park) agent for part of 1a.

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


class TacticalParameterGA:
    def __init__(self):
        self.toolbox = base.Toolbox()

        # Lists for the plots
        self.plot_best_fitness = []
        self.plot_average_fitness = []
        self.plot_worst_fitness = []

        # create our initial population as a list "population"
        self.population = ''

        # min and max turn range specified by the DSTG
        self.MIN_TURN_RANGE, self.MAX_TURN_RANGE = 0.1, 100
        # min and max turn angle specified by the DSTG
        self.MIN_TURN_ANGLE, self.MAX_TURN_ANGLE = -90, 90
        # min and max displacement specified by the DSTG
        self.MIN_DISP, self.MAX_DISP = 0, 180000
        # min and max conversion range specified by the DSTG
        self.MIN_CONVERSION_RANGE, self.MAX_CONVERSION_RANGE = 0, 30
        # min and max no closer range specified by the DSTG
        self.MIN_CLOSER_RANGE, self.MAX_CLOSER_RANGE = 500, 3000

        # how many cycles the chromosome will repeat the data, we want only 1 cycle to happen
        self.CYCLES = 1

        # how many repetitions to run the simulation for to get a fitness score
        self.repetitions = 1

        # how many chromosomes in each population
        self.POP = 50

        # how many generations to run the algorithm
        self.GENERATIONS = 200

        # crossover and mutation probabilities
        self.CROSSOVER_PROBABILITY = 0.6
        self.MUTATION_PROBABILITY = 1.0

        self.HOF_SIZE = 5

        self.converge_tracker = 0
        self.converge_tracker_max = 10
        self.isConverged = False

    # set up the initial generation
    def setup(self, seed):
        seed = seed
        # creates the fitness function and '1.0' stipulates its a max fitness function
        creator.create("fitness", base.Fitness, weights=(1.0,))
        # create a chromosome and assign the fitness function
        creator.create("Tactic", list, fitness=creator.fitness)

        # set the randomized seed for experimentation duplication
        random.seed(seed)

        # Attribute generator
        # Defines what values our tactic chromosomes can have
        self.toolbox.register("turn_range", Gene, self.MIN_TURN_RANGE, self.MAX_TURN_RANGE)
        self.toolbox.register("turn_angle", Gene, self.MIN_TURN_ANGLE, self.MAX_TURN_ANGLE)
        self.toolbox.register("desired_displacement", Gene, self.MIN_DISP, self.MAX_DISP)
        self.toolbox.register("conversion_range", Gene, self.MIN_CONVERSION_RANGE, self.MAX_CONVERSION_RANGE)
        self.toolbox.register("no_closer_range", Gene, self.MIN_CLOSER_RANGE, self.MAX_CLOSER_RANGE)

        # Structure initializer
        # This defines tactic to be an object of class Tactic populated by the attribute generators
        self.toolbox.register("tactic", tools.initCycle, creator.Tactic, (self.toolbox.turn_range,
                                                                          self.toolbox.turn_angle,
                                                                          self.toolbox.desired_displacement,
                                                                          self.toolbox.conversion_range,
                                                                          self.toolbox.no_closer_range), n=self.CYCLES)

        # the population of tactics, stored as a list and of size POP
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.tactic, self.POP)

        # create our initial population as a list "population"
        self.population = self.toolbox.population()

        # Operator registration
        # 1 point cross over to create child
        self.toolbox.register("mate", tools.cxOnePoint)

        # register a mutation operator
        self.toolbox.register("mutate", helper.gaussian, mu=0, sigma=1.0, indpb=0.1)

        # Use SUS selection
        # self.toolbox.register("select", tools.selStochasticUniversalSampling)
        self.toolbox.register("select", helper.selRanked)

        # use our pre written evaluation function
        self.toolbox.register("evaluate", helper.evaluate)

    # run the generations
    def run_algorithm(self, seed):
        # Set up custom hall of fame to keep track of the top chromosomes and their generations
        hall_of_fame = hof.HallOfFame(self.HOF_SIZE)
        # set up standard hall of fame that comes with DEAP
        hall_of_fame_with_dupes = tools.HallOfFame(self.HOF_SIZE)
        # Get date and time
        date_time = datetime.datetime.now().strftime("%m-%d_%I%M%p")

        # print out to file
        file_name = date_time + '.txt'
        sys.stdout = open(file_name, 'w')

        print 'Seed:', seed

        i = 0
        while i < self.GENERATIONS and not self.isConverged:
            i += 1
            print('--------------------------------' + 'Generation: ' + str(i) + '-----------------------------------')
            # evaluate each chromosome in the population and assign its fitness score
            for index, x in enumerate(self.population):
                # update the chromosome, write out to JSON tactical file
                chromosome_parameters.update_chromosome(x[0].value, x[1].value, x[2].value, x[3].value, x[4].value)
                # use Ace0 to evaluate the chromosome
                x.fitness.values = helper.evaluate(self.repetitions)

            # Select the best chromosome from this generation and display it
            best_chromosome = tools.selBest(self.population, 1)[0]
            print "Best chromosome is: ", helper.list_to_string(best_chromosome), best_chromosome.fitness.values

            # Select worst chromosome and display
            worst_chromosome = tools.selWorst(self.population, 1)[0]
            print "Worst chromosome is: ", helper.list_to_string(worst_chromosome), worst_chromosome.fitness.values

            # Get the over all fitness values
            sum_fits = sum(ind.fitness.values[0] for ind in self.population)
            average_fitness = sum_fits / self.POP
            print 'Generation average fitness: ', average_fitness

            # save best and average fitness to plot lists
            self.plot_best_fitness.append(best_chromosome.fitness.values)
            self.plot_average_fitness.append(average_fitness)
            self.plot_worst_fitness.append(worst_chromosome.fitness.values)

            # Update the hall of fame to track the best chromosomes from each generation
            hall_of_fame.update(self.population, i)
            hall_of_fame_with_dupes.update(self.population)

            # hall_of_fame.print_hof()

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
                    # print 'Mutated Chromosome before: ', helper.list_to_string(mutant)
                    for index, x in enumerate(mutant):
                        mutant[index].value = helper.convert_range(mutant[index].value, mutant[index].min,
                                                                   mutant[index].max)

                    self.toolbox.mutate(mutant)

                    for index, x in enumerate(mutant):
                        mutant[index].value = helper.change_back(mutant[index].value, mutant[index].min,
                                                                 mutant[index].max)
                        helper.bounds_check(mutant[index])

                    # print 'Mutated Chromosome after: ', helper.list_to_string(mutant)

            # The population is entirely replaced by the offspring
            self.population[:] = offspring

            if float(best_chromosome.fitness.values[0]) - average_fitness < 0.0001:
                self.converge_tracker += 1
                if self.converge_tracker >= self.converge_tracker_max:
                    print 'CONVERGED'
                    self.isConverged = True
            else:
                self.converge_tracker = 0

            # # Elitism
            self.population[0] = hall_of_fame_with_dupes[0]

        print ('-------------------------------------Hall Of Fame Regular----------------------------------------')
        for chromosomes in hall_of_fame_with_dupes:
            print 'Chromosome: ',   helper.list_to_string(chromosomes), 'Fitness: ', chromosomes.fitness

        print ('-------------------------------------Hall Of Fame with Gen----------------------------------------')
        hall_of_fame.print_hof()

        print ('-------------------------------------Stats----------------------------------------')
        print("Pop size: " + str(self.POP))
        print("Generations: " + str(self.GENERATIONS))
        print("Crossover Prob: " + str(self.CROSSOVER_PROBABILITY))
        print("Mutation Prob: " + str(self.MUTATION_PROBABILITY))

        # Select the best chromosome from this generation and display it
        best_chromosome = tools.selBest(self.population, 1)[0]
        print "Best chromosome is: ", helper.list_to_string(best_chromosome), best_chromosome.fitness.values

        # Select worst chromosome and display
        worst_chromosome = tools.selWorst(self.population, 1)[0]
        print "Worst chromosome is: ", helper.list_to_string(worst_chromosome), worst_chromosome.fitness.values

        # Get the over all fitness values
        sum_fits = sum(ind.fitness.values[0] for ind in self.population)
        average_fitness = sum_fits / self.POP
        print 'Generation average fitness: ', average_fitness

        title = 'Seed: ' + str(seed)

        visualization.draw_plot(title, self.plot_average_fitness, self.plot_best_fitness, self.plot_worst_fitness, 'average per generation',
                                'best fitness', 'worst fitness', 'generation', 'fitness', 1, 250, 150, date_time)

        del creator.fitness
        del creator.Tactic

    def run(self, seed):
        self.setup(seed)
        self.run_algorithm(seed)

