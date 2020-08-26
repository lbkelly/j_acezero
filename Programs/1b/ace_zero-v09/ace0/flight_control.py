"""
Flight Control Model

The flight control model is the pilot's interface to the aircraft platform
dynamics model. The flight control contains a platform model and can
process three types/families of commands.

These are speed commands, altitude commands and direction commands.
While in a real aircraft speed, altitude and direction are coupled through
the equations of motion, in this model the aircraft is somewhat 'arcadey'.

We've decoupled the three types of controls allowing the pilot agent to set
three independent command channels. Note that there are still some restrictions.
The pilot cannot send two type of altitude commands at any given time step.

The pilot can control the aircraft speed, altitude and direction independently.
The tick method for the flight control class reflects this independence.
"""

__author__ = 'mikepsn, lrbenke'


import numpy as np
import utils as ut
from states import FighterState


class FlightControl(object):
    """
    The flight control system is the pilot agent's interface to the aircraft
    platform dynamics model. The class has a number of instance variables.
    - platform model
    - the current speed command
    - the current altitude command
    - the current direction command
    The class also contains three dictionaries that map the commands
    that are sent from the pilot into various methods which process
    these commands and intepret them for the platform dynamics model.
    """
    def __init__(self, platform):
        self.platform = platform
        self.speed_cmd = None
        self.altitude_cmd = None
        self.direction_cmd = None

            # dict mapping speed commands
        self.speed_commands = {
            'SetSpeedCmd' : self.process_set_speed_cmd
        }

            # dict mapping altitude commands
        self.altitude_commands = {
            'SetFlyLevelCmd' : self.process_set_fly_level_cmd,
            'SetPitchAngleCmd' : self.process_set_pitch_angle_cmd,
            'SetAltitudeCmd' : self.process_set_altitude_cmd
        }

            # dict mapping direction commands
        self.direction_commands = {
            'SetHeadingCmd' : self.process_set_heading_cmd,
            'SetHeadingGLoadCmd' : self.process_set_heading_gload_cmd,
            'SetWaypointCmd' : self.process_set_waypoint_cmd
        }

    def get_platform_state(self):
        """ Returns a FighterState object with the state of the underlying
        platform model, including position, orientation and speed. """
        p = self.platform
        return FighterState(p.x, p.y, p.z, p.vx, p.vy, p.vz, p.ax, p.ay, p.az, p.z_c, p.psi, p.psi_c, p.theta, p.theta_c,
                p.phi, p.phi_c, p.v, p.v_c, p.gload)

    def tick(self, t, dt):
        """
        Ticks the flight control system every time step.
        Controls the speed, altitude and direction before ticking
        the underlying platform model.
        """
        self.control_speed(t, dt)
        self.control_altitude(t, dt)
        self.control_direction(t, dt)
        self.platform.tick(t, dt)

    def set_new_commands(self, commands):
        """
        Processes new incoming commands according to the their cmd type.
        Note if there is more than one command for a given category,
        it will get over written by the last command in that category.
        """
        for cmd in commands:
            cmd_name = type(cmd).__name__
            if cmd_name in self.speed_commands:
                self.set_speed_cmd(cmd)
            if cmd_name in self.altitude_commands:
                self.set_altitude_cmd(cmd)
            if cmd_name in self.direction_commands:
                self.set_direction_cmd(cmd)

    def set_speed_cmd(self, cmd):
        """ Sets the current speed command to cmd """
        self.speed_cmd = cmd

    def set_altitude_cmd(self, cmd):
        """ Sets the current altitude command to cmd """
        self.altitude_cmd = cmd

    def set_direction_cmd(self, cmd):
        """ Sets the current direction command to cmd """
        self.direction_cmd = cmd

    def control_speed(self, t, dt):
        """ If there is a speed command indexes into the speed
        command dict and calls the relevant processing method. """
        if self.speed_cmd != None:
            cmd_name = type(self.speed_cmd).__name__
            self.speed_commands[cmd_name](t, dt)

    def control_altitude(self, t, dt):
        """ If there is an altitude command indexes into the altitude
        command dict and calls the relevant processing method. """
        if self.altitude_cmd != None:
            cmd_name = type(self.altitude_cmd).__name__
            self.altitude_commands[cmd_name](t, dt)

    def control_direction(self, t, dt):
        """ If there is a direction command indexes into the direction
        command dict and calls the relevant processing method. """
        if self.direction_cmd != None:
            cmd_name = type(self.direction_cmd).__name__
            self.direction_commands[cmd_name](t, dt)

    def process_set_fly_level_cmd(self, t, dt):
        """ Processes a fly level command. This sets the desirec
        pitch and roll angles to zero. Basically levels out the
        wings of the aircraft. Originally we were setting the desired
        yaw (psi) angle to zero as well. However this has the potential
        to screw things up as it will change the direction the aircraft
        is flying in. This is an undesired side-effect. Therefore better
        to just fly straight and level. Pitch level and roll level.
        I've left it commented it to make it obvious.
        """
        assert(type(self.altitude_cmd).__name__ == 'SetFlyLevelCmd')
        #self.platform.yaw_cmd(0.0)
        self.platform.pitch_cmd(0.0)
        self.platform.roll_cmd(0.0)

    def process_set_pitch_angle_cmd(self, t, dt):
        """ Processes the pitch angel command sending a pitch command
        to the platform with the desired pitch angle theta_c. """
        assert(type(self.altitude_cmd).__name__ == 'SetPitchAngleCmd')
        theta_c = self.altitude_cmd.theta_c
        self.platform.pitch_cmd(theta_c)

    def process_set_altitude_cmd(self, t, dt):
        """ Processes the altitude command which takes a desired altitude,
        and a desired pitch angle (theta_c) to either ascend or to
        descend to that altitude. The method calculates the error zerr
        in altitude. If we are within the altitude tolerance we simply
        set the platform altitude to the desired altitude and level out
        the pitch angle to 0.0. Otherwise we issue a pitch commmand
        with the desired pitch angle (theta_c) to the platform.

        Note that the platform can only control altitude through pitching
        the nose up or down. If you want to descend and pitch your nose
        up (or vice versa), you'll never get to your desired altitude.

        That's a warning that the flight control system is not smart enough
        to prevent the pilot agent from doing stupid things.
        """
        assert(type(self.altitude_cmd).__name__ == 'SetAltitudeCmd')
        z_c, theta_c = (self.altitude_cmd.z_c, self.altitude_cmd.theta_c)
        self.platform.z_c = z_c
        altitude_tolerance = 1.0 / dt
        zerr = np.fabs(z_c - self.platform.z)
        if zerr < altitude_tolerance:
            self.platform.set_altitude(z_c)
            self.platform.pitch_cmd(0.0)
        else:
            self.platform.pitch_cmd(theta_c)

    def process_set_speed_cmd(self, t, dt):
        """ Processes the speed command by telling the platform model the
        desired speed v_c.
        """
        assert(type(self.speed_cmd).__name__ == 'SetSpeedCmd')
        v_c = self.speed_cmd.v_c
        self.platform.speed_cmd(v_c)

    def process_set_heading_cmd(self, t, dt):
        """ Processes the set heading command by telling the platform model
        of the desired yaw command angle (psi_c)
        """
        assert(type(self.direction_cmd).__name__ == 'SetHeadingCmd')
        psi_c = self.direction_cmd.psi_c
        self.platform.yaw_cmd(psi_c)

    def process_set_heading_gload_cmd(self, t, dt):
        """ Process the set heading cmd with a desired g loading. """
        assert type(self.direction_cmd).__name__ == 'SetHeadingGLoadCmd'
        psi_c = self.direction_cmd.psi_c
        gload_c = self.direction_cmd.gload_c
        gload_max = self.platform.gload_max
        gload_c = gload_max if gload_c > gload_max else gload_c 
        phi_c = np.degrees(np.arccos(1.0/gload_c))
        self.platform.yaw_cmd(psi_c)
        self.platform.roll_cmd(phi_c)

    def process_set_waypoint_cmd(self, t, dt):
        """
        Processes a set waypoint command which tells the aircraft
        model to fly to a commanded waypoint (x_c, y_c).
        Note that here we don't consider altitude. We control that separately.
        The aircraft's current position is (x, y).
        The difference in position (dx, dy) is calculated and then the
        range/distance to the waypoint is calculated using NumPy's hypot
        function (this is just Pythagoras).
        If we haven't reached the waypoint, we calculate the desired
        yaw angle (psi_c) using atan2 - this gives us the direction
        we need fly. There is a conversion to degrees and also
        a constraint to (0,360) degrees. Finally we issue the command
        to underlying platform model.
        """
        assert(type(self.direction_cmd).__name__ == 'SetWaypointCmd')
        waypoint_tolerance = 10.0
        x_c, y_c = (self.direction_cmd.x_c, self.direction_cmd.y_c)
        x, y = (self.platform.x, self.platform.y)
        dx = x_c - x
        dy = y_c - y
        distance_to_wp = np.hypot(dx, dy)
        if distance_to_wp > waypoint_tolerance:
            psi_c = ut.constrain_360(np.degrees(np.arctan2(dy, dx)))
            self.platform.yaw_cmd(psi_c)
            #print (t, x, y, x_c, y_c, self.platform.psi, psi_c)
