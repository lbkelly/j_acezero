""" This module contains subclasses of StateAgent that pursue a target. These
agents have no substates and should be initialised directly. """

__author__ = 'lrbenke'


from state_agent import StateAgent
import utils
from commands import *
import utils as ut


class PurePursuitAgent(StateAgent):
    """
    Single-state agent that pursues a target by pointing the aircraft nose
    directly at it.

    During execution the relative bearing to the threat is calculated and a
    command is issued to turn the aircraft to fly toward it.
    """
    def execute(self, t, dt):
        StateAgent.execute(self, t, dt)

        if self.beliefs.threat_state:
            # Determine the bearing to the threat aircraft
            entity = self.beliefs.entity_state
            threat = self.beliefs.threat_state
            threat_bearing = utils.relative_bearing(entity.x, entity.y,
                    threat.x, threat.y)

            # Issue the change heading command
            if not ut.is_close(threat_bearing, entity.desired_heading):
                self.commands.append(SetHeadingGLoadCmd(psi_c=threat_bearing,
                                                        gload_c=5))
