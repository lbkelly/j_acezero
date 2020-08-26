#!/usr/bin/python3
import six
import random
import numpy as np
import matplotlib
import math
import sys
import os
import string
from states import FighterState
import utils as ut
import json
import copy
import itertools

class Agent(FighterState) :

    def __init__( self, designation, aerodynamics ) :
        super(Agent,self).__init__( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0)
        self.callsign = designation
        for attr in aerodynamics :
            setattr( self, attr, aerodynamics[attr])
        self.position = np.matrix( [0.0, 0.0, 0.0, 1.0])
        self.velocity = np.matrix( [0.0, 0.0, 0.0, 1.0])

    def sync_speed(self) :
        self.velocity[0,1] = self.v
        #self.v = ut.clamp( np.linalg.norm(self.velocity),self.v_min,self.v_max)

    def rotate( self ) :
        # define rotation matrix
        alpha_z = np.radians(self.psi)
        cz, sz = np.cos(alpha_z), np.sin(alpha_z)
        Rz = np.matrix( [ [cz, sz, 0.0, 0.0], [-sz, cz, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0,0.0,0.0,0.0] ])
        alpha_x = np.radians(self.theta)
        cx, sx = np.cos(alpha_x), np.sin(alpha_x)
        Rx = np.matrix( [[1.0, 0.0, 0.0, 0.0],[0.0, cx, sx, 0.0],[0.0, -sx, cx, 0.0],[0.0, 0.0, 0.0, 1.0]])
        self.velocity = self.velocity.transpose()
        self.velocity =  Rz * Rx * self.velocity
        self.velocity = self.velocity.transpose()


    def aspect_angle_wrt( self, other ) :
        separation_vector = self.position - other.position
        numerator = separation_vector * other.velocity.transpose()
        denominator = np.linalg.norm(separation_vector) * np.linalg.norm(other.velocity)
        aspect_angle = np.degrees( np.arccos( numerator / denominator ))
        return aspect_angle[0,0]


    def bearing_angle_wrt( self, other ) :
        separation_vector = other.position - self.position
        numerator = separation_vector * self.velocity.transpose()
        denominator = np.linalg.norm(separation_vector) * np.linalg.norm(self.velocity)
        bearing_angle = np.degrees( np.arccos( numerator / denominator ))
        return bearing_angle[0,0]

    def write( self, filename, template ) :
        self.x = self.position[0,0]
        self.y = self.position[0,1]
        self.z = self.position[0,2]
        payload = copy.deepcopy(template)
        for attr in payload :
            try :
                payload[attr] = getattr(self,attr)
            except AttributeError :
                pass
        with open(filename, 'w') as outstream :
            print( json.dumps(payload, sort_keys=True, indent=4), file=outstream)

# Classification of situation for each airplane according to (Park et al., IJASS-2016)
def classify_combat_situation_1v1( a1, a2 ) :
    AA_a1_a2 = a1.aspect_angle_wrt(a2)
    BA_a1_a2 = a1.bearing_angle_wrt(a2)

    if math.fabs(AA_a1_a2 - 180.0 ) <= 90.0 :
        if math.fabs(BA_a1_a2 - 180.0 ) <= 90.0 :
            return 'offensive'
        else :
            return 'neutral'

    if math.fabs(BA_a1_a2 - 180.0 ) <= 90.0 :
        return 'offensive'

    return 'defensive'

def test() :
    blue = Agent('blue')
    blue.yaw = 30.0
    blue.theta = -5.0
    blue.position = np.matrix( [4000.0, 1000.0, 7500.0, 1.0])
    blue.v = 250.0
    blue.sync_speed()
    blue.rotate()
    print( "speed of blue: {} m/s".format(np.linalg.norm(blue.velocity)))

    red = Agent('red')
    red.yaw = 270.0
    red.theta = 0.0
    red.position = np.matrix( [-4000.0, -1000.0, 9500.0, 1.0])
    red.v = 250.0
    red.sync_speed()
    red.rotate()
    print( "speed of red: {} m/s".format(np.linalg.norm(red.velocity)))

    print(str(blue))
    print(str(red))


    print( "AA(blue,red) = {} degrees".format(blue.aspect_angle_wrt(red)) )
    print( "BA(blue,red) = {} degrees".format(blue.bearing_angle_wrt(red)) )
    print( "AA(red,blue) = {} degrees".format(red.aspect_angle_wrt(blue)) )
    print( "BA(red,blue) = {} degrees".format(red.bearing_angle_wrt(blue)) )

    # Classification of situation for each airplane according to (Park et al., IJASS-2016)
    situation = classify_combat_situation_1v1( blue, red )
    print( "{} perceives his relative position to {} as {}".format(blue.designation, red.designation, situation))
    situation = classify_combat_situation_1v1( red, blue )
    print( "{} perceives his relative position to {} as {}".format(red.designation, blue.designation, situation))

def parse_arguments() :
    import argparse

    parser = argparse.ArgumentParser(description='scgen - Random Scenario Generator of Stern Conversion Tasks')
    parser.add_argument('--tag', required=True, help='Descriptive tag for the generated scenarios, they will be stored in directory with the same name. It can contain the "/" symbol.')
    parser.add_argument('--num_instances', required=False, type=int, help='Number of instances to be generated', default=100)
    parser.add_argument('--max_altitude', required=False, type=float, help='Maximum altitude of airplanes (m/s)', default=12000.0)
    parser.add_argument('--min_altitude', required=False, type=float, help='Minimum altitude of airplanes (m/s)', default=6000.0)
    parser.add_argument('--max_distance', required=False, type=float, help='Maximum (radial) distance from the world origin (meters)', default=2000.0 )
    parser.add_argument('--min_speed', required=False, type=float, help ='Minimum airspeed of airplanes (m/s)', default=100.0)
    parser.add_argument('--max_speed', required=False, type=float, help ='Maximum airspeed of airplanes (m/s)', default=500.0)
    parser.add_argument('--blue_callsign', required=False, help='Blue aircraft callsign', default='snake')
    parser.add_argument('--red_callsign', required=False, help='Red aircraft callsign', default='viper')

    args = parser.parse_args()
    if  os.path.exists( args.tag  ) :
        print( 'Directory matching the supplied tag "{}" found, please move or delete the folder before proceeding!'.format(args.tag))
        print( 'Bailing out')
        sys.exit(1)
    return args

def determine_heading( airplane ) :
    # Any heading between 0 and 360 degrees, with
    # 1 degree granularity
    airplane.psi = random.randrange(0.0,359.0,1.0)

def determine_pitch( airplane ) :
    # pitch constrained to lie between -30 and 30 degrees,
    # with 1 degree increments
    airplane.theta = random.randrange(-70.0,70.0,1.0)

def determine_speed( airplane, min_speed, max_speed) :
    airplane.v = random.randrange(min_speed, max_speed, 1.0)

def determine_position( airplane, max_distance, min_altitude, max_altitude ) :
    min_distance = 200.0 # minimum distance is 200 meters

    altitude = random.randrange(min_altitude, max_altitude, 100.0)
    distance = random.randrange(min_distance, max_distance, 10.0)

    angle = np.radians(random.randrange(0.0,359.0))
    x = np.cos(angle)*distance
    y = np.sin(angle)*distance
    airplane.position = np.matrix( [ x, y, altitude, 1.0] )

def main() :

    settings_path = 'data/scengen/settings.json'
    if not os.path.exists( settings_path ) :
        raise SystemExit("Could not find scengen settings, patch checked: '{}'".format(settings_path))
    print("Loading settings...")
    with open( settings_path ) as instream :
        settings = json.loads(instream.read())
    aircraft_specs = []
    for aircraft_specs_file in settings["aircraft"] :
        with open(aircraft_specs_file) as instream :
            aircraft_specs.append(json.loads(instream.read()))
    print("Loading scenario template...")
    scen_template_path = 'data/scengen/scen_template.json'
    with open( scen_template_path ) as instream :
        scenario = json.loads(instream.read())
    print("Loading data template...")
    data_template_path = 'data/scengen/data_template.json'
    with open( data_template_path) as instream :
        s = instream.read()
        blue_data = json.loads(s)
        red_data = json.loads(s)

    args = parse_arguments()

    print("Creating folder for tag '{}'".format(args.tag))
    basedir = os.path.join('data/scenarios',args.tag)

    try :
        os.makedirs(basedir)
    except FileExistsError :
        # uh, so bad
        pass
    random.seed(args.tag)

    for i in range(args.num_instances) :
        print("Generating scenario #{}".format(i))
        blue = Agent(args.blue_callsign, aircraft_specs[0])
        blue.side=1
        blue.id = 0
        red = Agent(args.red_callsign, aircraft_specs[0])
        red.side = 2
        red.id = 1

        determine_heading(blue)
        determine_pitch(blue)
        determine_speed(blue, args.min_speed, args.max_speed)

        determine_heading(red)
        determine_pitch(red)
        determine_speed(red, args.min_speed, args.max_speed)

        determine_position(blue, args.max_distance, args.min_altitude, args.max_altitude)
        determine_position(red, args.max_distance, args.min_altitude, args.max_altitude)

        # Do not allow planes to start too close to each other (less than 200 meters)

        while np.linalg.norm(blue.position - red.position) <= 200.0 :
            determine_position(blue, args.max_distance, args.min_altitude, args.max_altitude)
            determine_position(red, args.max_distance, args.min_altitude, args.max_altitude)


        blue.sync_speed()
        blue.rotate()

        red.sync_speed()
        red.rotate()



        # We're all set then
        blue_initial_filename = os.path.join( basedir, '{:0>4d}_blue_initial.json'.format( i ) )
        red_initial_filename = os.path.join( basedir, '{:0>4d}_red_initial.json'.format( i ))
        blue.write(blue_initial_filename, blue_data)
        red.write(red_initial_filename, red_data)

        blue_sit = classify_combat_situation_1v1( blue, red )
        red_sit = classify_combat_situation_1v1( red, blue )

        for blue_agent, red_agent in itertools.permutations(settings["agents"],2) :
            scen_filename = os.path.join(basedir, 'scen_{:0>4d}_blue_{}_red_{}.json'.format(i,blue_agent["name"],red_agent["name"]))
            scen_obj = copy.deepcopy(scenario)
            scen_obj['name'] = ",".join([ '{}/{}'.format(args.tag,'scen_{:0>4d}'.format(i)), blue_agent["name"], red_agent["name"]])
            scen_obj['metadata'] = {    'blue_sit' : blue_sit,
                                        'red_sit' : red_sit }
            scen_obj["umpire"]["triggers"] = [
                    {   "class" : "umpires.triggers.MaxTimeElapsed",
                        "parameters" : { "max_time" : settings["defaults"]["sim"]["duration"] }
                    }
            ]

            blue_agent_parameters = blue_agent["args"]
            red_agent_parameters = red_agent["args"]

            if 'fsm_agent' not in blue_agent["classname"] :
                blue_agent_parameters = [ blue_initial_filename, red_initial_filename] + blue_agent_parameters

            if 'fsm_agent' not in red_agent["classname"] :
                red_agent_parameters = [ red_initial_filename, blue_initial_filename] + red_agent_parameters

            scen_obj["dt"] = settings["defaults"]["sim"]["dt"]
            scen_obj["blue"] = {    "initial" : blue_initial_filename,
                                    "agent_class" : blue_agent["classname"],
                                    "agent_parameters" : blue_agent_parameters }
            scen_obj["red"] = {    "initial" : red_initial_filename,
                                    "agent_class" : red_agent["classname"],
                                    "agent_parameters" : red_agent_parameters }

            with open(scen_filename,'w') as outstream :
                outstream.write(json.dumps(scen_obj,sort_keys=True,indent=4))

if __name__ == '__main__' :
    main()
