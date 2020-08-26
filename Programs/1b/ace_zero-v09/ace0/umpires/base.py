"""
    Umpire base class
"""

__author__ = 'miquelramirez'

class Umpire :

    def __init__( self , simulation) :
        self.simulation = simulation
        self.termination_triggers = []
        self.performance_critics = []

    def check_termination_triggers( self  ) :
        for trigger in self.termination_triggers :
            if trigger.check(self.simulation) : return True

    def evaluate_agent_performance( self ) :
        for critic in self.performance_critics :
            critic.evaluate( self.simulation )
