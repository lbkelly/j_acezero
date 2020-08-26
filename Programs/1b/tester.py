import helpers
import decimal
import cPickle
from helpers import Gene1 as gene

def main():

    # Load the test set from the pickle file
    with open("r1_testset.pkl", "r") as cp_file:
        cp = cPickle.load(cp_file)
    test_set = cp["population"]

    for index, x in enumerate(test_set):
        print x[0].value, x[1].value, x[2].value, x[3].value, x[4].value

if __name__ == "__main__":
    main()