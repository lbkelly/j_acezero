"""
Pilot Module

Although this works, currently is incomplete:

TODO:
- Need to implement plans for all the commands we can issue
- Need to add some higher level plans
- Need to populate the PilotBeliefs class
- Need to update the current plans so that the goals aren't achieved as soon
  a command/action is issued.
"""

__author__ = 'mikepsn'

import json
from collections import deque

import commands as cmds
import utils
from agents.agent import Agent


class PilotBeliefs(object):
    """ A class capturing the pilot agent's beliefs.
    TODO: we need to populate this with the pilots beliefs.
    """
    def __init__(self, entity_state=None, threat_state=None):
        self.entity_state = entity_state
        self.threat_state = threat_state

    def update(self, entity_state, threat_state):
        self.entity_state = entity_state
        self.threat_state = threat_state


class Plan(object):
    """ Base class for an agent plan. """
    def __init__(self, agent, plan_name):
        self.agent = agent
        self.plan_name = plan_name
        self.achieved = False

    def tick(self, t, dt):
        pass


class SetSpeed(Plan):
    """ A plan to change the desired speed of the aircraft. """
    def __init__(self, agent, speed):
        plan_name = 'set_speed(%d)' % (speed)
        Plan.__init__(self, agent, plan_name)
        self.speed = speed
    
    def tick(self, t, dt):
        if not self.achieved:
            set_speed_cmd = cmds.SetSpeedCmd(self.speed)
            self.agent.add_action(set_speed_cmd)
            self.achieved = True


class FlyHeading(Plan):
    """ A plan to fly to the specified heading. """
    def __init__(self, agent, heading):
        plan_name = 'fly_heading(%d)' % (heading)
        Plan.__init__(self, agent, plan_name)
        self.heading = heading

    def tick(self, t, dt):
        if not self.achieved:
            fly_heading_cmd = cmds.SetHeadingCmd(self.heading)
            self.agent.add_action(fly_heading_cmd)
            self.achieved = True

class FlyHeadingGLoad(Plan):
    """ A plan to fly to the specified heading under a particular g-load factor. """
    def __init__(self, agent, heading, gload):
        plan_name = 'fly_heading_gload(%d, %f)' % (heading, gload)
        Plan.__init__(self, agent, plan_name)
        self.heading = heading
        self.gload = gload

    def tick(self, t, dt):
        if not self.achieved:
            fly_heading_gload_cmd = cmds.SetHeadingGLoadCmd(self.heading, self.gload)
            self.agent.add_action(fly_heading_gload_cmd)
            self.achieved = True


class FlyAltitude(Plan):
    """ A plan to fly to the specified altitude. """
    def __init__(self, agent, z_c, theta_c):
        plan_name = 'fly_altitude(%d, %d)' % (z_c, theta_c)
        Plan.__init__(self, agent, plan_name)
        self.z_c = z_c
        self.theta_c = theta_c

    def tick(self, t, dt):
        if not self.achieved:
            fly_altitude_cmd = cmds.SetAltitudeCmd(self.z_c, self.theta_c)
            self.agent.add_action(fly_altitude_cmd)
            self.achieved = True

class FlyPitchAngle(Plan):
    """ A plan to fly to the specified altitude. """
    def __init__(self, agent, theta_c):
        plan_name = 'fly_pitch_angle(%d)' % (theta_c)
        Plan.__init__(self, agent, plan_name)
        self.theta_c = theta_c

    def tick(self, t, dt):
        if not self.achieved:
            fly_pitch_angle_cmd = cmds.SetPitchAngleCmd(self.theta_c)
            self.agent.add_action(fly_pitch_angle_cmd)
            self.achieved = True


class WaitFor(Plan):
    """ A plan to make the agent wait for specified number of seconds. """
    def __init__(self, agent, wait_time_seconds):
        plan_name = 'wait_for(%3.1f)' % (wait_time_seconds)
        Plan.__init__(self, agent, plan_name)
        self.wait_time = wait_time_seconds
        self.elapsed_time = 0.0

    def tick(self, t, dt):
        if not self.achieved:
            if self.elapsed_time <= self.wait_time:
                self.elapsed_time += dt
            else:
                self.achieved = True



class PilotAgent(Agent):
    """
    A class representing the pilot agent decision making.
    Each pilot has a name, a set of beliefs, a current goal, a list of current
    actions to send to the environment and a current missions (which is a queue
    of commands/actions)
    """
    def __init__(self, params_filename):
        self.beliefs = PilotBeliefs()
        self.goal = None
        self.actions = []
        self.mission = deque()

        # TODO: Remove once missions have been extracted to json files
        # Load the fighter name from the agent parameters file
        with open(params_filename) as params_file:
            data = json.load(params_file)
            self.name = data['name']
        # Add the predefined mission for the fighter name
        if self.name == "viper":
            self.add_mission(self.viper_mission())
        elif self.name == "cobra":
            self.add_mission(self.cobra_mission())

    def viper_mission(self):
        """
        Creates a mission profile for viper pilot.
        The mission profile is a list of commands that the pilot
        should execute. It includes time delays between commands.
        Note that here we've hard code the mission into the code.
        The long term plan is to pull this out somehow into a data
        file (most likely a .json representation).
        """
        viper_mission = [
            SetSpeed(self, utils.knots_to_mps(400)),
            WaitFor(self, 10.0),
            FlyHeadingGLoad(self, 160.0, 3.5),
            WaitFor(self, 10.0),
            FlyPitchAngle(self, 4.0),
            WaitFor(self, 20.0),
            FlyHeadingGLoad(self, 30.0, 3.0),
            WaitFor(self, 20.0),
            FlyHeadingGLoad(self, 150.0, 5.0),
            WaitFor(self, 20.0),
            FlyHeadingGLoad(self, 45.0, 2.0),
            FlyPitchAngle(self, -5.0),
            WaitFor(self, 20.0),
            FlyHeadingGLoad(self, 290.0, 4.0),
            WaitFor(self, 40.0),
            FlyPitchAngle(self, 0.0),
            FlyHeadingGLoad(self, 23.0, 6.0),
            WaitFor(self, 30.0),
            FlyHeadingGLoad(self, 10.0, 2.5)
        ]
        return viper_mission

    def cobra_mission(self):
        """
        Creates a mission profile for cobra pilot.
        The mission profile is a list of commands that the pilot
        should execute. It includes time delays between commands.
        Note that here we've hard code the mission into the code.
        The long term plan is to pull this out somehow into a data
        file (most likely a .json representation).
        """
        cobra_mission = [
            SetSpeed(self, utils.knots_to_mps(300)),
            FlyPitchAngle(self, 70.0),
            WaitFor(self, 20.0),
            FlyHeadingGLoad(self, 75.0, 7.0),
            WaitFor(self, 20.0),
            FlyHeadingGLoad(self, 225.0, 3.0),
            WaitFor(self, 30.0),
            FlyPitchAngle(self, 0.0),
            WaitFor(self, 30.0),
            FlyHeadingGLoad(self, 100.0, 5.0),
            WaitFor(self, 10.0),
            FlyHeadingGLoad(self, 190.0, 2.0),
            WaitFor(self, 20.0),
            FlyHeadingGLoad(self, 300.0, 3.0),
            FlyPitchAngle(self, 20.0),
            WaitFor(self, 10.0),
            FlyPitchAngle(self, 10.0),
            WaitFor(self, 10.0),
            FlyHeadingGLoad(self, 33.0, 5.0),
            WaitFor(self, 20.0),
            FlyHeadingGLoad(self, 70.0, 4.0),
            WaitFor(self, 20.0),
            FlyHeadingGLoad(self, 120.0, 5.0),
            WaitFor(self, 60.0),
            FlyHeadingGLoad(self, 300, 3.0)
        ]
        cobra2_mission = [
            FlyHeadingGLoad(self, 90.0, 3.0),
            WaitFor(self, 30.0),
            FlyHeadingGLoad(self, 180.0, 3.0),
            WaitFor(self, 30.0),
            FlyHeadingGLoad(self, 270.0, 3.0),
            WaitFor(self, 30.0),
            FlyHeadingGLoad(self, 0.0, 3.0),
            WaitFor(self, 30.0),
            FlyHeadingGLoad(self, 90.0, 3.0),
            WaitFor(self, 30.0),
            FlyHeadingGLoad(self, 180.0, 3.0),
            WaitFor(self, 30.0),
            FlyHeadingGLoad(self, 1.0, 5.0)
        ]
        return cobra2_mission

    def update_beliefs(self, my_state, adversary_state):
        """ Updates the pilot's beliefs about it's own and adversary state """
        self.beliefs.update(my_state, adversary_state)

    def set_beliefs(self, beliefs):
        self.beliefs = beliefs

    def tick(self, t, dt):
        """
        Ticks the agent every time step.
        Clears the previous set of actions.
        If we don't have a goal or we have achieved the current goal and
        we still have stuff to do in our mission, get a new goal.
        Otherwise just tick the current goal.
        """
        self.actions = []
        if (not self.goal or self.goal.achieved) and len(self.mission) > 0:
            self.goal = self.mission.popleft()
        if self.goal:
            if not self.goal.achieved:
                self.goal.tick(t, dt)

    def add_mission(self, mission):
        """ Add a new mission. """
        self.mission = deque(mission)

    def add_action(self, action):
        """ Append action to the action list. """
        self.actions.append(action)

    def get_actions(self):
        """ Returns the current set of actions. """
        return self.actions

    def get_commands(self):
        """ Returns the current set of actions. Commands is a pseudonym for actions. """
        return self.get_actions()


if __name__ == '__main__':

    viper = PilotAgent('viper')

    mission = [
        WaitFor(viper, 1.0),
        FlyHeading(viper, 150.0),
        WaitFor(viper, 1.0),
        FlyHeading(viper, 45.0)
    ]

    viper.add_mission(mission)

    t, dt = 0.0, 0.1
    while t < 10.0:
        viper.tick(t, dt)
        print t, viper.goal.plan_name, viper.goal.achieved
        t += dt
