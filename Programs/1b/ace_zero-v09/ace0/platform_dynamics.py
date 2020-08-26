#!/usr/env python 

"""
Platform Dynamics Model

This is a simple flight dynamics that is by no means realistic.
It can be described as an arcade level flight dynamics model.
It isn't quite complete and still needs tuning. 

Internally the model uses SI units (metres, m/s etc.)

The platform dynamics model is represented by a number of state 
variables:

- Position (x, y, z)
- Orientation (psi, theta, phi) or (yaw, pitch, roll)
- Speed (v)
- Weight (m) and Fuel (fuel)

Note that the weight of the aircraft and the fuel are not taken into
account in the dynamics calculations. This will be added at future date.

Also, we haven't modelled angle of attack (alpha) or slide-slip angle (beta).
The aircraft's velocity vector will be the direction it's nose is pointed at.

TODO:
- Move the control law variables out of the code and into the data files.
- Add roll angle and the ability to turn at different g-forces
"""

__author__ = 'mikepsn'

import numpy as np
import scipy.constants
import utils as ut


class PlatformDynamics(object):
    """
    The platform model is defined by the following state variables:
    Position: x, y, z (metres)
    Orientation: psi, theta, phi (yaw, pitch, roll) in (degrees)
    Mass/Fuel: (kg) - for the future.
    
    Additionally, the model keeps of track of a number of commanded/desired
    values. Theses are:
    z_c - desired/commanded altitude
    psi_c - desired/commanded yaw angle psi
    theta_c - desired/commanded pitch angle theta
    v_c - desired/command speed v

    The model also keeps track of it's trajectory through 3D space for plotting
    purposes. This is stored as a list of tuples in the self.trace atttribute.
    Each tuple in the list represents the state of the aircraft at a single
    time step. 
    """

    def __init__(self, x=0.0, y=0.0, z=0.0,
                vx=0.0, vy=0.0, vz=0.0,
                ax=0.0, ay=0.0, az=0.0,
                psi=0.0, theta=0.0, phi=0.0,
                v=0.0, weight=0.0, fuel=0.0,
                v_min=100, v_max=1000, v_K=0.1,
                theta_K=0.005, psi_K=10.0, gload_max=9.0, **kwargs):
        self.x = x
        self.y = y
        self.z = z
        self.vx = vx            # velocity x
        self.vy = vy            # velocity y
        self.vz = vz            # velocity y
        self.ax = ax            # acceleration x
        self.ay = ay            # acceleration y
        self.az = az            # acceleration y
        self.psi = psi          # heading
        self.theta = theta      # pitch
        self.phi = phi          # roll
        self.v = v              # velocity
        self.gload = 1.0        # current gload factor
        self.fuel = fuel
        self.weight = weight
        self.v_min = v_min      # platform minimum velocity
        self.v_max = v_max      # platform maximum velocity
        self.gload_max = gload_max # Maximum allowed gload
        self.v_K = v_K          # velocity change constant
        self.theta_K = theta_K  # pitch angle change constant
        self.psi_K = psi_K      # turn rate constant

        # Desired values
        self.z_c = self.z
        self.psi_c = self.psi
        self.theta_c = self.theta
        self.phi_c = self.phi
        self.v_c = self.v

        self.trace = []

    def __repr__(self):
        """ Printer friendly representation of the aircraft state. """
        return "(%3.2f, %3.2f, %3.2f) : (%3.2f, %3.2f, %3.2f) : (%3.2f, %3.2f, %3.2f) : \
                (%3.2f, %3.2f, %3.2f) : (%3.2f, %3.2f, %3.2f)" % \
               (self.x, self.y, self.z,
                self.vx, self.vy, self.vz,
                self.ax, self.ay, self.az,
                self.psi, self.theta, self.phi,
                self.v, self.weight, self.fuel)

    def record_trace(self, t, dt):
        """ Appends the current state of the aircraft to the trace list. """
        timeslice = (t, self.x, self.y, self.z,
                     self.vx, self.vy, self.vz,
                     self.ax, self.ay, self.az,
                     self.psi, self.theta, self.phi, 
                     self.v, self.weight, self.fuel)
        self.trace.append(timeslice)

    def tick(self, t, dt):
        """
        Ticks the platform model for the current time step.
        - Records the aircraft trace
        - Controls the aircraft yaw, speed and pitch
        - Updates the aircraft dynamics equations.
        """
        self.record_trace(t, dt)
        self.yaw_control(t, dt)
        self.speed_control(t, dt)
        self.pitch_control(t, dt)
        self.update_platform(t, dt)

    def update_platform(self, t, dt):
        """
        Solves the equations of motion for the current timestep and determines
        the new position (xn, yn, zn) of the aircraft. 
        """
        sin, cos = np.sin, np.cos
        x, y, z = (self.x, self.y, self.z)
        psi = np.radians(self.psi)
        theta = np.radians(self.theta)
        phi = np.radians(self.phi)
        self.gload = 1.0/np.cos(phi)
        v = self.v 
        xn = x + v * cos(psi) * dt
        yn = y + v * sin(psi) * dt
        zn = z + v * sin(theta) * dt

        self.vx, self.vy, self.vz = ut.motion_derivative(xn, yn, zn, x, y, z, dt)
        self.ax, self.ay, self.az = ut.motion_derivative(self.vx, self.vy, self.vz,
                                                         self.trace[-1][4], self.trace[-1][5], self.trace[-1][6],
                                                         dt)
        self.x, self.y, self.z = (xn, yn, zn)

    def set_position(self, x, y):
        """ Sets the aircraft position to (x, y). """
        self.x = x
        self.y = y

    def get_position(self):
        """ Returns the aircraft position. """
        return (self.x, self.y)

    def set_altitude(self, z):
        """ Sets the aircraft altitude to z. """
        self.z = z

    def set_gload(self, gload):
        """ Sets the aircraft g load factor. """
        self.gload = gload

    def get_altitude(self):
        """ Returns the aircraft's current altitude """
        return (self.z)

    def get_orientation(self):
        """ Returns the aircraft's yaw, pitch and roll angles as a tuple. """
        return (self.psi, self.theta, self.phi)

    def get_speed(self):
        """ Returns the aircraft's current speed. """
        return (self.v)

    def speed_cmd(self, vc):
        """ Sets the desired/commanded speed v_c. """
        self.v_c = vc

    def altitude_cmd(self, zc, theta_c):
        """ DEPRECATED
        Issues an altitude command by setting a desired altitude
        z_c and a desired pitch angle theta_c. Note that this type of
        alitude control has been moved into the flight control model
        and hence this method is deprecated. """
        self.z_c = zc
        self.theta_c = theta_c

    def yaw_cmd(self, psi_c):
        """ Sets the desired/commanded yaw angle psi_c """
        self.psi_c = psi_c

    def pitch_cmd(self, theta_c):
        """ Sets the desired/commanded pitch angle theta_c """
        self.theta_c = theta_c

    def roll_cmd(self, phi_c):
        """ Sets the desired roll angle phi_c  """
        self.phi_c = phi_c

    def speed_control(self, t, dt):
        """
        Linear control law to adjust aircraft speed. 
        """
        v_tolerance = 1.0
        v_err = self.v_c - self.v
        self.v = self.v + self.v_K * v_err * dt
        self.v = max(min(self.v_max, self.v), self.v_min)

    def altitude_control(self, t, dt):
        """
        NOTE: DEPRECATED
        Control law for altitude. Note that this
        has been moved to the flight control system 
        and is now deprecated here.
        """
        altitude_tolerance = 1.0
        zerr = np.fabs(self.z_c - self.z)
        if zerr > altitude_tolerance:
            self.pitch_control(t, dt)
        else:
            self.z = self.z_c
            self.pitch_cmd(theta_c=0.0)
            self.pitch_control(t, dt)

    def pitch_control(self, t, dt):
        """
        Linear control law for pitch control. 
        TODO: 
        - The control variable K_theta really needs to be tuned
        - Should we set up/lower limits for the pitch angle?
        - Move the control variables to a data file.
        """
        pitch_tolerance = 1e-3
        theta_rate, theta_min, theta_max = (1.0, -70.0, 70.0)
        theta_err = self.theta_c - self.theta
        self.theta = self.theta + self.theta_K * theta_err * dt
        self.theta = max(min(theta_max, self.theta), theta_min)

    def roll_control(self, t, dt):
        """ Roll Control """
        roll_tolerance = 1e-3
        roll_err = self.phi_c - self.phi
        self.phi = self.phi + 0.1 * roll_err * dt

    def yaw_control(self, t, dt):
        """
        Linear control law for yaw control. 
        TODO: Still need to tune control parameters/variables.
        """
        psi_tolerance = 0.1

        a = self.psi
        b = ut.constrain_360(self.psi_c)
        c = ut.smallest_angle(a, b)

            # Calculate the turn rate based on the bank angle
            # The turn rate omega is defined as
            # omega = g tan(phi) / v
            # where v is the velocity
            # Take the absolute value of the turn rate omega
            # We then need to convert omega into deg/s from rad/s
        g = scipy.constants.g
        omega = g * np.tan(np.radians(self.phi))/self.v
        self.psi_K = np.degrees(np.fabs(omega))

        if np.fabs(c) > psi_tolerance:
            if c < 0:
                self.psi = self.psi - self.psi_K * dt
                self.roll_cmd(-self.phi_c)
            else:
                self.psi = self.psi + self.psi_K * dt
        else:
            self.psi = self.psi_c
            self.roll_cmd(0.0)

        self.roll_control(t, dt)

        self.psi = ut.constrain_360(self.psi)



