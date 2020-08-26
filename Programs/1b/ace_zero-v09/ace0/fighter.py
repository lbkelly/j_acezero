"""
Fighter Aircraft Model
"""

__author__ = 'mikepsn'

import json

import flight_control
import utils as ut
from agents.goal_agent import pilot
from platform_dynamics import PlatformDynamics
from sensor import Sensor


class Fighter(object):
    """
    The fighter aircraft class consists of two components:
    1) A pilot agent which makes the pilot decisions, and
    2) A flight control system (which is the interface to the platform dynamics model)

    Each fighter aircraft is uniquely defined by a JSON file which is passed to
    the constructor and is loaded at object instantiation.

    The tick method executes the sub-component models of the Fighter
    and ensures that the correct data gets passed between the various
    components in the correct order.

    Note in this instance there is no sensor model. Since we are dealing
    Within Visual Range (WVR) combat we make the simplifying assumption
    that each pilot can perceive their adversary at all times.
    """

    def __init__(self, datasource, pilot_agent):
        self.pilot = pilot_agent

            # Read the fighter initialisation data
        data = self.load_data(datasource)
        self.callsign = data['callsign']
        self.id = data['id']
        self.side = data['side']
        self.actype = data['actype'] if data.has_key('actype') else 0
        self.score = 0

            # Convert units to SI
        if data['metric'] != 'SI':
            data['x'] = ut.nautical_miles_to_metres(data['x'])
            data['y'] = ut.nautical_miles_to_metres(data['y'])
            data['z'] = ut.feet_to_metres(data['z'])
            data['v'] = ut.knots_to_mps(data['v'])
            data['v_min'] = ut.knots_to_mps(data['v_min'])
            data['v_max'] = ut.knots_to_mps(data['v_max'])

            # Initialise platform with params read from initialisation data
        platform = PlatformDynamics(**data)

            # Create the flight control model to handle agent commands
        self.fcs = flight_control.FlightControl(platform)

            # Create the sensor model
        sensor_name = self.callsign + "_" + "sensor"
        if 'sensor_params' in data.keys():
            sensor_max_range = ut.nautical_miles_to_metres(data['sensor_params']['sensor_max_range'])
            sensor_fov = data['sensor_params']['sensor_fov']
            self.sensor = Sensor(name=sensor_name, max_range=sensor_max_range, fov=sensor_fov)
        else:
            self.sensor = Sensor(name=sensor_name)

            # A list containing a state history of the fighter
        self.history = []

    def load_data(self, datasource):
        """ Load the data for a the specified fighter. """
        if isinstance(datasource, (unicode,str)):
            with open(datasource) as data_file:
                 return json.load(data_file)
        elif isinstance(datasource, dict) :
            return datasource
        else :
            raise RuntimeError("Fighter data sources can only be filenames or dictionaries, provided:\n{}".format(type(datasource)))

    def get_state(self):
        """
        Returns a FighterState object representing the current state of the
        fighter aircraft, including position, orientation and speed.
        """
        state = self.fcs.get_platform_state()
        state.sensor_state = self.sensor.get_state()
        state.callsign = self.callsign
        state.id = self.id
        state.side = self.side
        state.actype = self.actype
        state.score = self.score
        return state

    def update_adversary_state(self, adversary_state):
        """ Updates the seven componet tuple representing the state
            of the adversary aircraft. """
        self.adversary_state = adversary_state

    def set_mission(self, mission):
        """ Sets the pilot's current mission. """
        self.pilot.add_mission(mission)

    def tick(self, t, dt):
        """
        Ticks the fighter aircraft at a rate dt, for the current time step t.

        The method gets the state of the aircraft and it's adversary and passes
        this information to the pilot so the beliefs can be updated.

        With update beliefs, this allows the pilot to be ticked to see
        what new decisions and actions/commands the pilot will take with these updated
        beliefs.

        The resulting command the pilot generates are then passed to the flight
        control system (fcs) which is then ticked to execute these commands.

        The flight control system controls the underlying platform model which
        allows the aircraft to update its position and orientation.

        The entire process is repeated in the next time step.
        """
        my_state = self.get_state()
        my_state.timestep = t
        my_state.tracked = self.am_i_being_tracked()
        
        beliefs = pilot.PilotBeliefs(my_state, self.adversary_state)
        self.pilot.set_beliefs(beliefs)
        self.pilot.tick(t, dt)
        commands = self.pilot.get_commands()
        self.fcs.set_new_commands(commands)
        self.fcs.tick(t, dt)
        self.sensor.update_entities([self.adversary_state])
        self.sensor.update_aircraft_state(my_state)
        self.sensor.tick(t, dt)
        self.history.append(my_state)

    def am_i_being_tracked(self):
        """ Returns true if the adversary is tracking me. """
        tracked = False
        tracks = self.adversary_state.sensor_state.tracks
        callsigns = [tracks[t].callsign for t in tracks] 
        if self.callsign in callsigns:
            tracked = True 
        return tracked

    def set_score(self, value):
        setattr(self, 'score', value)
