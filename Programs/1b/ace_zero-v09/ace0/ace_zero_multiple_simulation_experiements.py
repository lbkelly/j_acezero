#!/usr/env python

"""
Calls the ACE ZERO main function.
Runs the simulation and then calls XCombat to display the trajectories of the
two fighters.

Note that ace_zero has been developed using Python 2.7
and scientific python stack. There are dependencies on NumPy and matplotlib.

We have been using Continuum Analytics' Anaconda Python Distribution.

The code hasn't been fully tested (still in alpha).

The code has been developed on Apple MacOS X 10.11.12 El Capitan
and Microsoft Windows 10. Still need to test it under Linux.

TODO:
- Port to Python 3.5 (this shoulnd't be too much effort)
"""

__author__ = 'mikepsn, lrbenke'

import argparse
import os
import sys
import csv
import charts
import simulation


def parse_arguments(args):
    parser = argparse.ArgumentParser(description='ACE ZERO Simulator')
    parser.add_argument('--scenario', default=None,
                        help='Specifies what scenario is to be simulated')
    parser.add_argument('--graph', action='store_true',
                        help='Show graph of aircraft trajectories')
    parser.add_argument('--noxcombat', action='store_true',
                        help='Hide xcombat visualisation of run results')
    parser.add_argument('--critics', action='store_true',
                        help='Display performance critic graphs')
    parser.add_argument('--xcombat_path', default=None,
                        help='Optional path to XCombat executable.')
    args = parser.parse_args(args)
    return args


def load_scenario(scenario_uri):
    """ Loads and returns a scenario from the specified json file. """
    import os
    import json

    if scenario_uri is not None:
        # Check it is a valid path
        if not os.path.exists(scenario_uri):
            raise SystemExit("Scenario file '{}' does not exist".
                             format(scenario_uri))
        try:
            with open(scenario_uri) as instream:
                return json.load(instream)
        except IOError as e:
            raise SystemExit("Error opening scenario file '{}'\n{}".
                             format(scenario_uri, str(e)))


def run_ace_zero(scenario=None, graph=False, critics=False, noxcombat=False,
                 xcombat_path=None):
    """ Executes a simulation of the scenario provided and returns the aircraft
    trajectories. """
    # Load scenario from path if provided
    if isinstance(scenario, basestring):
        scenario = load_scenario(scenario)

    # Run the simulation
    ace_zero = simulation.MultiAgentSimulation(scenario)
    ace_zero.run()

    # # Generate the run output files in XCombat format
    # run = xc.XCombatRun()
    # run.update_history([ace_zero.viper.history, ace_zero.cobra.history])
    # run.generate_run_history()

    viper_trace = ace_zero.viper.fcs.platform.trace
    cobra_trace = ace_zero.cobra.fcs.platform.trace


    # if not noxcombat:
    #     # Display aircraft trajectories using XCombat
    #     if not xcombat_path:
    #         xcombat_path = find_xcombat()
    #
    #     if xcombat_path:
    #         try:
    #             run_output_path = os.path.abspath(run.file.name)
    #             #subprocess.call([xcombat_path, run_output_path],
    #             #                cwd=os.path.dirname(xcombat_path))
    #             args = [xcombat_path, run_output_path]
    #             subprocess.Popen(args, cwd=os.path.dirname(xcombat_path))
    #
    #         except:
    #             print "Could not run XCombat, check that the path to the " + \
    #                   "executable is correct: '" + xcombat_path + "'"
    #     else:
    #         print "Could not find XCombat executable. Specify path or " + \
    #               "install in a subdirectory of ACE Zero."

    # if graph:
    #     # Display aircraft trajectories using matplotlib3d
    #     charts.draw_trajectories(viper_trace, cobra_trace)

    # charts.draw_trajectories(viper_trace, cobra_trace)

    # if critics:
    #     # Display the performance critic graphs
    #     for critic in ace_zero.umpire.performance_critics:
    #         critic.draw_chart()

    # ---for graphs
    # charts.draw_trajectories(viper_trace, cobra_trace)
    # print ace_zero.viper.score
    return ace_zero.viper.score


def find_xcombat():
    """ Searches for the XCombat executable under the ACE Zero directory and
    returns the absolute path if found. """
    path = os.path.dirname(__file__)
    for root, dirs, files in os.walk(path):
        for filename in files:
            if ("xcombat" in filename.lower() and
                    filename.lower().endswith(".exe")):
                return os.path.join(root, filename)
    return None


def return_fitness_ace_zero():
    args = parse_arguments(sys.argv[1:])
    score = run_ace_zero(**vars(args))
    print score
    return score

def return_multiple_run_fitness(reps):
    score = 0
    for x in range(reps):
        args = parse_arguments(sys.argv[1:])
        score += run_ace_zero(**vars(args))
    # print score / reps
    return score / reps

if __name__ == '__main__':
    # how many repetitions per chromosome
    simulation_number = 5
    # how many generations
    runs = 100
    for x in range(runs):
        # run the ace zero simulations and write out to csv file
        csv_name = str(simulation_number) + '_simulations_per_run_stern_vs_straight_from_seed_1001_at_gen_150.csv'
        f = open(csv_name, 'ab')
        writer = csv.writer(f)
        writer.writerow((str(x), str(return_multiple_run_fitness(simulation_number))))
        f.close()
