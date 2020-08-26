"""
    Stern Conversion as Hybrid Planning
"""

__author__ = 'miquelramirez'

import json
import logging

import utils
from agents.ap_agent.automated_planning_agent import AutomatedPlanningAgent

PLANNER_DIR = '/home/bowman/Sandboxes/fs-plus-new/generated/testing/stern_conversion_level_4/standard'

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
        attributes = ['name', 'theta_c', 'psi_c', 'v_c', 'z_c', 'commands', 'control']
        for attrib in attributes :
            setattr( m, attrib, datasource[attrib] )
        m.transitions = {}
        for entry in datasource["transitions"] :
            m.transitions[entry[0]] = entry[1]
        return m


class SternConversionAgent(AutomatedPlanningAgent):

    def __init__(self, maneuver_specs):
        # Set up logging
        self.logger = logging.getLogger("FS+ (Stern Conversion)")
        self.logger.setLevel(logging.DEBUG)
        ch = logging.FileHandler( 'fs_plus_stern_conversion.log', mode='w')
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        self.load_variable_schema()

        self.yaw_control_state = "straight"
        self.pitch_control_state = "level"
        self.speed_control_state = "cruising"
        self.current_maneuver = None

        # Load the manoeuvres and plant data sources from the specs file
        with open(maneuver_specs) as instream:
            data = json.load(instream)
            super(SternConversionAgent, self).__init__(
                data['plant_data_source_blue'], data['plant_data_source_red'])
            self.maneuvers = self.setup_maneuvers(data)

    def setup_maneuvers(self, data):
        maneuvers = {}
        for maneuver_data in data['maneuvers']:
            m = Maneuver.load(maneuver_data)
            maneuvers[m.name] = m
        self.logger.debug("Loaded {} maneuvers from '{}'".format(
                len(maneuvers), data))
        return maneuvers

    def load_variable_schema(self ) :
        import os
        self.vars = {}
        self.values = {}
        self.problem = None
        with open( os.path.join(PLANNER_DIR, 'data/problem.json') )  as instream :
            self.problem = json.load(instream)
        for variable in self.problem["variables"] :
            init_index = None
            for i in range(len(self.problem["init"]["atoms"])) :
                if self.problem["init"]["atoms"][i][0] == variable["id"] :
                    init_index = i
                    break
            self.vars[variable["name"]] = (variable["id"], init_index)
        for object_def in self.problem["objects"] :
            self.values[object_def["name"]] = object_def["id"]

    def update_initial_state(self) :
        import os
        # Update blue plant state
        self.problem["init"]["atoms"][self.vars["x(blue)"][1]][1] = self.blue_plant.platform.x
        self.problem["init"]["atoms"][self.vars["y(blue)"][1]][1] = self.blue_plant.platform.y
        self.problem["init"]["atoms"][self.vars["z(blue)"][1]][1] = self.blue_plant.platform.z
        self.problem["init"]["atoms"][self.vars["v(blue)"][1]][1] = self.blue_plant.platform.v
        self.problem["init"]["atoms"][self.vars["psi(blue)"][1]][1] = self.blue_plant.platform.psi
        self.problem["init"]["atoms"][self.vars["theta(blue)"][1]][1] = self.blue_plant.platform.theta
        self.problem["init"]["atoms"][self.vars["speed_control_state(blue)"][1]][1] = self.values[self.speed_control_state]
        self.problem["init"]["atoms"][self.vars["yaw_control_state(blue)"][1]][1] = self.values[self.yaw_control_state]
        self.problem["init"]["atoms"][self.vars["pitch_control_state(blue)"][1]][1] = self.values[self.pitch_control_state]
        #self.problem["init"]["atoms"][self.vars["phi(blue)"][1]][1] = self.blue_plant.platform.phi
        self.logger.debug('Updating initial state to:')
        self.logger.debug('\tx(blue)={}'.format(self.blue_plant.platform.x))
        self.logger.debug('\ty(blue)={}'.format(self.blue_plant.platform.y))
        self.logger.debug('\tz(blue)={}'.format(self.blue_plant.platform.z))
        self.logger.debug('\tv(blue)={}'.format(self.blue_plant.platform.v))
        self.logger.debug('\tpsi(blue)={}'.format(self.blue_plant.platform.psi))
        self.logger.debug('\ttheta(blue)={}'.format(self.blue_plant.platform.theta))
        self.logger.debug('\tspeed_control_state(blue)={}'.format(self.speed_control_state))
        self.logger.debug('\tyaw_control_state(blue)={}'.format(self.yaw_control_state))
        self.logger.debug('\tpitch_control_state(blue)={}'.format(self.pitch_control_state))

        # Update red plant state
        self.problem["init"]["atoms"][self.vars["x(red)"][1]][1] = self.red_plant.platform.x
        self.problem["init"]["atoms"][self.vars["y(red)"][1]][1] = self.red_plant.platform.y
        self.problem["init"]["atoms"][self.vars["z(red)"][1]][1] = self.red_plant.platform.z
        self.problem["init"]["atoms"][self.vars["v(red)"][1]][1] = self.red_plant.platform.v
        self.problem["init"]["atoms"][self.vars["psi(red)"][1]][1] = self.red_plant.platform.psi
        self.problem["init"]["atoms"][self.vars["theta(red)"][1]][1] = self.red_plant.platform.theta
        #self.problem["init"]["atoms"][self.vars["phi(red)"][1]][1] = self.red_plant.platform.phi
        self.logger.debug('\tx(red)={}'.format(self.red_plant.platform.x))
        self.logger.debug('\ty(red)={}'.format(self.red_plant.platform.y))
        self.logger.debug('\tz(red)={}'.format(self.red_plant.platform.z))
        self.logger.debug('\tv(red)={}'.format(self.red_plant.platform.v))
        self.logger.debug('\tpsi(red)={}'.format(self.red_plant.platform.psi))
        self.logger.debug('\ttheta(red)={}'.format(self.red_plant.platform.theta))

        with open( os.path.join(PLANNER_DIR, 'data/problem.json'), 'w' ) as outstream :
            json.dump(self.problem, outstream, sort_keys=True, indent=1)

    def invoke_planner(self) :
        import os
        planner_cmd = './solver.bin -s 0.5 -H 1'
        current = os.getcwd()
        os.chdir( PLANNER_DIR )
        os.system( planner_cmd )
        os.chdir(current)

        with open( os.path.join(PLANNER_DIR, 'results.json') )  as instream :
            self.planner_result = json.load(instream)


    def make_commands_from_plan( self, plant ) :
        executable_entries = []
        self.logger.debug("Plan:")
        for entry in self.planner_result["plan"] :
            self.logger.debug(entry)
            if float(entry["time"]) < 0.01 :
                executable_entries.append(entry)
        self.logger.debug("{} actions in the plan out of {} can be executed".format(len(executable_entries),len(self.planner_result["plan"])))

        command_list = []
        for entry in executable_entries :
            try :
                self.current_maneuver = self.maneuvers[entry["action"]]
            except KeyError :
                continue
            command_list += self.current_maneuver.make_commands( plant )
            # determine what control state needs to be updated
            attrib_name = '{}_control_state'.format(self.current_maneuver.control)
            old_value = getattr(self, attrib_name)
            next_value = self.current_maneuver.transitions[old_value]
            setattr( self, attrib_name, next_value)
            self.logger.debug('Control state transition: {}, {} -> {}'.format(self.current_maneuver.control, old_value, next_value))



        return command_list

    def tick( self, t, dt ) :
        self.logger.debug('\n Empty plan')
        self.update_initial_state()
        self.invoke_planner()

        self.commands = self.make_commands_from_plan( self.blue_plant )
