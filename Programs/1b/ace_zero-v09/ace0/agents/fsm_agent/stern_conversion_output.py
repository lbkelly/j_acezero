""" This module contains subclasses of StateAgent that represent the discrete
states in a stern conversion operation. The class SternConversionAgent should be
initialised to generate a new stern conversion agent for execution. """
__author__ = 'lrbenke'

from state_agent import StateAgent
import utils as ut
from commands import *
import json
import agent_states

class SternConversionAgent(StateAgent):
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
        states = [PureIntercept(), FlyRelativeBearing(), FlyingOffset(),
                Converting(), MatchAltitude()]

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
                            initial=[PureIntercept, MatchAltitude])

    def update_states(self, tac_params):
        self.states.items()[0][1].TURN_RANGE = tac_params[0]
        self.states.items()[1][1].TURN_ANGLE = tac_params[1]
        self.states.items()[1][1].DESIRED_DISPLACEMENT = tac_params[2]
        self.states.items()[2][1].CONVERSION_RANGE = tac_params[3]
        self.states.items()[3][1].NO_CLOSER_RANGE = tac_params[4]

    def get_states(self):
        return self.states.items()[0][1].TURN_RANGE, self.states.items()[1][1].TURN_ANGLE, self.states.items()[1][1].DESIRED_DISPLACEMENT, self.states.items()[2][1].CONVERSION_RANGE, self.states.items()[3][1].NO_CLOSER_RANGE


class MatchAltitude(StateAgent):
    """
    State that matches altitude with a threat aircraft.
    """
    def execute(self, t, dt):
        StateAgent.execute(self, t, dt)

        # Check threat is detected
        if not self.beliefs.threat_state:
            return

        # Issue command to match threat altitude
        entity = self.beliefs.entity_state
        threat = self.beliefs.threat_state
        if not ut.is_close(threat.z, entity.z_c):
            self.commands.append(SetAltitudeCmd(threat.z, 7.0))


class PureIntercept(StateAgent):
    """
    Default state for a stern conversion manoeuvre.

    This state intercepts a target by pointing the aircraft nose directly at it.
    During execution the relative bearing to the threat is calculated and
    commands are issued to turn the aircraft to fly toward it.

    If an enemy is detected that is aligned with the aircraft and is within the
    defined turn range, the state requests a transition to the
    FlyRelativeBearing state.
    """
    MAX_ALIGNMENT_DIFF = 5.0  # maximum alignment angle difference to proceed
    TURN_RANGE = 999.0  # range to threat aircraft (NM)

    def on_entry(self):
        # ECU TESTING lbkelly 27/02/2017
        # print self.__class__.__name__
        agent_states.statestring.append("PureIntercept")
        self.__class__.__name__

    def execute(self, t, dt):
        StateAgent.execute(self, t, dt)

        # Check threat is detected
        if not self.beliefs.threat_state:
            return



        # Determine the bearing to the threat aircraft
        entity = self.beliefs.entity_state
        threat = self.beliefs.threat_state
        threat_bearing = ut.relative_bearing(entity.x, entity.y,
                threat.x, threat.y)

        # Issue command to turn toward threat
        if not ut.is_close(threat_bearing, entity.desired_heading):
            # self.commands.append(SetHeadingCmd(threat_bearing))
            # TODO: extract GLoad, calculate based on desired displacement
            self.commands.append(SetHeadingGLoadCmd(psi_c=threat_bearing,
                                                    gload_c=5))

    def process_state(self, t, dt):
        StateAgent.process_state(self, t, dt)

        if self.beliefs.threat_state:
            entity = self.beliefs.entity_state
            threat = self.beliefs.threat_state

            # Check whether threat is aligned with aircraft
            taa = ut.target_aspect_angle(entity.x, entity.y,
                    threat.x, threat.y, threat.heading)
            bearing_to_entity = ut.relative_bearing(threat.x, threat.y,
                    entity.x, entity.y)
            bearing_offset = abs(threat.heading - bearing_to_entity)
            if bearing_offset > self.MAX_ALIGNMENT_DIFF:
                # Threat not aligned so don't proceed to next state
                return

            # Check whether at turn range from threat
            distance = ut.distance(entity.pos_2d(), threat.pos_2d())
            if ut.metres_to_nautical_miles(distance) <= self.TURN_RANGE:
                self.transition_request = FlyRelativeBearing


class FlyRelativeBearing(StateAgent):
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
    TURN_ANGLE = 15.0  # relative bearing angle (deg)
    DESIRED_DISPLACEMENT = 5000  # lateral separation (ft), depends on turn rate

    def on_entry(self):
        # ECU TESTING lbkelly 27/02/2017
        # print self.__class__.__name__
        agent_states.statestring.append("FlyRelative")
        self.__class__.__name__
        self._first_tick = True

    def execute(self, t, dt):
        StateAgent.execute(self, t, dt)

        # Execute state behaviour only on first tick after entering state
        if self._first_tick:
            self._first_tick = False

            # Check threat is detected
            if not self.beliefs.threat_state:
                return

            # Calculate bearing from entity to threat and the reverse
            entity = self.beliefs.entity_state
            threat = self.beliefs.threat_state
            threat_bearing = ut.relative_bearing(entity.x, entity.y,
                    threat.x, threat.y)
            entity_bearing = ut.reciprocal_heading(threat_bearing)

            # Add or subtract the turn angle depending on whether we are
            # clockwise or counter-clockwise from the threat's heading, so that
            # we turn away from the threat not across it
            if ut.is_angle_ccw(threat.heading, entity_bearing):
                new_heading = threat_bearing + self.TURN_ANGLE
            else:
                new_heading = threat_bearing - self.TURN_ANGLE
            new_heading = ut.constrain_360(new_heading)

            # Issue the change heading command
            if not ut.is_close(new_heading, entity.desired_heading,
                    abs_tol=1.0):
                # self.commands.append(SetHeadingCmd(new_heading))
                # TODO: extract GLoad, calculate based on desired displacement
                self.commands.append(SetHeadingGLoadCmd(psi_c=new_heading, gload_c=5))

    def process_state(self, t, dt):
        StateAgent.process_state(self, t, dt)

        if self.beliefs.threat_state:
            # Calculate the lateral distance to the threat aircraft
            entity = self.beliefs.entity_state
            threat = self.beliefs.threat_state
            distance = ut.distance(entity.pos_2d(), threat.pos_2d())
            displacement = ut.lateral_displacement(entity.x, entity.y,
                    threat.x, threat.y, threat.heading, distance)
            displacement = ut.metres_to_feet(displacement)

            # Check whether the desired lateral separation has been reached
            if displacement >= self.DESIRED_DISPLACEMENT:
                self.transition_request = FlyingOffset

        else:
            # No threats detected so return to default state
            self.transition_request = PureIntercept


class FlyingOffset(StateAgent):
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
    CONVERSION_RANGE = 1.0  # range to threat aircraft at conversion point (NM)

    def on_entry(self):
        # ECU TESTING lbkelly 27/02/2017
        # print self.__class__.__name__
        agent_states.statestring.append("FlyingOffset")
        self.__class__.__name__
        self._last_range = None

    def execute(self, t, dt):
        StateAgent.execute(self, t, dt)

        # Check threat is detected
        if not self.beliefs.threat_state:
            return

        # Determine heading parallel to flight path of threat
        entity = self.beliefs.entity_state
        threat = self.beliefs.threat_state
        parallel_heading = ut.reciprocal_heading(threat.heading)

        # Issue the change heading command
        if not ut.is_close(parallel_heading, entity.desired_heading,
                abs_tol=1.0):
            # self.commands.append(SetHeadingCmd(parallel_heading))
            # TODO: extract GLoad, calculate based on desired displacement
            self.commands.append(SetHeadingGLoadCmd(psi_c=parallel_heading, gload_c=5))

    def process_state(self, t, dt):
        StateAgent.process_state(self, t, dt)

        if self.beliefs.threat_state:
            entity = self.beliefs.entity_state
            threat = self.beliefs.threat_state
            distance = ut.distance(entity.pos_2d(), threat.pos_2d())

            # Check whether the conversion point has been reached
            if ut.metres_to_nautical_miles(distance) <= self.CONVERSION_RANGE:
                self.transition_request = Converting

            # Check if still closing with threat
            if self._last_range:
                if distance > self._last_range:
                    # Not closing with threat so return to default state
                    self.transition_request = PureIntercept
            self._last_range = distance

        else:
            # No threats detected so return to default state
            self.transition_request = PureIntercept


class Converting(StateAgent):
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
    NO_CLOSER_RANGE = 2.0  # minimum range from threat to prevent overshoot (NM)

    def on_entry(self):
        # ECU TESTING lbkelly 27/02/2017
        # print self.__class__.__name__
        self.__class__.__name__
        agent_states.statestring.append("Converting")

    def execute(self, t, dt):
        StateAgent.execute(self, t, dt)

        # Check threat is detected
        if not self.beliefs.threat_state:
            return

        entity = self.beliefs.entity_state
        threat = self.beliefs.threat_state

        # Check if the threat heading is exactly reciprocal
        if ut.is_reciprocal(entity.heading, threat.heading):
            # Issue command to turn toward the threat aircraft
            threat_bearing = ut.relative_bearing(entity.x, entity.y,
                    threat.x, threat.y)
            if not ut.is_close(entity.desired_heading, threat_bearing,
                    abs_tol=1.0):
                # self.commands.append(SetHeadingCmd(threat_bearing))
                # TODO: extract GLoad, calculate based on desired displacement
                self.commands.append(SetHeadingGLoadCmd(psi_c=threat_bearing, gload_c=5))
        elif not ut.is_close(entity.desired_heading, threat.heading):
            # Issue command to turn to match the threat aircraft heading
            # self.commands.append(SetHeadingCmd(threat.heading))
            # TODO: extract GLoad, calculate based on desired displacement
            self.commands.append(SetHeadingGLoadCmd(psi_c=threat.heading, gload_c=5))

        # Adjust the entity speed to avoid overshooting
        if (entity.desired_v > threat.v and not
                ut.is_close(entity.desired_v, threat.v)):
            distance = ut.distance(entity.pos_2d(), threat.pos_2d())
            if ut.metres_to_nautical_miles(distance) <= \
                    self.NO_CLOSER_RANGE:
                # Issue command to match threat speed
                self.commands.append(SetSpeedCmd(threat.v))

    def process_state(self, t, dt):
        StateAgent.process_state(self, t, dt)

        if not self.beliefs.threat_state:
            # No threats detected so return to the default state
            self.transition_request = PureIntercept
