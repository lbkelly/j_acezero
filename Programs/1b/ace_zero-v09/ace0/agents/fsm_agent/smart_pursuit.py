""" This module contains subclasses of StateAgent that represent the discrete
states in a pursuit operation. The class SmartPursuitAgent should be
initialised to generate a new agent for execution. """

__author__ = 'lrbenke'


from state_agent import StateAgent
import utils
from commands import *
import utils as ut


class SmartPursuitAgent(StateAgent):
    """
    This class represents an agent that pursues a threat aircraft by flying
    directly toward it.

    During execution the agent will adjust heading and altitude to point the
    aircraft nose directly at the threat aircraft. If the threat aircraft is
    within sensor range the aircraft velocity is reduced to avoid overshooting.
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
        states = [PureIntercept(), MatchAltitude(), MatchSpeed()]
        StateAgent.__init__(self, states,
                initial=[PureIntercept, MatchAltitude, MatchSpeed])


class PureIntercept(StateAgent):
    """
    This state intercepts a target by pointing the aircraft nose directly at it.
    During execution the relative bearing to the threat is calculated and
    commands are issued to turn the aircraft to fly toward it.
    """
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
            self.commands.append(SetHeadingGLoadCmd(psi_c=threat_bearing,
                                                    gload_c=10))


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


class MatchSpeed(StateAgent):
    """
    State that matches speed with a threat aircraft if it is within sensor
    range, to avoid overshooting.
    """
    def execute(self, t, dt):
        StateAgent.execute(self, t, dt)

        # Check threat is detected
        if not self.beliefs.threat_state:
            return

        # Check whether we are within sensor range
        entity = self.beliefs.entity_state
        threat = self.beliefs.threat_state
        distance = ut.distance(entity.pos_2d(), threat.pos_2d())
        sensor_max = self.beliefs.entity_state.sensor_state.max_range
        if distance < sensor_max:
            if not ut.is_close(entity.desired_v, threat.v):
                # Issue command to match threat speed
                self.commands.append(SetSpeedCmd(threat.v))
