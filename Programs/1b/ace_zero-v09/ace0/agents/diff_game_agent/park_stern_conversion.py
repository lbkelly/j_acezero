"""
Implementation of the techniques discussed in the paper:

 Differential Game Based Air Combat Maneuver Generation Using Scoring Function Matrix
 H. Park, B.-Y. Lee, M.-J. Tahk, D.-W. Yoo
 International Journal of Aeronautical and Space Sciences, number 17, vol 2, pages 204-213
 2016
"""

__author__ = 'miquelramirez'

import json
import logging

import numpy as np

import utils
from agents.diff_game_agent.two_player_agent import TwoPlayerAgent


class Maneuver :

    def __init__(self) :
        self.name = None
        self.theta_c = 0.0
        self.psi_c = 0.0
        self.v_c = 0.0
        self.z_c = 0.0
        self.commands = []

    def make_commands(self, plant) :
        import commands

        cmd_list = []
        theta_c = utils.constrain_360(plant.platform.theta + self.theta_c)
        psi_c = utils.constrain_360(plant.platform.psi + self.psi_c)
        v_c = plant.platform.v + self.v_c
        z_c = plant.platform.z + self.z_c
        for cmd in self.commands :
            cmd_class = getattr(commands, cmd)
            values = []
            for a in cmd_class._fields :
                values.append(locals()[a])
            cmd_instance = cmd_class._make(values)
            cmd_list.append(cmd_instance)
        return cmd_list

    def update( self, plant ) :
        plant.set_new_commands(self.make_commands(plant))

    @staticmethod
    def load( datasource ) :
        m = Maneuver()
        attributes = ['name', 'theta_c', 'psi_c', 'v_c', 'z_c', 'commands']
        for attrib in attributes :
            setattr( m, attrib, datasource[attrib] )
        return m


class SternConversionAgent(TwoPlayerAgent):

    def __init__(self, maneuver_specs):
        # Set up logging
        self.logger = logging.getLogger("Park's Stern Conversion")
        self.logger.setLevel(logging.DEBUG)
        ch = logging.FileHandler( 'park_stern_conversion.log', mode='w')
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

        # Load the manoeuvres and plant data sources from the specs file
        with open(maneuver_specs) as instream:
            data = json.load(instream)
            super(SternConversionAgent, self).__init__(
                data['plant_data_source_blue'], data['plant_data_source_red'])
            self.maneuvers = self.setup_maneuvers(data)

    def setup_maneuvers(self, data):
        maneuvers = []
        for maneuver_data in data['maneuvers']:
            maneuvers.append(Maneuver.load(maneuver_data))
        self.logger.debug("Loaded {} maneuvers from '{}'".format(
                len(maneuvers), data))
        return maneuvers

    def compute_aspect_angle( self, blue_plant, red_plant ) :
        return utils.get_aspect_angle( blue_plant.platform, red_plant.platform )

    def compute_bearing_angle( self, blue_plant, red_plant ) :
        return utils.get_bearing_angle( blue_plant.platform, red_plant.platform )

    def compute_orientation_score( self, blue_plant, red_plant ) :
        aspect_angle = self.compute_aspect_angle(red_plant,blue_plant)
        assert aspect_angle > 0.0
        assert aspect_angle <= 360.0
        return (360.0 - (blue_plant.platform.psi + aspect_angle))/180.0

    def compute_range_error_score( self, blue_plant, red_plant ) :
        distance_to_red = utils.get_range( blue_plant.platform, red_plant.platform )
        # Safety distance is set to 500m
        engagement_range = distance_to_red - 500.0
        # "Optimal" range is set to 800m
        return 1.0 - np.exp( -1.0*np.power(engagement_range - 800.0,2.0) )

    def compute_velocity_error_score( self, blue_plant, red_plant ) :
        return np.absolute((red_plant.platform.v-blue_plant.platform.v)/blue_plant.platform.v)

    def evaluate_scoring_function( self, state, tactical_situation ) :
        blue_plant, red_plant = state
        # Normalising factor for orientation score is 2.0
        orientation_score = self.compute_orientation_score(blue_plant,red_plant) / 2.0
        range_error_score = self.compute_range_error_score(blue_plant,red_plant)
        velocity_error_score = self.compute_velocity_error_score(blue_plant,red_plant)
        if tactical_situation in ('NEUTRAL', 'DEFENSIVE', 'HEAD-ON') :
            return orientation_score - velocity_error_score
        if tactical_situation in ('NEEDS-TO-CLOSE') :
            return range_error_score
        assert tactical_situation == 'OFFENSIVE'
        return orientation_score + range_error_score

    def populate_scoring_matrix( self ) :
        matrix_shape= ( len(self.maneuvers), len(self.maneuvers) )
        self.scoring_matrix = np.zeros(matrix_shape)
        for i in range(len(self.maneuvers)) :
            for j in range(len(self.maneuvers)) :
                end_state = self.compute_successor( self.maneuvers[i], self.maneuvers[j], 1.0)
                tactical_situation = self.classify_tactical_situation(end_state)
                self.scoring_matrix[i,j] = self.evaluate_scoring_function(end_state,tactical_situation)

    def classify_tactical_situation( self, state ) :
        blue_plant, red_plant = state
        aspect_angle = self.compute_aspect_angle(red_plant, blue_plant)
        bearing_angle = self.compute_bearing_angle( blue_plant, red_plant)
        blue_pos = np.matrix([blue_plant.platform.x,blue_plant.platform.y,blue_plant.platform.z])
        red_pos = np.matrix([red_plant.platform.x,red_plant.platform.y,red_plant.platform.z])
        separation_vector = blue_pos - red_pos
        distance_to_red = np.linalg.norm(separation_vector)
        if distance_to_red > 2000.0 :
            return 'NEEDS-TO-CLOSE'
        if bearing_angle > 90.0 :
            if aspect_angle < 90.0 :
                return 'NEUTRAL'
            else :
                return 'DEFENSIVE'
        else :
            if aspect_angle < 90.0 :
                return 'OFFENSIVE'
            else :
                if bearing_angle < 45.0 :
                    if aspect_angle > 135.0 :
                        return 'HEAD-ON'
                return 'OFFENSIVE'
        assert False

    def tick( self, t, dt ) :
        situation = self.classify_tactical_situation((self.blue_plant, self.red_plant))
        self.logger.debug('\n Tactical Situation Assesment: {}'.format(situation))
        self.populate_scoring_matrix()
        red_best = None
        min_score = float('inf')
        for i in range(len(self.maneuvers)) :
            for j in range(len(self.maneuvers)) :
                if min_score > self.scoring_matrix[i,j] :
                    min_score = self.scoring_matrix[i,j]
                    red_best = j
        blue_best = None
        max_score = float('-inf')
        for i in range(len(self.maneuvers)) :
            if max_score < self.scoring_matrix[i,red_best] :
                max_score = self.scoring_matrix[i,red_best]
                blue_best = i
        self.logger.debug("\nManeuver chosen for t={} is {}, score was {}".format(t, self.maneuvers[blue_best].name, max_score ))
        self.commands = self.maneuvers[blue_best].make_commands(self.blue_plant)
