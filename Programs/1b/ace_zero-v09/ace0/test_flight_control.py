#!/usr/env python

""" Tests for the Platform class. """

__author__ = 'mikepsn'

import unittest
import flight_control
import commands as cmds

class TestFlightControl(unittest.TestCase):
    """ 
    Test the basic commands for the platform dynamics model. 
    Each tests issues a command, ticks the platform model a number of steps
    and then asserts to see if the platform model is in the desired state.
    Additionally, a call to draw_platform_trace is made to generate a plot
    of the trajectory of the platform during the test. 
    """

    @classmethod
    def setUpClass(self):
        """ Common initialisation data for all the tests. """
        self.tmin, self.tmax, self.dt = (0, 10.0, 0.1)
        self.start = { 'x' : 100.0, 'y' : 100.0, 'z' : 100.0,
                       'psi' : 30.0, 'theta' : 0.0, 'phi' : 0.0,
                       'v': 1.0, 'weight' : 100.0, 'fuel' : 100.0}
    
    def test_climb(self):
        """
        Tests the ability of the platform model to climb to the desired altitude. 
        Issues an altitude_cmd with a desired altitude and pitch angle.
        """
        fcs = flight_control.FlightControl(**self.start)

        altitude = 120.0
        pitch_angle = 10.0
        alt_cmd = cmds.SetAltitudeCmd(120.0, 10.0)
        fcs.set_altitude_cmd(alt_cmd)

        #heading = 150.0
        #heading_cmd = cmds.SetHeadingCmd(heading)
        #fcs.set_direction_cmd(heading_cmd)

        t = self.tmin
        while t < self.tmax:
            fcs.tick(t, self.dt)
            t += self.dt

        self.assertAlmostEqual(fcs.platform.z, altitude, delta=1.0)
        self.assertAlmostEqual(fcs.platform.theta_c, 0.0, delta=1.0)

    def test_descend(self):
        pass

    def test_heading_change(self):
        fcs = flight_control.FlightControl(**self.start)
        heading = 150.0
        heading_cmd = cmds.SetHeadingCmd(heading)
        fcs.set_direction_cmd(heading_cmd)

        t = self.tmin
        while t < self.tmax + 100.0:
            fcs.tick(t, self.dt)
            t += self.dt

    def test_waypoint(self):
        fcs = flight_control.FlightControl(**self.start)
        fcs.set_direction_cmd(cmds.SetWaypointCmd(6000, 6000))

        t = self.tmin
        while t < self.tmax + 200.0:
            if t > 100.0:
                fcs.set_direction_cmd(cmds.SetWaypointCmd(300, 600))
                fcs.set_altitude_cmd(cmds.SetAltitudeCmd(180.0, 1.0))
                fcs.set_speed_cmd(cmds.SetSpeedCmd(1.0))
            if t > 150.0:
                fcs.set_direction_cmd(cmds.SetWaypointCmd(1000, 4000))
            fcs.tick(t, self.dt)
            t += self.dt

if __name__ == '__main__':
    unittest.main()
