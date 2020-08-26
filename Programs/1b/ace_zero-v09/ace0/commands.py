"""
Commands Module

This module contains a list of commands that the pilot agent can send to the flight control system.
Each command represents an atomic agent action that the pilot can generate.
Each command is defined as a named tuple, specified by the command name and a list of parameters.
In the case where the command doesn't have any parameters, we just use an empty list. 

Note that all the parameters for a command are denoted by an underscore _c.
This is to represent the commanded value and not the actual value of a parameter. 
We use this to differentiate the commanded value and the actual value when we 
calculate the error in the flight control system. 

The list of commands currently supported include:

- SetFlyLevelCmd: sets the desired pitch (theta_c) and roll (phi_c) angles to 0.0
- SetPitchAngleCmd: sets the desired pitch (theta_c) angle. will cause the aircraft to ascend or descend
- SetAltitudeCmd: sets the desired altitude (z_c) with a desired pitch (theta_c) angle
- SetSpeedCmd: sets the desired aircraft speed (v_c)
- SetHeadingCmd: sets the desired aircraft heading (psi_c)
- SetWaypointCmd: sets the desired waypoint to fly to (x_c, y_c)
"""

__author__ = 'mikepsn'

from collections import namedtuple

SetFlyLevelCmd = namedtuple('SetFlyLevelCmd', [])
SetPitchAngleCmd = namedtuple('SetPitchAngleCmd', ['theta_c'])
SetAltitudeCmd = namedtuple('SetAltitudeCmd', ['z_c', 'theta_c'])
SetSpeedCmd = namedtuple('SetSpeedCmd', ['v_c'])
SetHeadingCmd = namedtuple('SetHeadingCmd', ['psi_c'])
SetHeadingGLoadCmd = namedtuple('SetHeadingGLoadCmd', ['psi_c', 'gload_c'])
SetWaypointCmd = namedtuple('SetWaypointCmd', ['x_c', 'y_c'])