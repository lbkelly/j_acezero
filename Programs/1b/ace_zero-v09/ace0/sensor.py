"""
Sensor Model
"""

import numpy as np
from states import SensorState, SensorTrack

def spherical_to_cartesian(r, theta, phi): 
    x = r * np.sin(np.radians(phi)) * np.cos(np.radians(theta))
    y = r * np.sin(np.radians(phi)) * np.sin(np.radians(theta))
    z = r * np.cos(np.radians(phi))
    return (x, y, z)

def cartesian_to_spherical_old(x, y, z):
    r = np.sqrt(x*x + y*y + z*z)
    phi = np.degrees(np.arccos(z/r))
    theta = np.degrees(np.arctan2(y, x))
    return (r, theta, phi)

def cartesian_to_spherical(x, y, z):
    r = np.sqrt(x*x + y*y + z*z)
    elevation = np.degrees(np.arccos(z/r))
    azimuth = np.degrees(np.arctan2(y, x))
    return (r, azimuth, elevation)

def rotate_x(angle, point):
    x, y, z = point
    theta = np.radians(angle)
    xn = x
    yn = y * np.cos(theta) - z * np.sin(theta)
    zn = y * np.sin(theta) + z * np.cos(theta)
    return (xn, yn, zn)

def rotate_y(angle, point):
    x, y, z = point
    theta = np.radians(angle)
    xn = x * np.cos(theta) + z * np.sin(theta)
    yn = y
    zn = -x * np.sin(theta) + z * np.cos(theta)
    return (xn, yn, zn)

def rotate_z(angle, point):
    x, y, z = point
    theta = np.radians(angle)
    xn = x * np.cos(theta) - y * np.sin(theta)
    yn = x * np.sin(theta) + y * np.cos(theta)
    zn = z
    return (xn, yn, zn)

class Sensor(object):
    """ A model of a sensor. """
    def __init__(self, name="Sensor",
                 max_range=19500.0,
                 fov=30.0,
                 s_x=0.0, s_y=0.0, s_z=0.0,
                 s_psi=0.0, s_theta=0.0, s_phi=0.0, **kwargs):
        self.name = name
        self.max_range = max_range
        self.fov = fov
        self.s_x = s_x
        self.s_y = s_y
        self.s_z = s_z
        self.s_psi = s_psi
        self.s_theta = s_theta
        self.s_phi = s_phi

        self.ac_x = 0.0
        self.ac_y = 0.0
        self.ac_z = 0.0
        self.ac_psi = 0.0
        self.ac_theta = 0.0
        self.ac_phi = 0.0

        self.entities = []
        self.tracks = {}

    def tick(self, t, dt):

        for e in self.entities:
            sx, sy, sz = self.convert_to_sensor_coordinates(e.x, e.y, e.z)
            r, theta, phi = cartesian_to_spherical(sx, sy, sz)

            in_range = self.in_range(r)
            in_fov = self.in_fov(theta, phi)

            if in_range and in_fov:
                self.update_tracks(t, dt, e, r, theta, phi)

            # Remove any old tracks
        self.tracks = {key:self.tracks[key] for key in self.tracks if self.tracks[key].current_time == t}

    def update_tracks(self, t, dt, entity, r, theta, phi):
        """ Updates the track dictionary with the latest track. """
        track = SensorTrack()
        track.callsign = entity.callsign
        track.id = entity.id
        track.side = entity.side
        track.x = entity.x
        track.y = entity.y
        track.z = entity.z
        track.v = entity.v
        track.track_range = r
        track.track_psi = theta
        track.track_theta = phi

        if self.tracks.has_key(entity.callsign):
            track.start_time = self.tracks[entity.callsign].start_time
            track.current_time = t
            track.total_time = self.tracks[entity.callsign].total_time + dt
        else:
            track.start_time = t
            track.current_time = t
            track.total_time = dt

            # Replace the track with the updated data
        self.tracks[entity.callsign] = track


    def get_state(self):
        """ Returns the current state of the sensor model. """
        sensor_state = SensorState()
        sensor_state.name = self.name
        sensor_state.max_range = self.max_range
        sensor_state.fov = self.fov
        sensor_state.tracks = self.tracks
        return sensor_state

    def update_aircraft_state(self, ac_state):
        """ Updates the aircraft's position orientation that the sensor is attached to. """
        self.ac_x = ac_state.x
        self.ac_y = ac_state.y
        self.ac_z = ac_state.z
        self.ac_psi = ac_state.psi
        self.ac_theta = ac_state.theta
        self.ac_phi = ac_state.phi

    def update_entities(self, entities):
        """ Updates the list of entities to search through to see if we can see any of them. """
        self.entities = entities

    def convert_to_sensor_coordinates(self, x, y, z):
        """ Converts the position of the entity to sensor coordinates. """
            # Get the location of the aircraft and the sensor
        ax, ay, az = self.ac_x, self.ac_y, self.ac_z
        sx, sy, sz = self.s_x, self.s_y, self.s_z

            # Translate the coordinates
        tx = x - (ax + sx)
        ty = y - (ay + sy)
        tz = z - (az + sz)

            # Get the orientation of the aircraft and the sensor
        a_psi, a_theta, a_phi = self.ac_psi, self.ac_theta, self.ac_phi
        s_psi, s_theta, s_phi = self.s_psi, self.s_theta, self.s_psi

            # Now rotate around the x, y and z axes
            # Temporarily disable the roll angle. 
            # This makes the sensor roll stabilized.
        p0 = (tx, ty, tz) 
        p1 = rotate_z( -(a_psi   + s_psi),   p0)
        p2 = rotate_y( -(a_theta + s_theta), p1)
        #p3 = rotate_x( -(a_phi   + s_phi),   p2)

        nx, ny, nz = p2

        return (nx, ny, nz)

    def in_range(self, r):
        return r <= self.max_range

    def in_fov(self, theta, phi):
        angle = self.fov / 2.0
        in_theta = (theta <= angle and theta >= -angle)
        in_phi = (phi <= 90 + angle and phi >= 90 - angle)
        return in_theta and in_phi
