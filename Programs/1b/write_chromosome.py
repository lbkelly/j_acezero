import helpers
import os

"""
A test script for saving out chromosomes to a JSON file
"""

__author__ = 'lbkelly'


class WriteChromosome:
    def __init__(self):
        self.turn_range = 0
        self.turn_angle = 0
        self.displacement = 0
        self.conversion_range = 0
        self.no_close_range = 0
        self.file_path = 0

    def update_ecu_chromosome(self, parameters):
        step = 18
        offset = 18
        temp = []
        param = list(parameters)
        param_values = []

        for gene in param:
            param_values.append(gene.value)

        for i in xrange(12):
            temp.append(param_values[step - offset:step])
            step += offset



        chromosome = {
                      "EcuConverting":
                      {
                        "PARAMETER_SET_ONE": temp[0],
                        "PARAMETER_SET_TWO": temp[1],
                        "PARAMETER_SET_THREE": temp[2]
                      },
                      "EcuFlyRelativeBearing":
                      {
                        "PARAMETER_SET_ONE": temp[3],
                        "PARAMETER_SET_TWO": temp[4],
                        "PARAMETER_SET_THREE": temp[5]
                      },
                      "EcuFlyingOffset":
                      {
                        "PARAMETER_SET_ONE": temp[6],
                        "PARAMETER_SET_TWO": temp[7],
                        "PARAMETER_SET_THREE": temp[8]
                      },
                      "EcuPureIntercept":
                      {
                        "PARAMETER_SET_ONE": temp[9],
                        "PARAMETER_SET_TWO": temp[10],
                        "PARAMETER_SET_THREE": temp[11]
                      }
                    }

        helpers.save_chromosome_to_file(chromosome,
                                        (os.path.dirname(__file__)) +
                                        r"\ace_zero-v09\ace0\data\ecu_blue_tactics.json")

    def update_ecu_basic_chromosome(self, parameters):
        step = 18
        offset = 18
        temp = []
        param = list(parameters)
        param_values = []

        for gene in param:
            param_values.append(gene.value)

        for i in xrange(42):
            temp.append(param_values[step - offset:step])
            step += offset

        chromosome = {
                      "LeftDown":
                      {
                        "PARAMETER_SET_ONE": temp[0],
                        "PARAMETER_SET_TWO": temp[1],
                        "PARAMETER_SET_THREE": temp[2],
                        "PARAMETER_SET_FOUR": temp[3],
                        "PARAMETER_SET_FIVE": temp[4],
                        "PARAMETER_SET_SIX": temp[5]
                      },
                      "LeftUp":
                      {
                        "PARAMETER_SET_ONE": temp[6],
                        "PARAMETER_SET_TWO": temp[7],
                        "PARAMETER_SET_THREE": temp[8],
                        "PARAMETER_SET_FOUR": temp[9],
                        "PARAMETER_SET_FIVE": temp[10],
                        "PARAMETER_SET_SIX": temp[11]
                      },
                      "PullUp":
                      {
                        "PARAMETER_SET_ONE": temp[12],
                        "PARAMETER_SET_TWO": temp[13],
                        "PARAMETER_SET_THREE": temp[14],
                        "PARAMETER_SET_FOUR": temp[15],
                        "PARAMETER_SET_FIVE": temp[16],
                        "PARAMETER_SET_SIX": temp[17]
                      },
                      "LevelFlight":
                      {
                        "PARAMETER_SET_ONE": temp[18],
                        "PARAMETER_SET_TWO": temp[19],
                        "PARAMETER_SET_THREE": temp[20],
                        "PARAMETER_SET_FOUR": temp[21],
                        "PARAMETER_SET_FIVE": temp[22],
                        "PARAMETER_SET_SIX": temp[23]
                      },
                      "PushDown":
                      {
                        "PARAMETER_SET_ONE": temp[24],
                        "PARAMETER_SET_TWO": temp[25],
                        "PARAMETER_SET_THREE": temp[26],
                        "PARAMETER_SET_FOUR": temp[27],
                        "PARAMETER_SET_FIVE": temp[28],
                        "PARAMETER_SET_SIX": temp[29]
                      },
                      "RightUp":
                      {
                        "PARAMETER_SET_ONE": temp[30],
                        "PARAMETER_SET_TWO": temp[31],
                        "PARAMETER_SET_THREE": temp[32],
                        "PARAMETER_SET_FOUR": temp[33],
                        "PARAMETER_SET_FIVE": temp[34],
                        "PARAMETER_SET_SIX": temp[35]
                      },
                      "RightDown":
                      {
                        "PARAMETER_SET_ONE": temp[36],
                        "PARAMETER_SET_TWO": temp[37],
                        "PARAMETER_SET_THREE": temp[38],
                        "PARAMETER_SET_FOUR": temp[39],
                        "PARAMETER_SET_FIVE": temp[40],
                        "PARAMETER_SET_SIX": temp[41]
                      }
                     }

        helpers.save_chromosome_to_file(chromosome,
                                        (os.path.dirname(__file__)) +
                                        r"\ace_zero-v09\ace0\data\ecu_basic_blue_tactics.json")

    def update_blue_chromosome(self, turn_range, turn_angle, displacement, conversion_range, no_close_range):
        self.turn_range = turn_range
        self.turn_angle = turn_angle
        self.displacement = displacement
        self.conversion_range = conversion_range
        self.no_close_range = no_close_range

        chromosome = {'PureIntercept': {
            'TURN_RANGE': self.turn_range
        }, 'FlyRelativeBearing': {
            'TURN_ANGLE': self.turn_angle,
            'DESIRED_DISPLACEMENT': self.displacement
        }, 'FlyingOffset': {
            'CONVERSION_RANGE': self.conversion_range
        }, 'Converting': {
            'NO_CLOSER_RANGE': self.no_close_range
        }}

        helpers.save_chromosome_to_file(chromosome,
                                        (os.path.dirname(__file__)) +
                                        r"\ace_zero-v09\ace0\data\blue_tactics.json")

    def update_red_chromosome(self, turn_range, turn_angle, displacement, conversion_range, no_close_range):
        self.turn_range = turn_range
        self.turn_angle = turn_angle
        self.displacement = displacement
        self.conversion_range = conversion_range
        self.no_close_range = no_close_range

        chromosome = {'PureIntercept': {
            'TURN_RANGE': self.turn_range
        }, 'FlyRelativeBearing': {
            'TURN_ANGLE': self.turn_angle,
            'DESIRED_DISPLACEMENT': self.displacement
        }, 'FlyingOffset': {
            'CONVERSION_RANGE': self.conversion_range
        }, 'Converting': {
            'NO_CLOSER_RANGE': self.no_close_range
        }}

        helpers.save_chromosome_to_file(chromosome,
                                        (os.path.dirname(__file__)) +
                                        r"\ace_zero-v09\ace0\data\red_tactics.json")


    def load_basic_ecu_chromosome(self, parameters):
        step = 18
        offset = 18
        temp = []
        for i in xrange(42):
            temp.append(parameters[step - offset:step])
            step += offset

        chromosome = {
            "LeftDown":
                {
                    "PARAMETER_SET_ONE": temp[0],
                    "PARAMETER_SET_TWO": temp[1],
                    "PARAMETER_SET_THREE": temp[2],
                    "PARAMETER_SET_FOUR": temp[3],
                    "PARAMETER_SET_FIVE": temp[4],
                    "PARAMETER_SET_SIX": temp[5]
                },
            "LeftUp":
                {
                    "PARAMETER_SET_ONE": temp[6],
                    "PARAMETER_SET_TWO": temp[7],
                    "PARAMETER_SET_THREE": temp[8],
                    "PARAMETER_SET_FOUR": temp[9],
                    "PARAMETER_SET_FIVE": temp[10],
                    "PARAMETER_SET_SIX": temp[11]
                },
            "PullUp":
                {
                    "PARAMETER_SET_ONE": temp[12],
                    "PARAMETER_SET_TWO": temp[13],
                    "PARAMETER_SET_THREE": temp[14],
                    "PARAMETER_SET_FOUR": temp[15],
                    "PARAMETER_SET_FIVE": temp[16],
                    "PARAMETER_SET_SIX": temp[17]
                },
            "LevelFlight":
                {
                    "PARAMETER_SET_ONE": temp[18],
                    "PARAMETER_SET_TWO": temp[19],
                    "PARAMETER_SET_THREE": temp[20],
                    "PARAMETER_SET_FOUR": temp[21],
                    "PARAMETER_SET_FIVE": temp[22],
                    "PARAMETER_SET_SIX": temp[23]
                },
            "PushDown":
                {
                    "PARAMETER_SET_ONE": temp[24],
                    "PARAMETER_SET_TWO": temp[25],
                    "PARAMETER_SET_THREE": temp[26],
                    "PARAMETER_SET_FOUR": temp[27],
                    "PARAMETER_SET_FIVE": temp[28],
                    "PARAMETER_SET_SIX": temp[29]
                },
            "RightUp":
                {
                    "PARAMETER_SET_ONE": temp[30],
                    "PARAMETER_SET_TWO": temp[31],
                    "PARAMETER_SET_THREE": temp[32],
                    "PARAMETER_SET_FOUR": temp[33],
                    "PARAMETER_SET_FIVE": temp[34],
                    "PARAMETER_SET_SIX": temp[35]
                },
            "RightDown":
                {
                    "PARAMETER_SET_ONE": temp[36],
                    "PARAMETER_SET_TWO": temp[37],
                    "PARAMETER_SET_THREE": temp[38],
                    "PARAMETER_SET_FOUR": temp[39],
                    "PARAMETER_SET_FIVE": temp[40],
                    "PARAMETER_SET_SIX": temp[41]
                }
        }

        helpers.save_chromosome_to_file(chromosome,
                                        (os.path.dirname(__file__)) +
                                        r"\ace_zero-v09\ace0\data\ecu_basic_blue_tactics.json")

    def load_ecu_chromosome(self, parameters):
        step = 18
        offset = 18
        temp = []
        for i in xrange(42):
            temp.append(parameters[step - offset:step])
            step += offset

        chromosome = {
            "EcuConverting":
                {
                    "PARAMETER_SET_ONE": temp[0],
                    "PARAMETER_SET_TWO": temp[1],
                    "PARAMETER_SET_THREE": temp[2]
                },
            "EcuFlyRelativeBearing":
                {
                    "PARAMETER_SET_ONE": temp[3],
                    "PARAMETER_SET_TWO": temp[4],
                    "PARAMETER_SET_THREE": temp[5]
                },
            "EcuFlyingOffset":
                {
                    "PARAMETER_SET_ONE": temp[6],
                    "PARAMETER_SET_TWO": temp[7],
                    "PARAMETER_SET_THREE": temp[8]
                },
            "EcuPureIntercept":
                {
                    "PARAMETER_SET_ONE": temp[9],
                    "PARAMETER_SET_TWO": temp[10],
                    "PARAMETER_SET_THREE": temp[11]
                }
        }

        helpers.save_chromosome_to_file(chromosome,
                                        (os.path.dirname(__file__)) +
                                        r"\ace_zero-v09\ace0\data\ecu_blue_tactics.json")
