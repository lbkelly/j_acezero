#!/usr/env/ python

"""
Multi-agent simulation of two fighter aircraft in a 1v1 configuration.
"""

__author__ = 'mikepsn, lrbenke'

import importlib
import os

import fighter
from agents.agent import Agent
from umpires.base import Umpire
from utils import find_data_file

class MultiAgentSimulationDefault(object):
    """
    A simple time stepped multi-agent simulation consisting of two fighter
    aircraft in a 1v1 adversarial Within Visual Range (WVR) air combat scenario.

    The simulation is defined by a json file that specifies the initial
    conditions and agents for the fighters in the scenario.
    """

    def __init__(self, scenario=None):
        """
        Initialises the start and end time for the simulation as well
        as the tick rate. Instantiates two fighter aircraft, viper (blue) and
        cobra (red).
        """
        self.umpire = None
        self.current_time = 0

        if not scenario:
            scenario = self.default_scenario()

        self.setup(scenario)

    def setup(self, scenario):
        """
        Loads the simulation, entity and agent parameters from the specified
        scenario dictionary, and initialises two fighter entities for execution.

        Args:
            scenario (dict): dictionary specifying a scenario
        """
        # Load the simulation parameters
        self.tmin = scenario['tmin']
        self.dt = scenario['dt']

        # Create the blue fighter 'viper'
        initial = scenario['blue']['initial']
        agent_class = scenario['blue']['agent_class']
        agent_params = scenario['blue']['agent_parameters']
        self.viper = self.get_fighter(initial, agent_class, agent_params)

        # Create the red fighter 'cobra'
        initial = scenario['red']['initial']
        agent_class = scenario['red']['agent_class']
        agent_params = scenario['red']['agent_parameters']
        self.cobra = self.get_fighter(initial, agent_class, agent_params)

        # Setup the Umpire
        self.umpire = self.get_umpire( scenario['umpire'], self )

    def run(self):
        """
        Runs the simulation until the maximum run time self.tmax is reached.
        """
        self.current_time = self.tmin
        while not self.umpire.check_termination_triggers():
            self.tick(self.current_time, self.dt)
            self.current_time += self.dt
            self.umpire.evaluate_agent_performance()

    def tick(self, t, dt):
        """
        Ticks each fighter aircraft.
        Gets the current state of each fighter and then passes each state to the
        opponent aircraft. Once this is done, each aircraft is then ticked.
        """
        viper_state = self.viper.get_state()
        cobra_state = self.cobra.get_state()

        self.viper.update_adversary_state(cobra_state)
        self.cobra.update_adversary_state(viper_state)

        self.viper.tick(t, dt)
        self.cobra.tick(t, dt)

    @staticmethod
    def get_fighter(initial, agent_class, agent_params):
        """
        Creates a Fighter with the specified initial conditions and agent.

        Args:
            initial (string): path to the json file specifying the initial
              conditions for the fighter
            agent_class (string): qualified name of the class of the agent
            agent_params (string): path to the json file specifying any
              parameters required by the agent

        Returns:
            (Fighter): an initialised fighter entity
        """
        AgentClass = get_class(agent_class)
        if not issubclass(AgentClass, Agent):
            # TODO: replace with logger warning
            print("Warning: Agent class specified in scenario is not a " +
                    "subclass of Agent '" + agent_class + "'")
        pilot = AgentClass(params_filename=agent_params)
        assert pilot is not None
        return fighter.Fighter(initial, pilot)

    @staticmethod
    def get_umpire( umpire_specs, sim ) :
        umpire = Umpire(sim)

        for trigger_specs in umpire_specs['triggers'] :
            TriggerClass = get_class( trigger_specs['class'] )
            trigger = TriggerClass(**trigger_specs['parameters'])
            umpire.termination_triggers.append( trigger )

        for critic_specs in umpire_specs['critics'] :
            CriticClass = get_class( critic_specs['class'])
            critic = CriticClass( **critic_specs['parameters'])
            umpire.performance_critics.append( critic )

        return umpire

    @staticmethod
    def default_scenario():
        return {'name': 'default',
                'tmin': 0.0,
                'umpire' : {
                        'triggers' : [
                                {   'class' : 'umpires.triggers.MaxTimeElapsed',
                                    'parameters' : { "max_time" : 250.0 }
                                }
                            ],
                        "critics" : [
                                {
                                    "class" : "umpires.critics.GunScore",
                                    "parameters" : {    "name" : "Viper Gun Score",
                                                        "subject" : "viper",
                                                        "object" : "cobra",
                                                        "min_range" : 500,
                                                        "max_range" : 3000.0,
                                                        "max_altitude": 500,
                                                        "max_speed": 100,
                                                        "max_angle" : 30.0 }
                                },
                                {
                                    "class" : "umpires.critics.GunScore",
                                    "parameters" : {    "name" : "Cobra Gun Score",
                                                        "subject" : "cobra",
                                                        "object" : "viper",
                                                        "min_range" : 500,
                                                        "max_range" : 3000.0,
                                                        "max_altitude": 500,
                                                        "max_speed": 100,
                                                        "max_angle" : 30.0 }
                                }
                        ]
                },
                'dt': 0.1,
                # Basic Park ECU agent for transition evolution experiments
                # 'blue': {
                #     'initial': os.path.dirname(__file__) + r"\data\blue.json",
                #     'agent_class': 'agents.fsm_agent.ecu_stern_basic.EcuSternBasicAgent',
                #     'agent_parameters': os.path.dirname(__file__) + r"\data\ecu_basic_blue_tactics.json"},

                # ECU stern agent for transition evolution experiments
                # 'blue': {
                #     'initial': os.path.dirname(__file__) + r"\data\blue.json",
                #     'agent_class': 'agents.fsm_agent.ecu_stern_conversion.EcuSternConversionAgent',
                #     'agent_parameters': os.path.dirname(__file__) + r"\data\ecu_blue_tactics.json"},

                # Park ECU pure pursuit hardcoded agent
                # 'blue': {
                #     'initial': os.path.dirname(__file__) + r"\data\blue.json",
                #     'agent_class': 'agents.fsm_agent.park_ecu_pure.ParkEcuPure',
                #     'agent_parameters': None},

                # ROUND THREE
                'blue': {
                    'initial': find_data_file("blue.json"),
                    'agent_class': 'agents.fsm_agent.ecu_stern_basic.EcuSternBasicAgent',
                    'agent_parameters': find_data_file("blue_tactics.json")},

                # ECU states
                # 'blue': {
                #     'initial': os.path.dirname(__file__) + r"\data\blue.json",
                #     'agent_class': 'agents.fsm_agent.ecu_stern_conversion.EcuSternConversionAgent',
                #     'agent_parameters': os.path.dirname(__file__) + r"\data\blue_tactics.json"},

                # Default DSTG stern agent
                # 'blue': {
                #     'initial': os.path.dirname(__file__) + r"\data\blue.json",
                #     'agent_class': 'agents.fsm_agent.stern_conversion.SternConversionAgent',
                #     'agent_parameters': os.path.dirname(__file__) + r"\data\blue_tactics.json"},

                # Default red
                # 'red': {'initial': os.path.dirname(__file__) + r"\data\red.json",
                #         'agent_class': 'agents.fsm_agent.stern_conversion_default.SternConversionAgentDefault', #'agents.agent.Agent',
                #         'agent_parameters': os.path.dirname(__file__) + r"\data\red_tactics.json"}}

                # 'blue': {
                #     # 'initial': os.path.dirname(__file__) + r"\data\blue.json",
                #     # 'initial': os.path.dirname(sys.executable) + r"\blue.json",
                #     'initial': find_data_file("blue.json"),
                #     'agent_class': 'agents.fsm_agent.ecu_stern_conversion.EcuSternConversionAgent',
                #     # 'agent_parameters': os.path.dirname(__file__) + r"\data\blue_tactics.json"},
                #     'agent_parameters': find_data_file("blue_tactics.json")},

                # # Straight red
                'red': {
                    # {'initial': os.path.dirname(__file__) + r"\data\red.json",
                    'initial': find_data_file("red.json"),
                    'agent_class': 'agents.fsm_agent.stern_conversion.SternConversionAgent',
                    # 'agents.agent.Agent',
                    # 'agent_parameters': os.path.dirname(__file__) + r"\data\red_tactics.json"}}
                    'agent_parameters': find_data_file("red_tactics.json")}}

                # # Default DSTG stern agent
                # 'blue': {
                #     'initial': os.path.dirname(__file__) + r"\data\blue - default.json",
                #     'agent_class': 'agents.fsm_agent.stern_conversion.SternConversionAgent',
                #     'agent_parameters': os.path.dirname(__file__) + r"\data\red_tactics.json"}},
                #
                # Default Straight red
                # 'red': {'initial': os.path.dirname(__file__) + r"\data\red - default.json",
                #         'agent_class': 'agents.agent.Agent',
                #         'agent_parameters': None}}



                # Default stern red
                # 'red': {'initial': os.path.dirname(__file__) + r"\data\red.json",
                #         'agent_class': 'agents.fsm_agent.stern_conversion.SternConversionAgent',
                #          'agent_parameters': os.path.dirname(__file__) + r"\data\blue_tactics - Copy.json"}}

                # Pure pursuit red
                # 'red': {'initial': os.path.dirname(__file__) + r"\data\red.json",
                #         'agent_class': 'agents.fsm_agent.pursuit.PurePursuitAgent',
                #          'agent_parameters': None}}

                # ECU evolved stern red
                # 'red': {'initial': os.path.dirname(__file__) + r"\data\red.json",
                #          'agent_class': 'agents.fsm_agent.ecu_stern_conversion.EcuSternConversionAgent',
                #          'agent_parameters': os.path.dirname(__file__) + r"\data\ecu_blue_tactics - Copy.json"} }


def get_class(class_path):
    """  Returns a class given its full path (packages.module.class). """
    module_name, class_name = class_path.rsplit(".", 1)
    try:
        ImportedClass = getattr(importlib.import_module(module_name), class_name)
        return ImportedClass
    except ImportError:
        # TODO: replace with logger fatal
        print("Fatal: Agent class specified in scenario could not be imported '"
                + class_path + "'")
        raise
