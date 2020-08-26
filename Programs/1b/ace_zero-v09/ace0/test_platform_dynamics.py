#!/usr/env python

""" Tests for the Platform class. """

__author__ = 'mikepsn'

import unittest
import platform_dynamics

class TestPlatformDynamics(unittest.TestCase):
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
        self.tmin, self.tmax, self.dt = (0, 3.0, 0.1)
        self.start = { 'x' : 100.0, 'y' : 100.0, 'z' : 100.0,
                       'psi' : 30.0, 'theta' : 0.0, 'phi' : 0.0,
                       'v': 100.0, 'weight' : 100.0, 'fuel' : 100.0}
    
    def test_climb(self):
        """
        Tests the ability of the platform model to climb to the desired altitude. 
        Issues an altitude_cmd with a desired altitude and pitch angle.
        """
        p = platform_dynamics.PlatformDynamics(**self.start)

        altitude = 120.0
        pitch_angle = 10.0

        p.altitude_cmd(altitude, pitch_angle)

        t = self.tmin
        while t < self.tmax:
            p.tick(t, self.dt)
            t += self.dt

        self.assertAlmostEqual(p.z, altitude, delta=1.0)
        self.assertAlmostEqual(p.theta_c, 0.0, delta=1.0)


if __name__ == '__main__':
    unittest.main()
