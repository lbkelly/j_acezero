""" Park ECU pure pursuit agent """
# based on the code written by 'lrbenke'
__author__ = 'lbkelly'

from state_agent import StateAgent
import helpers
import random
from commands import *
import json


def transition(bool_a, bool_b, bool_c, bool_d, bool_e, bool_f,
               state_a, state_b, state_c, state_d, state_e, state_f):
    states = [state_a, state_b, state_c, state_d, state_e, state_f]
    list_of_bools = [bool_a, bool_b, bool_c, bool_d, bool_e, bool_f]
    legal = []
    for i, bool_value in enumerate(list_of_bools):
        if bool_value:
            legal.append(states[i])
    return legal[random.randint(0, len(legal) - 1)]


class ParkEcuPure(StateAgent):
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
        states = [LeftDown(), LeftUp(), PullUp(), LevelFlight(), PushDown(), RightUp(), RightDown()]

        # Pre-fill tactical parameters if json file is defined
        if params_filename:
            with open(params_filename) as data_file:
                data = json.load(data_file)
                for state in states:
                    state_classname = state.__class__.__name__
                    if state_classname in data:
                        # Set parameters to the values defined in the json file
                        for param, value in data[state_classname].items():
                            setattr(state, param, value)

        StateAgent.__init__(self, states,
                            initial=[LeftDown])


class LeftDown(StateAgent):
    """
    Default state for a stern conversion manoeuvre.

    This state intercepts a target by pointing the aircraft nose directly at it.
    During execution the relative bearing to the threat is calculated and
    commands are issued to turn the aircraft to fly toward it.

    If an enemy is detected that is aligned with the aircraft and is within the
    defined turn range, the state requests a transition to the
    FlyRelativeBearing state.
    """
    THETA_C = -90.0
    PSI_C = 30.0

    LEFT_DOWN = [-100000, 100000, 0, 100000, -100000, 0, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100,
                 100, -100, 100]
    LEFT_UP = [-100000, 100000, 0, 100000, 1, 100000, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100, 100,
               -100, 100]
    PULL_UP = [-100000, 100000, 1, -1, 0, 100000, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100, 100,
               -100, 100]
    LEVEL_FLIGHT = [-5000, 5000, 1, -1, -0.5, 0.5, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100, 100,
                    -100, 100]
    PUSH_DOWN = [-100000, 100000, 1, -1, -100000, 0, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100, 100,
                 -100, 100]
    RIGHT_UP = [-100000, 100000, -100000, 0, 1, 100000, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100,
                100, -100, 100]
    RIGHT_DOWN = [-100000, 100000, -100000, 0, -100000, 0, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100,
                  100, -100, 100]

    is_left_up = False
    is_pull_up = False
    is_level_flight = False
    is_push_down = False
    is_right_up = False
    is_right_down = False

    def on_entry(self):
        # ECU TESTING lbkelly 27/02/2017
        print self.__class__.__name__
        self.__class__.__name__

    def execute(self, t, dt):
        StateAgent.execute(self, t, dt)
        self.commands.append(SetPitchAngleCmd(theta_c=self.THETA_C))
        self.commands.append(SetHeadingGLoadCmd(psi_c=self.PSI_C + self.beliefs.entity_state.psi, gload_c=5))

    def process_state(self, t, dt):
        StateAgent.process_state(self, t, dt)
        # Calculate the lateral distance to the threat aircraft
        entity = self.beliefs.entity_state
        threat = self.beliefs.threat_state

        self.is_left_up = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.LEFT_UP)
        self.is_pull_up = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PULL_UP)
        self.is_level_flight = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.LEVEL_FLIGHT)
        self.is_push_down = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PUSH_DOWN)
        self.is_right_up = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.RIGHT_UP)
        self.is_right_down = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.RIGHT_DOWN)

        if self.is_left_up or self.is_pull_up or self.is_level_flight or self.is_push_down or self.is_right_up or self.is_right_down:
            self.transition_request = transition(self.is_left_up, self.is_pull_up, self.is_level_flight,
                                                 self.is_push_down, self.is_right_up, self.is_right_down,
                                                 LeftUp, PullUp, LevelFlight, PushDown, RightUp, RightDown)


class LeftUp(StateAgent):
    """
    Default state for a stern conversion manoeuvre.

    This state intercepts a target by pointing the aircraft nose directly at it.
    During execution the relative bearing to the threat is calculated and
    commands are issued to turn the aircraft to fly toward it.

    If an enemy is detected that is aligned with the aircraft and is within the
    defined turn range, the state requests a transition to the
    FlyRelativeBearing state.
    """
    THETA_C = 90.0
    PSI_C = 30.0

    LEFT_DOWN = [-100000, 100000, 0, 100000, -100000, 0, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100,
                 100, -100, 100]
    LEFT_UP = [-100000, 100000, 0, 100000, 1, 100000, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100, 100,
               -100, 100]
    PULL_UP = [-100000, 100000, 1, -1, 0, 100000, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100, 100,
               -100, 100]
    LEVEL_FLIGHT = [-5000, 5000, 1, -1, -0.5, 0.5, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100, 100,
                    -100, 100]
    PUSH_DOWN = [-100000, 100000, 1, -1, -100000, 0, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100, 100,
                 -100, 100]
    RIGHT_UP = [-100000, 100000, -100000, 0, 1, 100000, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100,
                100, -100, 100]
    RIGHT_DOWN = [-100000, 100000, -100000, 0, -100000, 0, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100,
                  100, -100, 100]

    is_left_down = False
    is_pull_up = False
    is_level_flight = False
    is_push_down = False
    is_right_up = False
    is_right_down = False

    def on_entry(self):
        # ECU TESTING lbkelly 27/02/2017
        print self.__class__.__name__
        self.__class__.__name__

    def execute(self, t, dt):
        StateAgent.execute(self, t, dt)
        self.commands.append(SetPitchAngleCmd(theta_c=self.THETA_C))
        self.commands.append(SetHeadingGLoadCmd(psi_c=self.PSI_C + self.beliefs.entity_state.psi, gload_c=5))

    def process_state(self, t, dt):
        StateAgent.process_state(self, t, dt)
        # Calculate the lateral distance to the threat aircraft
        entity = self.beliefs.entity_state
        threat = self.beliefs.threat_state

        self.is_left_down = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.LEFT_DOWN)
        self.is_pull_up = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PULL_UP)
        self.is_level_flight = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.LEVEL_FLIGHT)
        self.is_push_down = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PUSH_DOWN)
        self.is_right_up = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.RIGHT_UP)
        self.is_right_down = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.RIGHT_DOWN)

        if self.is_left_down or self.is_pull_up or self.is_level_flight or self.is_push_down or self.is_right_up or self.is_right_down:
            self.transition_request = transition(self.is_left_down, self.is_pull_up, self.is_level_flight,
                                                 self.is_push_down, self.is_right_up, self.is_right_down,
                                                 LeftDown, PullUp, LevelFlight, PushDown, RightUp, RightDown)


class PullUp(StateAgent):
    """
    Default state for a stern conversion manoeuvre.

    This state intercepts a target by pointing the aircraft nose directly at it.
    During execution the relative bearing to the threat is calculated and
    commands are issued to turn the aircraft to fly toward it.

    If an enemy is detected that is aligned with the aircraft and is within the
    defined turn range, the state requests a transition to the
    FlyRelativeBearing state.
    """
    THETA_C = 90.0

    LEFT_DOWN = [-100000, 100000, 0, 100000, -100000, 0, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100,
                 100, -100, 100]
    LEFT_UP = [-100000, 100000, 0, 100000, 1, 100000, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100, 100,
               -100, 100]
    PULL_UP = [-100000, 100000, 1, -1, 0, 100000, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100, 100,
               -100, 100]
    LEVEL_FLIGHT = [-5000, 5000, 1, -1, -0.5, 0.5, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100, 100,
                    -100, 100]
    PUSH_DOWN = [-100000, 100000, 1, -1, -100000, 0, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100, 100,
                 -100, 100]
    RIGHT_UP = [-100000, 100000, -100000, 0, 1, 100000, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100,
                100, -100, 100]
    RIGHT_DOWN = [-100000, 100000, -100000, 0, -100000, 0, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100,
                  100, -100, 100]

    is_left_down = False
    is_left_up = False
    is_level_flight = False
    is_push_down = False
    is_right_up = False
    is_right_down = False

    def on_entry(self):
        # ECU TESTING lbkelly 27/02/2017
        print self.__class__.__name__
        self.__class__.__name__

    def execute(self, t, dt):
        StateAgent.execute(self, t, dt)
        self.commands.append(SetPitchAngleCmd(theta_c=self.THETA_C))

    def process_state(self, t, dt):
        StateAgent.process_state(self, t, dt)
        # Calculate the lateral distance to the threat aircraft
        entity = self.beliefs.entity_state
        threat = self.beliefs.threat_state

        self.is_left_down = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.LEFT_DOWN)
        self.is_left_up = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.LEFT_UP)
        self.is_level_flight = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.LEVEL_FLIGHT)
        self.is_push_down = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PUSH_DOWN)
        self.is_right_up = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.RIGHT_UP)
        self.is_right_down = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.RIGHT_DOWN)

        if self.is_left_down or self.is_left_up or self.is_level_flight or self.is_push_down or self.is_right_up or self.is_right_down:
            self.transition_request = transition(self.is_left_down, self.is_left_up, self.is_level_flight,
                                                 self.is_push_down, self.is_right_up, self.is_right_down,
                                                 LeftDown, LeftUp, LevelFlight, PushDown, RightUp, RightDown)


class LevelFlight(StateAgent):
    """
    Default state for a stern conversion manoeuvre.

    This state intercepts a target by pointing the aircraft nose directly at it.
    During execution the relative bearing to the threat is calculated and
    commands are issued to turn the aircraft to fly toward it.

    If an enemy is detected that is aligned with the aircraft and is within the
    defined turn range, the state requests a transition to the
    FlyRelativeBearing state.
    """

    LEFT_DOWN = [-100000, 100000, 0, 100000, -100000, 0, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100,
                 100, -100, 100]
    LEFT_UP = [-100000, 100000, 0, 100000, 1, 100000, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100, 100,
               -100, 100]
    PULL_UP = [-100000, 100000, 1, -1, 0, 100000, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100, 100,
               -100, 100]
    LEVEL_FLIGHT = [-5000, 5000, 1, -1, -0.5, 0.5, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100, 100,
                    -100, 100]
    PUSH_DOWN = [-100000, 100000, 1, -1, -100000, 0, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100, 100,
                 -100, 100]
    RIGHT_UP = [-100000, 100000, -100000, 0, 1, 100000, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100,
                100, -100, 100]
    RIGHT_DOWN = [-100000, 100000, -100000, 0, -100000, 0, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100,
                  100, -100, 100]

    is_left_down = False
    is_left_up = False
    is_pull_up = False
    is_push_down = False
    is_right_up = False
    is_right_down = False

    def on_entry(self):
        # ECU TESTING lbkelly 27/02/2017
        print self.__class__.__name__
        self.__class__.__name__

    def execute(self, t, dt):
        StateAgent.execute(self, t, dt)
        self.commands.append(SetFlyLevelCmd())

    def process_state(self, t, dt):
        StateAgent.process_state(self, t, dt)
        # Calculate the lateral distance to the threat aircraft
        entity = self.beliefs.entity_state
        threat = self.beliefs.threat_state

        self.is_left_down = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.LEFT_DOWN)
        self.is_left_up = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.LEFT_UP)
        self.is_pull_up = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PULL_UP)
        self.is_push_down = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PUSH_DOWN)
        self.is_right_up = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.RIGHT_UP)
        self.is_right_down = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.RIGHT_DOWN)

        if self.is_left_down or self.is_left_up or self.is_pull_up or self.is_push_down or self.is_right_up or self.is_right_down:
            self.transition_request = transition(self.is_left_down, self.is_left_up, self.is_pull_up,
                                                 self.is_push_down, self.is_right_up, self.is_right_down,
                                                 LeftDown, LeftUp, PullUp, PushDown, RightUp, RightDown)


class PushDown(StateAgent):
    """
    Default state for a stern conversion manoeuvre.

    This state intercepts a target by pointing the aircraft nose directly at it.
    During execution the relative bearing to the threat is calculated and
    commands are issued to turn the aircraft to fly toward it.

    If an enemy is detected that is aligned with the aircraft and is within the
    defined turn range, the state requests a transition to the
    FlyRelativeBearing state.
    """
    THETA_C = -90.0

    LEFT_DOWN = [-100000, 100000, 0, 100000, -100000, 0, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100,
                 100, -100, 100]
    LEFT_UP = [-100000, 100000, 0, 100000, 1, 100000, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100, 100,
               -100, 100]
    PULL_UP = [-100000, 100000, 1, -1, 0, 100000, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100, 100,
               -100, 100]
    LEVEL_FLIGHT = [-5000, 5000, 1, -1, -0.5, 0.5, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100, 100,
                    -100, 100]
    PUSH_DOWN = [-100000, 100000, 1, -1, -100000, 0, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100, 100,
                 -100, 100]
    RIGHT_UP = [-100000, 100000, -100000, 0, 1, 100000, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100,
                100, -100, 100]
    RIGHT_DOWN = [-100000, 100000, -100000, 0, -100000, 0, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100,
                  100, -100, 100]

    is_left_down = False
    is_left_up = False
    is_pull_up = False
    is_level_flight = False
    is_right_up = False
    is_right_down = False

    def on_entry(self):
        # ECU TESTING lbkelly 27/02/2017
        print self.__class__.__name__
        self.__class__.__name__

    def execute(self, t, dt):
        StateAgent.execute(self, t, dt)
        self.commands.append(SetPitchAngleCmd(theta_c=self.THETA_C))

    def process_state(self, t, dt):
        StateAgent.process_state(self, t, dt)
        # Calculate the lateral distance to the threat aircraft
        entity = self.beliefs.entity_state
        threat = self.beliefs.threat_state

        self.is_left_down = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.LEFT_DOWN)
        self.is_left_up = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.LEFT_UP)
        self.is_pull_up = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PULL_UP)
        self.is_level_flight = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.LEVEL_FLIGHT)
        self.is_right_up = helpers.transition_conditionhelpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.RIGHT_UP)
        self.is_right_down = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.RIGHT_DOWN)

        if self.is_left_down or self.is_left_up or self.is_pull_up or self.is_level_flight or self.is_right_up or self.is_right_down:
            self.transition_request = transition(self.is_left_down, self.is_left_up, self.is_pull_up,
                                                 self.is_level_flight, self.is_right_up, self.is_right_down,
                                                 LeftDown, LeftUp, PullUp, LevelFlight, RightUp, RightDown)


class RightUp(StateAgent):
    """
    Default state for a stern conversion manoeuvre.

    This state intercepts a target by pointing the aircraft nose directly at it.
    During execution the relative bearing to the threat is calculated and
    commands are issued to turn the aircraft to fly toward it.

    If an enemy is detected that is aligned with the aircraft and is within the
    defined turn range, the state requests a transition to the
    FlyRelativeBearing state.
    """
    THETA_C = 90.0
    PSI_C = -30.0

    LEFT_DOWN = [-100000, 100000, 0, 100000, -100000, 0, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100,
                 100, -100, 100]
    LEFT_UP = [-100000, 100000, 0, 100000, 1, 100000, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100, 100,
               -100, 100]
    PULL_UP = [-100000, 100000, 1, -1, 0, 100000, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100, 100,
               -100, 100]
    LEVEL_FLIGHT = [-5000, 5000, 1, -1, -0.5, 0.5, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100, 100,
                    -100, 100]
    PUSH_DOWN = [-100000, 100000, 1, -1, -100000, 0, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100, 100,
                 -100, 100]
    RIGHT_UP = [-100000, 100000, -100000, 0, 1, 100000, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100,
                100, -100, 100]
    RIGHT_DOWN = [-100000, 100000, -100000, 0, -100000, 0, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100,
                  100, -100, 100]

    is_left_down = False
    is_left_up = False
    is_pull_up = False
    is_level_flight = False
    is_push_down = False
    is_right_down = False

    def on_entry(self):
        # ECU TESTING lbkelly 27/02/2017
        print self.__class__.__name__
        self.__class__.__name__

    def execute(self, t, dt):
        StateAgent.execute(self, t, dt)
        self.commands.append(SetPitchAngleCmd(theta_c=self.THETA_C))
        self.commands.append(SetHeadingGLoadCmd(psi_c=self.PSI_C + self.beliefs.entity_state.psi, gload_c=5))

    def process_state(self, t, dt):
        StateAgent.process_state(self, t, dt)
        # Calculate the lateral distance to the threat aircraft
        entity = self.beliefs.entity_state
        threat = self.beliefs.threat_state

        self.is_left_down = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.LEFT_DOWN)
        self.is_left_up = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.LEFT_UP)
        self.is_pull_up = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PULL_UP)
        self.is_level_flight = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.LEVEL_FLIGHT)
        self.is_push_down = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PUSH_DOWN)
        self.is_right_down = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.RIGHT_DOWN)

        if self.is_left_down or self.is_left_up or self.is_pull_up or self.is_level_flight or self.is_push_down or self.is_right_down:
            self.transition_request = transition(self.is_left_down, self.is_left_up, self.is_pull_up,
                                                 self.is_level_flight, self.is_push_down, self.is_right_down,
                                                 LeftDown, LeftUp, PullUp, LevelFlight, PushDown, RightDown)


class RightDown(StateAgent):
    """
    Default state for a stern conversion manoeuvre.

    This state intercepts a target by pointing the aircraft nose directly at it.
    During execution the relative bearing to the threat is calculated and
    commands are issued to turn the aircraft to fly toward it.

    If an enemy is detected that is aligned with the aircraft and is within the
    defined turn range, the state requests a transition to the
    FlyRelativeBearing state.
    """
    THETA_C = -90.0
    PSI_C = -30.0

    LEFT_DOWN = [-100000, 100000, 0, 100000, -100000, 0, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100,
                 100, -100, 100]
    LEFT_UP = [-100000, 100000, 0, 100000, 1, 100000, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100, 100,
               -100, 100]
    PULL_UP = [-100000, 100000, 1, -1, 0, 100000, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100, 100,
               -100, 100]
    LEVEL_FLIGHT = [-5000, 5000, 1, -1, -0.5, 0.5, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100, 100,
                    -100, 100]
    PUSH_DOWN = [-100000, 100000, 1, -1, -100000, 0, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100, 100,
                 -100, 100]
    RIGHT_UP = [-100000, 100000, -100000, 0, 1, 100000, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100,
                100, -100, 100]
    RIGHT_DOWN = [-100000, 100000, -100000, 0, -100000, 0, -1000, 1000, -1000, 1000, -1000, 1000, -100, 100, -100,
                  100, -100, 100]

    is_left_down = False
    is_left_up = False
    is_pull_up = False
    is_level_flight = False
    is_push_down = False
    is_right_up = False

    def on_entry(self):
        # ECU TESTING lbkelly 27/02/2017
        print self.__class__.__name__
        self.__class__.__name__

    def execute(self, t, dt):
        StateAgent.execute(self, t, dt)
        self.commands.append(SetPitchAngleCmd(theta_c=self.THETA_C))
        self.commands.append(SetHeadingGLoadCmd(psi_c=self.PSI_C + self.beliefs.entity_state.psi, gload_c=5))

    def process_state(self, t, dt):
        StateAgent.process_state(self, t, dt)
        # Calculate the lateral distance to the threat aircraft
        entity = self.beliefs.entity_state
        threat = self.beliefs.threat_state

        self.is_left_down = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.LEFT_DOWN)
        self.is_left_up = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.LEFT_UP)
        self.is_pull_up = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PULL_UP)
        self.is_level_flight = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.LEVEL_FLIGHT)
        self.is_push_down = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.PUSH_DOWN)
        self.is_right_up = helpers.transition_condition(entity.tactical_3d(), threat.tactical_3d(), self.RIGHT_UP)

        if self.is_left_down or self.is_left_up or self.is_pull_up or self.is_level_flight or self.is_push_down or self.is_right_up:
            self.transition_request = transition(self.is_left_down, self.is_left_up, self.is_pull_up,
                                                 self.is_level_flight, self.is_push_down, self.is_right_up,
                                                 LeftDown, LeftUp, PullUp, LevelFlight, PushDown, RightUp)
