__author__ = 'miquelramirez'

from flight_control import FlightControl
from platform_dynamics import PlatformDynamics
import utils as ut

class AutomatedPlanningAgent(object) :

    """
    Base agent for Automated Planning agents.
    """
    def __init__(self, plant_data_source_blue, plant_data_source_red):
        self.blue_plant = self.setup_plant_instance(plant_data_source_blue)
        self.red_plant = self.setup_plant_instance(plant_data_source_red)
        self.commands = []

    def get_commands(self):
        """
        Returns the list of commands from the agent.

        Returns:
            ([object]): the list of commands
        """
        return self.commands

    def set_beliefs(self, beliefs):
        """
        Sets the beliefs of the agent and all sub-states.

        Args:
            beliefs (object): object defining the agent beliefs about the world
        """
        # update the plants according to the current values
        blue_state = beliefs.entity_state
        self.sync_plant_state( self.blue_plant, beliefs.entity_state)
        self.sync_plant_state( self.red_plant, beliefs.threat_state)

    def sync_plant_state( self, plant, state ) :
        common_attributes = ['x','y','z','psi','psi_c','theta','theta_c','phi','v','v_c']

        for attribute_name in common_attributes :
            setattr( plant.platform, attribute_name, getattr(state, attribute_name))


    def setup_plant_instance( self, datasource ) :
        import json
        if isinstance(datasource, (unicode,str)) :
            with open(datasource) as data_file:
                data = json.load(data_file)
        elif isinstance(datasource,dict) :
            data = datasource
        else :
            raise RuntimeError("Fighter data sources can only be filenames or dictionaries")

        # Convert units to SI
        if data['metric'] != 'SI' :
            data['x'] = ut.nautical_miles_to_metres(data['x'])
            data['y'] = ut.nautical_miles_to_metres(data['y'])
            data['z'] = ut.feet_to_metres(data['z'])
            data['v'] = ut.knots_to_mps(data['v'])
            data['v_min'] = ut.knots_to_mps(data['v_min'])
            data['v_max'] = ut.knots_to_mps(data['v_max'])

        platform = PlatformDynamics(**data)
        return FlightControl(platform)

    def clone_environment(self) :
        """
        Clones the current world state
        """
        from copy import deepcopy
        return (deepcopy(self.blue_plant),deepcopy(self.red_plant))

    def compute_successor(self, blue_control, red_control, T ) :
        blue_state, red_state = self.clone_environment()
        blue_control.update(blue_state)
        red_control.update(red_state)

        # Numeric integration
        dh = 0.1
        while T > 0.0 :
            h = min(T,dh)
            blue_state.tick(0.0, h)
            red_state.tick(0.0, h)
            T = T - h

        return blue_state, red_state

    def tick(self, t, dt):
        raise RuntimeError("tick(t,dt) needs to be implemented by subclasses of TwoPlayerAgent")
