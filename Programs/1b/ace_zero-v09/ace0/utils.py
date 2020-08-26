"""
Utility Functions
"""

from __future__ import division
import numpy as np
from operator import sub
import scipy.constants
import math
import sys, os

__author__ = 'mikepsn, lrbenke'

def find_data_file(filename):
    if getattr(sys, 'frozen', False):
        # The application is frozen
        datadir = os.path.dirname(sys.executable)
    else:
        # The application is not frozen
        # Change this bit to match where you store your data files:
        datadir = os.path.dirname(__file__) + "\data\\"

    return os.path.join(datadir, filename)

def constrain_360(angle):
    """ Constrains the angle in degrees to (0, 360) """
    x = np.fmod(angle, 360)
    if x < 0:
        x += 360
    return x


def constrain_180(angle):
    """ Constrains the angle in degrees to (-180, 180) """
    x = np.fmod(angle, 360)
    if angle > 180:
        angle -= 360
    return angle


def smallest_angle(a, b):
    """ Returns the smallest angle between two angles including direction """
    return min(b-a, b-a+360, b-a-360, key=abs)


def nautical_miles_to_metres(a):
    """ Converts nautical miles to metres """
    nautical_mile = scipy.constants.nautical_mile
    return a * nautical_mile


def metres_to_nautical_miles(a):
    """ Converts metres to nautical miles """
    nautical_mile = scipy.constants.nautical_mile
    return float(a)/nautical_mile


def feet_to_metres(a):
    """ Converts feet to metres """
    foot = scipy.constants.foot
    return a * foot


def metres_to_feet(a):
    """ Converts metres to feet """
    foot = scipy.constants.foot
    return float(a)/foot


def knots_to_mps(a):
    """ Converts knots to metres per second """
    knot = scipy.constants.knot
    return a * knot


def mps_to_knots(a):
    """ Converts metres per second to knots """
    knot = scipy.constants.knot
    return float(a)/knot


def mps_to_mach(v):
    """ Converts speed from metres per second to mach number. """
    mach = scipy.constants.mach
    return float(v)/mach


def distance(p1, p2):
    """ Calculates the distance between two positions """
    diff = np.subtract(p1, p2)
    return np.linalg.norm(diff)


def get_location_vector( obj ) :
    return np.matrix( [ getattr( obj, name) for name in [ 'x', 'y', 'z'] ] )


def get_velocity_vector( obj ) :
    #  ECU 23/02/17 lbkelly - commented out code, potentially wrong (z component uses sin, not cos)
    # return np.matrix([obj.v * np.cos(np.radians(obj.psi)),obj.v * np.sin(np.radians(obj.psi)),
    #  obj.v * np.cos(np.radians(obj.theta))] )
    return np.matrix([obj.v * np.cos(np.radians(obj.psi)), obj.v * np.sin(np.radians(obj.psi)),
                      obj.v * np.sin(np.radians(obj.theta))] )


def get_range( obj1, obj2 ) :
    o1_loc = get_location_vector( obj1 )
    o2_loc = get_location_vector( obj2 )
    separation_vector = o1_loc - o2_loc
    return np.linalg.norm(separation_vector)


def get_aspect_angle( obj1, obj2 ) :
    o1_loc = get_location_vector( obj1 )
    o2_loc = get_location_vector( obj2 )
    separation_vector = o1_loc - o2_loc
    velocity_vector = get_velocity_vector(obj2)
    cosine_taa = separation_vector * velocity_vector.transpose() / ((np.linalg.norm(separation_vector) * np.linalg.norm(velocity_vector)))
    return np.degrees( np.arccos( cosine_taa ))


def get_bearing_angle( obj1, obj2 ) :
    o1_loc = get_location_vector( obj1 )
    o2_loc = get_location_vector( obj2 )
    separation_vector = o1_loc - o2_loc
    velocity_vector = get_velocity_vector(obj1)
    cosine_ba = separation_vector * velocity_vector.transpose() / ((np.linalg.norm(separation_vector) * np.linalg.norm(velocity_vector)))
    return np.degrees( np.arccos( cosine_ba ))


def relative_bearing(own_x, own_y, other_x, other_y):
    """ Calculates the bearing from one position to another """
    return constrain_360(
            np.degrees(np.arctan2(other_y - own_y, other_x - own_x)))


def reciprocal_heading(heading):
    """ Calculates the reciprocal (anti-parallel) heading """
    return constrain_360(heading + 180)


def is_reciprocal(h1, h2):
    """ Returns True if the headings are reciprocal (at 180 degrees) """
    relative_heading = constrain_360(h1 - h2)
    return is_close(relative_heading, 180.0)


def is_close(a, b, rel_tol=1e-09, abs_tol=0.0):
    """ Returns True if a and b are close to within floating point error (can
     be replaced by math.isclose() in Python 3.5+) """
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


def lateral_displacement(own_x, own_y, threat_x, threat_y, threat_heading,
        threat_range):
    """ Returns the perpendicular distance to the threat flight path using the
    rule `sin(theta) = opposite/hypotenuse`; assumes headings in degrees """
    taa = target_aspect_angle(own_x, own_y, threat_x, threat_y, threat_heading)
    return abs(threat_range * math.sin(math.radians(taa)))


def target_aspect_angle(own_x, own_y, threat_x, threat_y, threat_heading):
    """ Calculates the target aspect angle (TAA) """
    threat_bearing = relative_bearing(own_x, own_y, threat_x, threat_y)
    return reciprocal_heading(threat_bearing) - threat_heading


def is_angle_ccw(angle_1, angle_2):
    """ Returns True if the shortest angle from angle_1 to angle_2 is
    counter-clockwise """
    diff = angle_2 - angle_1
    return diff > 180 if diff > 0 else diff >= -180


def speed_difference(speed_1, speed_2):
    """
    Returns the absolute difference in speed between two fighters

    :param speed_1: speed of the first fighter
    :param speed_2: speed of the second fighter
    :return: absolute speed difference value as float
    """
    return abs(speed_1 - speed_2)


def altitude_difference(height_1, height_2):
    """
    Returns the absolute difference in height between two fighters

    :param height_1: height of the first fighter from y coord
    :param height_2: height of the second fighter from y coord
    :return: absolute speed difference value as float
    """
    return abs(height_1 - height_2)


def is_behind(obj1, obj2):
    """"
    Returns true if object 1, is behind object 2

    :param obj1: the attacking plane
    :param obj2: the target plane
    :return: boolean value to depict if the object is behind on not
    """
    separation = get_location_vector(obj1) - get_location_vector(obj2)
    separation /= np.linalg.norm(separation)
    temp = get_velocity_vector(obj2).getA1()
    if np.dot(separation, temp) > 0:
        return False
    else:
        return True

def is_in_attack_angle(obj1, obj2, max_angle):
    """"
    Returns true if object 2, is within the viewing cone of X degrees,
    stipulated by max angle of the first object

    :param obj1: the attacking plane
    :param obj2: the target plane
    :param max_angle: the max angle from the nose cone to attack from
    :return: boolean value to depict if the target object is within the viewing cone of object the attacker
    """

    separation = get_location_vector(obj2).getA1() - get_location_vector(obj1).getA1()
    # print 'seperation: ', separation
    attacker_forward = get_velocity_vector(obj1).getA1()
    # print 'attacker_forward:', attacker_forward
    combined_norms = np.sqrt(separation.dot(separation)) * np.sqrt(attacker_forward.dot(attacker_forward))
    # print 'combined_norms:', combined_norms
    temp_dot = np.dot(separation, attacker_forward) / combined_norms
    """
    todo: lbkelly
    Needs to be changed. Ugly and changed for testing
    np.dot some times returns a value of 1.00000002 and this stuffs up the np.arccos call.
     np.arccos can't have a value greater than 1.0
    """
    if temp_dot >= 1.0:
        temp_dot = 1.0

    if temp_dot <= -1.0:
        temp_dot = -1.0

    angle_between_attacker_target = np.rad2deg(np.arccos(temp_dot))
    # print np.dot(separation, attacker_forward) / combined_norms

    if angle_between_attacker_target < max_angle / 2:
        return True
    else:
        return False


def is_in_reverse_attack_angle(obj1, obj2, max_angle):
    """"
       Returns true if object 2, is within the viewing cone of X degrees,
       stipulated by max angle of the first object

       :param obj1: the attacking plane
       :param obj2: the target plane
       :param max_angle: the max angle from the nose cone to attack from
       :return: boolean value to depict if the target object is within the viewing cone of object the attacker
       """
    separation = get_location_vector(obj2).getA1() - get_location_vector(obj1).getA1()
    attacker_forward = get_velocity_vector(obj1).getA1() * -1
    combined_norms = np.sqrt(separation.dot(separation)) * np.sqrt(attacker_forward.dot(attacker_forward))

    temp_dot = np.dot(separation, attacker_forward) / combined_norms
    """
    todo: lbkelly
    Needs to be changed. Ugly and changed for testing
    np.dot some times returns a value of 1.00000002 and this stuffs up the np.arccos call.
     np.arccos can't have a value greater than 1.0
    """
    if temp_dot >= 1.0:
        temp_dot = 1.0

    if temp_dot <= -1.0:
        temp_dot = -1.0

    angle_between_attacker_target = np.rad2deg(np.arccos(temp_dot))
    # angle_between_attacker_target = np.rad2deg(np.arccos(np.dot(separation, attacker_forward) / combined_norms))
    if angle_between_attacker_target < max_angle / 2:
        return True
    else:
        return False


def motion_derivative(x1, y1, z1, x2, y2, z2, time):
    """
    Returns the derivative of the values sent in.
    Can derive the velocity if two positional points are sent in.
    Can derive the acceleration if two velocity points are sent in.

    :param x1: the first x position
    :param y1: the first y position
    :param z1: the first z position
    :param x2: the second x position
    :param y2: the second y position
    :param z2: the second z position
    :param time: the time that has elapsed between the two points
    :return: the derivative of the points given
    """
    derived_x = (x2 - x1) / time
    derived_y = (y2 - y1) / time
    derived_z = (z2 - z1) / time
    return abs(derived_x), abs(derived_y), abs(derived_z)


def delta_parameter(obj1, obj2):
    """
    Return the difference in position, velocity and accleration between the two objects

    :param obj1: the attacking plane, contains the pos, velocity and acceleration
    :param obj2: the target plane, contains the pos, the velocity and the acceleration
    :return: a tuple of the difference in position, velocity and acceleration
    """
    return tuple(map(sub, obj2, obj1))


def rotation_matrix(axis, theta):
    """
    Return the rotation matrix associated with counterclockwise rotation about
    the given axis by theta radians.

    todo: not used, needs to be deleted after i recheck 'LBKELLY'
    """
    axis = np.asarray(axis)
    axis = axis/math.sqrt(np.dot(axis, axis))
    a = math.cos(theta/2.0)
    b, c, d = -axis*math.sin(theta/2.0)
    aa, bb, cc, dd = a*a, b*b, c*c, d*d
    bc, ad, ac, ab, bd, cd = b*c, a*d, a*c, a*b, b*d, c*d
    return np.array([[aa+bb-cc-dd, 2*(bc+ad), 2*(bd-ac)],
                     [2*(bc-ad), aa+cc-bb-dd, 2*(cd+ab)],
                     [2*(bd+ac), 2*(cd-ab), aa+dd-bb-cc]])


