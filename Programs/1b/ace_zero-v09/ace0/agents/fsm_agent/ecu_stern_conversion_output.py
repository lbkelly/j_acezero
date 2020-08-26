from state_agent import StateAgent
import random
from stern_conversion import PureIntercept, FlyRelativeBearing, FlyingOffset, Converting, MatchAltitude
import utils as ut
import helpers
import math
import json
import agent_states
"""
This module contains subclasses of stern conversion, which is based on the state agent.
This is the testing class for the new stern conversion agent using a GA to evolve
the transitions between each state. It uses the tactical provided by 'lrbenke' with new
state transition logic.
"""
# based on the code written by 'lrbenke'
__author__ = 'lbkelly'


def transition(bool_a, bool_b, bool_c, state_a, state_b, state_c):
    """
    Checks which states are legal and can be transitioned too.
    If more than one transition is legal, randomly pick a legal transition.

    TODO: after experiments, send in a list of booleans and states, not individual.

    :param bool_a: transition boolean, if true, the transition can happen
    :param state_a: possible state to transition too
    :return: the state to transition too
    """
    states = [state_a, state_b, state_c]
    list_of_bools = [bool_a, bool_b, bool_c]
    legal = []
    for i, bool_value in enumerate(list_of_bools):
        if bool_value:
            legal.append(states[i])
    return legal[random.randint(0, len(legal) - 1)]


class EcuSternConversionAgent(StateAgent):
    """
    This class represents an agent that performs a stern conversion manoeuvre
    against a target aircraft.

    To execute a stern conversion correctly the aircraft must be in the forward
    quarter of the threat aircraft at the beginning of the operation. If the
    target aspect angle is too great the agent will not be able to achieve the
    correct lateral separation to execute the manoeuvre.
    """

    def __init__(self, params_filename=None):
        """
        Creates an agent that performs a stern conversion against a target
        aircraft.

        A new StateAgent is initialised with the states in this module. The
        tactical parameters for each state may be set using a json file.

        Args:
            params_filename (string): optional json file containing tactical
              parameters to overwrite the default state parameters

        Returns:
            (StateAgent): stern conversion state agent
        """
        states = [EcuPureIntercept(), EcuFlyRelativeBearing(), EcuFlyingOffset(),
                  EcuConverting(), EcuMatchAltitude()]

        # # Pre-fill tactical parameters if json file is defined
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
                            initial=[EcuPureIntercept, EcuMatchAltitude])

    def update_states(self, tac_params):
        self.states.items()[0][1].PP2FR = tac_params[0]
        self.states.items()[0][1].PP2FO = tac_params[1]
        self.states.items()[0][1].PP2C = tac_params[2]
        self.states.items()[1][1].FR2PP = tac_params[3]
        self.states.items()[1][1].FR2FO = tac_params[4]
        self.states.items()[1][1].FR2C = tac_params[5]
        self.states.items()[2][1].FO2PP = tac_params[6]
        self.states.items()[2][1].FO2FR = tac_params[7]
        self.states.items()[2][1].FO2C = tac_params[8]
        self.states.items()[3][1].C2PP = tac_params[9]
        self.states.items()[3][1].C2FR = tac_params[10]
        self.states.items()[3][1].C2FO = tac_params[11]

class EcuMatchAltitude(MatchAltitude):
    """
    State that matches altitude with a threat aircraft.
    """
    def execute(self, t, dt):
        MatchAltitude.execute(self, t, dt)


class EcuPureIntercept(PureIntercept):
    """
    Default state for a stern conversion manoeuvre.

    This state intercepts a target by pointing the aircraft nose directly at it.
    During execution the relative bearing to the threat is calculated and
    commands are issued to turn the aircraft to fly toward it.

    If an enemy is detected that is aligned with the aircraft and is within the
    defined turn range, the state requests a transition to the
    FlyRelativeBearing state.
    """
    PP2FR = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    PP2FO = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    PP2C = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    #EcuFlyRelativeBearing, EcuFlyingOffset, EcuConverting

    is_param_one = False
    is_param_two = False
    is_param_three = False

    def on_entry(self):
        # ECU TESTING lbkelly 27/02/2017
        # print self.__class__.__name__
        self.__class__.__name__
        agent_states.statestring.append(self.__class__.__name__)

    def execute(self, t, dt):
        PureIntercept.execute(self, t, dt)

    def process_state(self, t, dt):
        StateAgent.process_state(self, t, dt)
        # print 'State: ', self.__class__.__name__, ' at time step: ', t

        if self.beliefs.threat_state:
            entity = self.beliefs.entity_state
            threat = self.beliefs.threat_state

            self.is_param_one = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PP2FR)
            self.is_param_two = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PP2FO)
            self.is_param_three = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PP2C)

            if self.is_param_one or self.is_param_two or self.is_param_three:
                self.transition_request = transition(self.is_param_one, self.is_param_two, self.is_param_three,
                                                 EcuFlyRelativeBearing, EcuFlyingOffset, EcuConverting)


class EcuFlyRelativeBearing(FlyRelativeBearing):
    """
    State to fly at a constant bearing relative to the threat aircraft.

    On entry to this state a command is issued to turn the aircraft a
    predetermined angle relative to the threat aircraft. When the turn has been
    completed the aircraft will continue to fly on this bearing to increase
    lateral separation, until the desired displacement has been achieved.

    If the desired displacement has been achieved the state requests a
    transition to the FlyingOffset state. If no threats are detected the state
    requests a transition back to the default state.
    """

    FR2PP = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    FR2FO = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    FR2C = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    # EcuPureIntercept, EcuFlyingOffset, EcuConverting

    is_param_one = False
    is_param_two = False
    is_param_three = False

    def on_entry(self):
        # ECU TESTING lbkelly 27/02/2017
        # print self.__class__.__name__
        self.__class__.__name__
        self._first_tick = True
        agent_states.statestring.append(self.__class__.__name__)

    def execute(self, t, dt):
        FlyRelativeBearing.execute(self, t, dt)

    def process_state(self, t, dt):
        StateAgent.process_state(self, t, dt)
        # print 'State: ', self.__class__.__name__, ' at time step: ', t

        if self.beliefs.threat_state:
            # Calculate the lateral distance to the threat aircraft
            entity = self.beliefs.entity_state
            threat = self.beliefs.threat_state

            self.is_param_one = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.FR2PP)
            self.is_param_two = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.FR2FO)
            self.is_param_three = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.FR2C)

            if self.is_param_one or self.is_param_two or self.is_param_three:
                self.transition_request = transition(self.is_param_one, self.is_param_two, self.is_param_three,
                                                 EcuPureIntercept, EcuFlyingOffset, EcuConverting)


class EcuFlyingOffset(FlyingOffset):
    """
    State to fly parallel to a threat aircraft to maintain constant separation.

    On entry to this state a command is issued to turn the aircraft to fly
    parallel to the flight path of the threat aircraft. When the turn has been
    completed the aircraft will continue to fly on this heading to maintain
    lateral separation, until the conversion point has been reached. Note that
    the state does not currently check whether the heading is still parallel to
    the threat flight path; if the threat changes heading the lateral separation
    will change.

    If the defined conversion point has been reached the state requests a
    transition to the Converting state. If no threats are detected the state
    requests a transition back to the default state.
    """

    FO2PP = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    FO2FR = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    FO2C = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    #EcuPureIntercept, EcuFlyRelativeBearing, EcuConverting

    is_param_one = False
    is_param_two = False
    is_param_three = False

    def on_entry(self):
        # ECU TESTING lbkelly 27/02/2017
        # print self.__class__.__name__
        self.__class__.__name__
        self._last_range = None
        agent_states.statestring.append(self.__class__.__name__)

    def execute(self, t, dt):
        FlyingOffset.execute(self, t, dt)

    def process_state(self, t, dt):
        StateAgent.process_state(self, t, dt)
        # print 'State: ', self.__class__.__name__, ' at time step: ', t

        if self.beliefs.threat_state:
            # Calculate the lateral distance to the threat aircraft
            entity = self.beliefs.entity_state
            threat = self.beliefs.threat_state

            self.is_param_one = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.FO2PP)
            self.is_param_two = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.FO2FR)
            self.is_param_three = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.FO2C)

            if self.is_param_one or self.is_param_two or self.is_param_three:
                self.transition_request = transition(self.is_param_one, self.is_param_two, self.is_param_three,
                                                 EcuPureIntercept, EcuFlyRelativeBearing, EcuConverting)


class EcuConverting(Converting):
    """
    State to turn aircraft to match a threat aircraft's heading to maintain a
    rear-hemisphere position.

    During execution commands are issued to turn the aircraft to match the
    threat aircraft heading. In the special case where the headings are exactly
    reciprocal, commands are initially issued to turn toward the threat aircraft
    itself to ensure that the turn is in the correct direction.

    If no threats are detected the state requests a transition back to the
    default state.
    """

    C2PP = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    C2FR = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    C2FO = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    #EcuPureIntercept, EcuFlyRelativeBearing, EcuFlyingOffset

    is_param_one = False
    is_param_two = False
    is_param_three = False

    def on_entry(self):
        # ECU TESTING lbkelly 27/02/2017
        # print self.__class__.__name__
        self.__class__.__name__
        agent_states.statestring.append(self.__class__.__name__)

    def execute(self, t, dt):
        Converting.execute(self, t, dt)

    def process_state(self, t, dt):
        StateAgent.process_state(self, t, dt)
        # print 'State: ', self.__class__.__name__, ' at time step: ', t

        if self.beliefs.threat_state:
            # Calculate the lateral distance to the threat aircraft
            entity = self.beliefs.entity_state
            threat = self.beliefs.threat_state

            self.is_param_one = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.C2PP)
            self.is_param_two = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.C2FR)
            self.is_param_three = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.C2FO)

            if self.is_param_one or self.is_param_two or self.is_param_three:
                self.transition_request = transition(self.is_param_one, self.is_param_two, self.is_param_three,
                                                    EcuPureIntercept, EcuFlyRelativeBearing, EcuFlyingOffset)
