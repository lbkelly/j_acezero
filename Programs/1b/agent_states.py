import csv

statestring = []

def main():

    agents_csv = 'agentStates.csv'
    agent_file = open(agents_csv, 'ab')
    states = csv.writer(agent_file)

    states.writerow(statestring)

    agent_file.close()

    # for index, item in enumerate(statestring):
    #     print statestring[index]
    #     del statestring[index]
    #
    # for index, item in enumerate(statestring):
    #     print "still here", statestring[index]

    return

if __name__ == "__main__":
    main()