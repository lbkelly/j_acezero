""" This module contains classes required to implement an agent that uses a
hierarchical finite state machine to represent decision making. """

from agents.agent import Agent
import inspect
from collections import OrderedDict


__author__ = 'lrbenke'


class StateAgent(Agent):
    """
    Base class for agents implemented using a Finite State Machine.

    Objects of this class may contain child states, or be 'leaf' states that
    execute behaviour and process state transitions.

    Attributes:
        beliefs (Beliefs): the current agent beliefs about the world
        commands ([Command]): list of Commands from this agent and any children
        states ({class: StateAgent}): dict of child state objects by class
        params_filename (str): path to file specifying any agent parameters
        active_states ([StateAgent]): the list of states currently being
                executed by the agent
        transition_request (class): class of the state to transition into from
                this state
    """

    def __init__(self, states=[], params_filename=None, initial=None,
                 auto_initial=True):
        """
        Constructor.

        Args:
            states ([StateAgent]): list of states for this agent
            initial (class | [class]): the class/es of the initial state/s of
                    the agent (overrides auto_initial)
            auto_initial (bool): if true the initial active state is set to the
                    first state in the list
        """
        self.beliefs = None
        self.commands = []
        self.states = OrderedDict([[type(state), state] for state in states])
        self.active_states = []
        self.transition_request = None

        # Set the initial state/s of the agent
        if initial:
            if type(initial) is not list:
                initial = [initial]
            for state in initial:
                self.add_active_state(state)
        elif auto_initial and len(states) > 0:
            self.add_active_state(type(states[0]))

    def tick(self, t, dt):
        """
        Ticks the StateAgent.

        This method calls the process_state and _execute methods.

        Args:
            t (int): current simulation time
            dt (float): change in time from previous tick
        """
        self.process_state(t, dt)
        self.execute(t, dt)

    def process_state(self, t, dt):
        """
        Processes state transitions.

        The default implementation calls the process_state method in the current
        state, then checks whether a transition is requested and updates the
        current state accordingly.

        Child states should extend this method to implement state change
        logic. State transitions should only be requested in this method, by
        setting the transition_request attribute.

        Args:
            t (int): current simulation time
            dt (float): change in time from previous tick
        """
        # Clear any state transition request from the previous tick
        self.transition_request = None

        # Iterate over a copy of the active states list so we can modify it
        active_states_copy = list(self.active_states)
        for state in active_states_copy:
            # Propagate state processing to the child state
            state.process_state(t, dt)

            # Process any transition requests by replacing the child state
            if state.transition_request:
                new_state = self.get_state(state.transition_request)
                self.remove_active_state(type(state))
                self.add_active_state(new_state)

    def execute(self, t, dt):
        """
        Executes the state behaviour.

        The default implementation clears the commands list then propagates
        execution to the current state by calling its execute method and
        retrieving any commands.

        Child agents should extend this method to carry out actions associated
        with the state behaviour. Commands should only be issued from this
        method, to ensure that they are not cleared during execution.

        Args:
            t (int): current simulation time
            dt (float): change in time from previous tick
        """
        # Clear any commands from the previous tick
        self.commands = []

        for state in self.active_states:
            state.execute(t, dt)
            self.commands.extend(state.commands)

    def on_entry(self):
        """ Called when the state is entered. """
        pass

    def on_exit(self):
        """ Called when the state is entered. """
        pass

    def add_active_state(self, state):
        """ Adds a state to the list of active states. """
        if inspect.isclass(state):
            state = self.get_state(state)

        self.active_states.append(state)
        state.on_entry()

    def remove_active_state(self, state):
        """ Removes the state with the given class from the active states. """
        if inspect.isclass(state):
            state = self.get_state(state)

        state.on_exit()
        self.active_states.remove(state)

    def get_state(self, state):
        """ Returns the state with the given class. """
        return self.states[state]

    def state_names(self):
        """ Returns a list of the names of the agent states. """
        return [x.__name__ for x in self.states.keys()]

    def set_beliefs(self, beliefs):
        """
        Sets the beliefs of the agent and all sub-states.

        Args:
            beliefs (object): object defining the agent beliefs about the world
        """
        self.beliefs = beliefs
        for state in self.states.values():
            state.set_beliefs(beliefs)

    def get_commands(self):
        """
        Returns the list of commands from the agent and any active sub-states.

        Returns:
            ([object]): the list of commands; may be empty
        """
        return self.commands
