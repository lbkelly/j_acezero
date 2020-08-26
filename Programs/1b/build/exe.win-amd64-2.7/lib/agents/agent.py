""" Module containing classes required to implement agent models for the
simulation. """

__author__ = 'lrbenke'


class Agent(object):
    """
    Base class for all agents.

    This class defines the interface expected by the simulation engine when
    instantiating and executing agents. All agent implementations should
    extend this class.

    Attributes:
        beliefs (Beliefs): object defining the agent beliefs about the world
        commands ([Command]): list of Commands from this agent
    """

    def __init__(self, params_filename=None):
        """
        Constructor.

        The default implementation creates the beliefs and commands attributes
        of the agent. It may be overridden or extended to provide additional
        functionality.

        Args:
            params_filename (string): optional path to agent parameters file
        """
        self.beliefs = None
        self.commands = []

    def tick(self, t, dt):
        """
        Ticks the StateAgent.

        This method is called by the simulation engine during execution to
        advance the agent a single time-step. It may be overridden to
        implement agent behaviour.

        Args:
            t (int): current simulation time
            dt (float): change in time from previous tick
        """
        pass

    def set_beliefs(self, beliefs):
        """
        Sets the percepts of the agent.

        This method is called by the simulation engine during execution, to
        update the agent with the current state of physical models in its
        associated entity. The default implementation sets the beliefs attribute
        of the agent. It may be extended or overridden to provide additional
        functionality.

        Args:
            beliefs (object): object defining the agent beliefs about the world
        """
        self.beliefs = beliefs

    def get_commands(self):
        """
        Returns the current list of commands from the agent.

        This method is called by the simulation engine during execution to
        retrieve commands from the agent for other agents or for physical models
        in its associated entity. The default implementation returns the
        commands attribute of the agent. It may be extended or overridden to
        provide additional functionality.

        Returns:
            ([object]): the list of commands; may be empty
        """
        return self.commands
