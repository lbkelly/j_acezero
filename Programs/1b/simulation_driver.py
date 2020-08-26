import ace_zero

"""
Driver script to run the multiple simulation experiments
"""

__author__ = 'lbkelly'


def main():
    # set your initial seed and number of experiments
    number_of_experiments = 100

    # run the simulation experiments
    simulations = [ace_zero.run_ace_zero() for i in range(number_of_experiments)]

    # for simulation in simulations:
    #     simulation.run()
    #     del simulation

if __name__ == "__main__":
    main()
