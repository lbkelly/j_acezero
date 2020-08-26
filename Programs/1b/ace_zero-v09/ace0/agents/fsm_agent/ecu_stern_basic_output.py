""" This module contains subclasses of StateAgent that combine the logic
of the park stern conversion agent with the transition logic to govern the
state changes. This agent will have the logic to preform the maneuvers right and up,
right and down, left and up, left and down, up, down and fly level.

The class EcuSternBasicAgent should be initialised to generate a new stern
conversion agent for execution.

NOTE - Much of the code is heavily based on lrbenke existing stern class
"""
# based on the code written by 'lrbenke'
__author__ = 'lbkelly'

from state_agent import StateAgent
import utils as ut
import helpers
import math
import random
from commands import *
import json
import agent_states


def transition(bool_a, bool_b, bool_c, bool_d, bool_e, bool_f,
               state_a, state_b, state_c, state_d, state_e, state_f):
    """
    Checks which states are legal and can be transitioned too.
    If more than one transition is legal, randomly pick a legal transition.

    TODO: after experiments, send in a list of booleans and states, not individual.

    :param bool_a: transition boolean, if true, the transition can happen
    :param state_a: possible state to transition too
    :return: the state to transition too
    """
    states = [state_a, state_b, state_c, state_d, state_e, state_f]
    list_of_bools = [bool_a, bool_b, bool_c, bool_d, bool_e, bool_f]
    legal = []
    for i, bool_value in enumerate(list_of_bools):
        if bool_value:
            legal.append(states[i])
    return legal[random.randint(0, len(legal) - 1)]


class EcuSternBasicAgent(StateAgent):
    """
    This class has basic instructions on flying an aircraft. It can only preform simple
    maneuvers like right up, right down, level flight, push down etc.
    """

    TRANSITION_COUNT = 0

    def __init__(self, params_filename=None):
        """
        Creates an agent that performs basic air flight maneuvers based on the
        Park agent paper.

        A new StateAgent is initialised with the states in this module. The
        transition parameters are set from a specified JSON file.

        Args:
            params_filename (string): optional json file containing tactical
              parameters to overwrite the default transition parameters

        Returns:
            (StateAgent): basic state agent
        """
        states = [LeftDown(), LeftUp(), PullUp(), LevelFlight(), PushDown(), RightUp(), RightDown()]

        # Pre-fill tactical parameters if json file is defined
        # if params_filename:
        #     with open(params_filename) as data_file:
        #         data = json.load(data_file)
        #         for state in states:
        #             state_classname = state.__class__.__name__
        #             if state_classname in data:
        #                 # Set parameters to the values defined in the json file
        #                 for param, value in data[state_classname].items():
        #                     setattr(state, param, value)

        StateAgent.__init__(self, states,
                            initial=[LeftUp])


    def update_states(self, tac_params):
        self.states.items()[0][1].PARAMETER_SET_ONE = tac_params[0]
        self.states.items()[0][1].PARAMETER_SET_TWO = tac_params[1]
        self.states.items()[0][1].PARAMETER_SET_THREE = tac_params[2]
        self.states.items()[0][1].PARAMETER_SET_FOUR = tac_params[3]
        self.states.items()[0][1].PARAMETER_SET_FIVE = tac_params[4]
        self.states.items()[0][1].PARAMETER_SET_SIX = tac_params[5]
        self.states.items()[1][1].PARAMETER_SET_ONE = tac_params[6]
        self.states.items()[1][1].PARAMETER_SET_TWO = tac_params[7]
        self.states.items()[1][1].PARAMETER_SET_THREE = tac_params[8]
        self.states.items()[1][1].PARAMETER_SET_FOUR = tac_params[9]
        self.states.items()[1][1].PARAMETER_SET_FIVE = tac_params[10]
        self.states.items()[1][1].PARAMETER_SET_SIX = tac_params[11]
        self.states.items()[2][1].PARAMETER_SET_ONE = tac_params[12]
        self.states.items()[2][1].PARAMETER_SET_TWO = tac_params[13]
        self.states.items()[2][1].PARAMETER_SET_THREE = tac_params[14]
        self.states.items()[2][1].PARAMETER_SET_FOUR = tac_params[15]
        self.states.items()[2][1].PARAMETER_SET_FIVE = tac_params[16]
        self.states.items()[2][1].PARAMETER_SET_SIX = tac_params[17]
        self.states.items()[3][1].PARAMETER_SET_ONE = tac_params[18]
        self.states.items()[3][1].PARAMETER_SET_TWO = tac_params[19]
        self.states.items()[3][1].PARAMETER_SET_THREE = tac_params[20]
        self.states.items()[3][1].PARAMETER_SET_FOUR = tac_params[21]
        self.states.items()[3][1].PARAMETER_SET_FIVE = tac_params[22]
        self.states.items()[3][1].PARAMETER_SET_SIX = tac_params[23]
        self.states.items()[4][1].PARAMETER_SET_ONE = tac_params[24]
        self.states.items()[4][1].PARAMETER_SET_TWO = tac_params[25]
        self.states.items()[4][1].PARAMETER_SET_THREE = tac_params[26]
        self.states.items()[4][1].PARAMETER_SET_FOUR = tac_params[27]
        self.states.items()[4][1].PARAMETER_SET_FIVE = tac_params[28]
        self.states.items()[4][1].PARAMETER_SET_SIX = tac_params[29]
        self.states.items()[5][1].PARAMETER_SET_ONE = tac_params[30]
        self.states.items()[5][1].PARAMETER_SET_TWO = tac_params[31]
        self.states.items()[5][1].PARAMETER_SET_THREE = tac_params[32]
        self.states.items()[5][1].PARAMETER_SET_FOUR = tac_params[33]
        self.states.items()[5][1].PARAMETER_SET_FIVE = tac_params[34]
        self.states.items()[5][1].PARAMETER_SET_SIX = tac_params[35]
        self.states.items()[6][1].PARAMETER_SET_ONE = tac_params[36]
        self.states.items()[6][1].PARAMETER_SET_TWO = tac_params[37]
        self.states.items()[6][1].PARAMETER_SET_THREE = tac_params[38]
        self.states.items()[6][1].PARAMETER_SET_FOUR = tac_params[39]
        self.states.items()[6][1].PARAMETER_SET_FIVE = tac_params[40]
        self.states.items()[6][1].PARAMETER_SET_SIX = tac_params[41]

class LeftDown(StateAgent):
    """
    This state points the fighter to the left and down
    """
    THETA_C = -90.0
    PSI_C = 30.0

    PARAMETER_SET_ONE = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    PARAMETER_SET_TWO = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    PARAMETER_SET_THREE = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    PARAMETER_SET_FOUR = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    PARAMETER_SET_FIVE = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    PARAMETER_SET_SIX = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    is_param_one = False
    is_param_two = False
    is_param_three = False
    is_param_four = False
    is_param_five = False
    is_param_six = False

    def on_entry(self):
        # ECU TESTING lbkelly 27/02/2017
        # print self.__class__.__name__
        self.__class__.__name__
        agent_states.statestring.append(self.__class__.__name__)


    def execute(self, t, dt):
        StateAgent.execute(self, t, dt)
        self.commands.append(SetPitchAngleCmd(theta_c=self.THETA_C))
        self.commands.append(SetHeadingGLoadCmd(psi_c=self.PSI_C + self.beliefs.entity_state.psi, gload_c=5))

    def process_state(self, t, dt):
        # Calculate the lateral distance to the threat aircraft
        StateAgent.process_state(self, t, dt)
        entity = self.beliefs.entity_state
        threat = self.beliefs.threat_state

        self.is_param_one = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PARAMETER_SET_ONE)
        self.is_param_two = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PARAMETER_SET_TWO)
        self.is_param_three = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PARAMETER_SET_THREE)
        self.is_param_four = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PARAMETER_SET_FOUR)
        self.is_param_five = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PARAMETER_SET_FIVE)
        self.is_param_six = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PARAMETER_SET_SIX)

        if self.is_param_one or self.is_param_two or self.is_param_three or self.is_param_four or self.is_param_five or self.is_param_six:
            self.transition_request = transition(self.is_param_one, self.is_param_two, self.is_param_three,
                                                 self.is_param_four, self.is_param_five, self.is_param_six, LeftUp, PullUp, LevelFlight, PushDown, RightUp, RightDown)


class LeftUp(StateAgent):
    """
    This state points the fighter to the left and up
    """
    THETA_C = 90.0
    PSI_C = 30.0

    PARAMETER_SET_ONE = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    PARAMETER_SET_TWO = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    PARAMETER_SET_THREE = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    PARAMETER_SET_FOUR = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    PARAMETER_SET_FIVE = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    PARAMETER_SET_SIX = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    is_param_one = False
    is_param_two = False
    is_param_three = False
    is_param_four = False
    is_param_five = False
    is_param_six = False

    def on_entry(self):
        # ECU TESTING lbkelly 27/02/2017
        # print self.__class__.__name__
        self.__class__.__name__
        agent_states.statestring.append(self.__class__.__name__)

    def execute(self, t, dt):
        StateAgent.execute(self, t, dt)
        self.commands.append(SetPitchAngleCmd(theta_c=self.THETA_C))
        self.commands.append(SetHeadingGLoadCmd(psi_c=self.PSI_C + self.beliefs.entity_state.psi, gload_c=5))

    def process_state(self, t, dt):
        StateAgent.process_state(self, t, dt)
        # Calculate the lateral distance to the threat aircraft
        entity = self.beliefs.entity_state
        threat = self.beliefs.threat_state

        self.is_param_one = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PARAMETER_SET_ONE)
        self.is_param_two = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PARAMETER_SET_TWO)
        self.is_param_three = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PARAMETER_SET_THREE)
        self.is_param_four = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PARAMETER_SET_FOUR)
        self.is_param_five = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PARAMETER_SET_FIVE)
        self.is_param_six = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PARAMETER_SET_SIX)

        if self.is_param_one or self.is_param_two or self.is_param_three or self.is_param_four or self.is_param_five or self.is_param_six:
            self.transition_request = transition(self.is_param_one, self.is_param_two, self.is_param_three,
                                                 self.is_param_four, self.is_param_five, self.is_param_six, LeftDown, PullUp, LevelFlight, PushDown, RightUp, RightDown)


class PullUp(StateAgent):
    """
    This state points the fighter up
    """
    THETA_C = 90.0

    PARAMETER_SET_ONE = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    PARAMETER_SET_TWO = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    PARAMETER_SET_THREE = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    PARAMETER_SET_FOUR = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    PARAMETER_SET_FIVE = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    PARAMETER_SET_SIX = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    is_param_one = False
    is_param_two = False
    is_param_three = False
    is_param_four = False
    is_param_five = False
    is_param_six = False

    def on_entry(self):
        # ECU TESTING lbkelly 27/02/2017
        # print self.__class__.__name__
        self.__class__.__name__
        agent_states.statestring.append(self.__class__.__name__)

    def execute(self, t, dt):
        StateAgent.execute(self, t, dt)
        self.commands.append(SetPitchAngleCmd(theta_c=self.THETA_C))

    def process_state(self, t, dt):
        StateAgent.process_state(self, t, dt)
        # Calculate the lateral distance to the threat aircraft
        entity = self.beliefs.entity_state
        threat = self.beliefs.threat_state

        self.is_param_one = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PARAMETER_SET_ONE)
        self.is_param_two = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PARAMETER_SET_TWO)
        self.is_param_three = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PARAMETER_SET_THREE)
        self.is_param_four = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PARAMETER_SET_FOUR)
        self.is_param_five = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PARAMETER_SET_FIVE)
        self.is_param_six = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PARAMETER_SET_SIX)

        if self.is_param_one or self.is_param_two or self.is_param_three or self.is_param_four or self.is_param_five or self.is_param_six:
            self.transition_request = transition(self.is_param_one, self.is_param_two, self.is_param_three,
                                                 self.is_param_four, self.is_param_five, self.is_param_six, LeftDown, LeftUp, LevelFlight, PushDown, RightUp, RightDown)


class LevelFlight(StateAgent):
    """
    This state makes the fighter fly level
    """

    PARAMETER_SET_ONE = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    PARAMETER_SET_TWO = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    PARAMETER_SET_THREE = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    PARAMETER_SET_FOUR = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    PARAMETER_SET_FIVE = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    PARAMETER_SET_SIX = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    is_param_one = False
    is_param_two = False
    is_param_three = False
    is_param_four = False
    is_param_five = False
    is_param_six = False

    def on_entry(self):
        # ECU TESTING lbkelly 27/02/2017
        # print self.__class__.__name__
        self.__class__.__name__
        agent_states.statestring.append(self.__class__.__name__)

    def execute(self, t, dt):
        StateAgent.execute(self, t, dt)
        self.commands.append(SetFlyLevelCmd())

    def process_state(self, t, dt):
        StateAgent.process_state(self, t, dt)
        # Calculate the lateral distance to the threat aircraft
        entity = self.beliefs.entity_state
        threat = self.beliefs.threat_state

        self.is_param_one = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PARAMETER_SET_ONE)
        self.is_param_two = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PARAMETER_SET_TWO)
        self.is_param_three = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PARAMETER_SET_THREE)
        self.is_param_four = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PARAMETER_SET_FOUR)
        self.is_param_five = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PARAMETER_SET_FIVE)
        self.is_param_six = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PARAMETER_SET_SIX)

        if self.is_param_one or self.is_param_two or self.is_param_three or self.is_param_four or self.is_param_five or self.is_param_six:
            self.transition_request = transition(self.is_param_one, self.is_param_two, self.is_param_three,
                                                 self.is_param_four, self.is_param_five, self.is_param_six, LeftDown, LeftUp, PullUp, PushDown, RightUp, RightDown)


class PushDown(StateAgent):
    """
    This state points the fighter down
    """
    THETA_C = -90.0

    PARAMETER_SET_ONE = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    PARAMETER_SET_TWO = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    PARAMETER_SET_THREE = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    PARAMETER_SET_FOUR = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    PARAMETER_SET_FIVE = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    PARAMETER_SET_SIX = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    is_param_one = False
    is_param_two = False
    is_param_three = False
    is_param_four = False
    is_param_five = False
    is_param_six = False

    def on_entry(self):
        # ECU TESTING lbkelly 27/02/2017
        # print self.__class__.__name__
        self.__class__.__name__
        agent_states.statestring.append(self.__class__.__name__)

    def execute(self, t, dt):
        StateAgent.execute(self, t, dt)
        self.commands.append(SetPitchAngleCmd(theta_c=self.THETA_C))

    def process_state(self, t, dt):
        StateAgent.process_state(self, t, dt)
        # Calculate the lateral distance to the threat aircraft
        entity = self.beliefs.entity_state
        threat = self.beliefs.threat_state

        self.is_param_one = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PARAMETER_SET_ONE)
        self.is_param_two = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PARAMETER_SET_TWO)
        self.is_param_three = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PARAMETER_SET_THREE)
        self.is_param_four = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PARAMETER_SET_FOUR)
        self.is_param_five = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PARAMETER_SET_FIVE)
        self.is_param_six = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PARAMETER_SET_SIX)

        if self.is_param_one or self.is_param_two or self.is_param_three or self.is_param_four or self.is_param_five or self.is_param_six:
            self.transition_request = transition(self.is_param_one, self.is_param_two, self.is_param_three,
                                                 self.is_param_four, self.is_param_five, self.is_param_six, LeftDown, LeftUp, PullUp, LevelFlight, RightUp, RightDown)


class RightUp(StateAgent):
    """
    This state points the fighter to the right and up
    """
    THETA_C = 90.0
    PSI_C = -30.0

    PARAMETER_SET_ONE = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    PARAMETER_SET_TWO = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    PARAMETER_SET_THREE = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    PARAMETER_SET_FOUR = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    PARAMETER_SET_FIVE = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    PARAMETER_SET_SIX = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    is_param_one = False
    is_param_two = False
    is_param_three = False
    is_param_four = False
    is_param_five = False
    is_param_six = False

    def on_entry(self):
        # ECU TESTING lbkelly 27/02/2017
        # print self.__class__.__name__
        self.__class__.__name__
        agent_states.statestring.append(self.__class__.__name__)

    def execute(self, t, dt):
        StateAgent.execute(self, t, dt)
        self.commands.append(SetPitchAngleCmd(theta_c=self.THETA_C))
        self.commands.append(SetHeadingGLoadCmd(psi_c=self.PSI_C + self.beliefs.entity_state.psi, gload_c=5))

    def process_state(self, t, dt):
        StateAgent.process_state(self, t, dt)
        # Calculate the lateral distance to the threat aircraft
        entity = self.beliefs.entity_state
        threat = self.beliefs.threat_state

        self.is_param_one = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PARAMETER_SET_ONE)
        self.is_param_two = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PARAMETER_SET_TWO)
        self.is_param_three = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PARAMETER_SET_THREE)
        self.is_param_four = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PARAMETER_SET_FOUR)
        self.is_param_five = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PARAMETER_SET_FIVE)
        self.is_param_six = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PARAMETER_SET_SIX)

        if self.is_param_one or self.is_param_two or self.is_param_three or self.is_param_four or self.is_param_five or self.is_param_six:
            self.transition_request = transition(self.is_param_one, self.is_param_two, self.is_param_three,
                                                 self.is_param_four, self.is_param_five, self.is_param_six, LeftDown, LeftUp, PullUp, LevelFlight, PushDown, RightDown)


class RightDown(StateAgent):
    """
    This state points the fighter to the right and down
    """
    THETA_C = -90.0
    PSI_C = -30.0

    PARAMETER_SET_ONE = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    PARAMETER_SET_TWO = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    PARAMETER_SET_THREE = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    PARAMETER_SET_FOUR = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    PARAMETER_SET_FIVE = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    PARAMETER_SET_SIX = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    is_param_one = False
    is_param_two = False
    is_param_three = False
    is_param_four = False
    is_param_five = False
    is_param_six = False

    def on_entry(self):
        # ECU TESTING lbkelly 27/02/2017
        # print self.__class__.__name__
        self.__class__.__name__
        agent_states.statestring.append(self.__class__.__name__)

    def execute(self, t, dt):
        StateAgent.execute(self, t, dt)
        self.commands.append(SetPitchAngleCmd(theta_c=self.THETA_C))
        self.commands.append(SetHeadingGLoadCmd(psi_c=self.PSI_C + self.beliefs.entity_state.psi, gload_c=5))

    def process_state(self, t, dt):
        StateAgent.process_state(self, t, dt)
        # Calculate the lateral distance to the threat aircraft
        entity = self.beliefs.entity_state
        threat = self.beliefs.threat_state

        self.is_param_one = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PARAMETER_SET_ONE)
        self.is_param_two = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PARAMETER_SET_TWO)
        self.is_param_three = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PARAMETER_SET_THREE)
        self.is_param_four = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PARAMETER_SET_FOUR)
        self.is_param_five = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PARAMETER_SET_FIVE)
        self.is_param_six = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PARAMETER_SET_SIX)

        if self.is_param_one or self.is_param_two or self.is_param_three or self.is_param_four or self.is_param_five or self.is_param_six:
            self.transition_request = transition(self.is_param_one, self.is_param_two, self.is_param_three,
                                                 self.is_param_four, self.is_param_five, self.is_param_six, LeftDown, LeftUp, PullUp, LevelFlight, PushDown, RightUp)
