from unittest import TestCase
import os
from agents.fsm_agent.state_agent import StateAgent


class TestFSMAgent(TestCase):
    def setUp(self):
        # Change working directory to the directory of this test so paths work
        abspath = os.path.abspath(__file__)
        dname = os.path.dirname(abspath)
        os.chdir(dname)

    def test_default_fsm(self):
        """ Tests that the agent can be initialised. """
        agent = StateAgent()

    def test_state_initialisation(self):
        """ Tests that states are correctly stored and initialised. """
        class State1(StateAgent):
            pass

        class State2(StateAgent):
            pass

        class State3(StateAgent):
            pass

        state1 = State1()
        state2 = State2()
        state3 = State3()

        # Test that the default initial active states list is empty if
        # auto_initial is False and no initial state is specified
        agent = StateAgent([state3, state1, state2], auto_initial=False)
        self.assertEqual(agent.state_names(), ["State3", "State1", "State2"])
        self.assertEqual(agent.active_states, [])

        # Test that the default initial active state is the first state in the
        # list if auto_initial is True
        agent = StateAgent([state3, state1, state2])
        self.assertEqual(agent.state_names(), ["State3", "State1", "State2"])
        self.assertEqual(agent.active_states, [state3])

        # Test that the initial active state can be set explicitly
        agent = StateAgent([state3, state1, state2], initial=State1)
        self.assertEqual(agent.state_names(), ["State3", "State1", "State2"])
        self.assertEqual(agent.active_states, [state1])

        # Test that multiple initial states may be set
        agent = StateAgent([state3, state1, state2], initial=[State1, State2])
        self.assertEqual(agent.state_names(), ["State3", "State1", "State2"])
        self.assertItemsEqual(agent.active_states, [state1, state2])

    def test_single_transition_single_active_state(self):
        """ Tests that states can request transitions successfully. """
        class State1(StateAgent):
            def process_state(self, t, dt):
                StateAgent.process_state(self, t, dt)
                self.transition_request = State3

        class State2(StateAgent):
            def process_state(self, t, dt):
                StateAgent.process_state(self, t, dt)
                self.transition_request = State1

        class State3(StateAgent):
            def process_state(self, t, dt):
                StateAgent.process_state(self, t, dt)
                self.transition_request = State2

        state1 = State1()
        state2 = State2()
        state3 = State3()

        agent = StateAgent([state2, state3, state1])
        self.assertEqual(agent.active_states, [state2])

        # Trigger transition request in State2 then check transition to State1
        agent.process_state(0, 0)
        self.assertEqual(agent.active_states, [state1])

        # Trigger transition request in State1 then check transition to State3
        agent.process_state(0, 0)
        self.assertEqual(agent.active_states, [state3])

        # Trigger transition request in State3 then check transition to State2
        agent.process_state(0, 0)
        self.assertEqual(agent.active_states, [state2])

        # Trigger another transition request in State2
        agent.process_state(0, 0)
        self.assertEqual(agent.active_states, [state1])

    def test_single_transition_multiple_active_states(self):
        """ Tests that a single transition is executed when there are multiple
        active states. """
        class State1(StateAgent):
            def process_state(self, t, dt):
                StateAgent.process_state(self, t, dt)
                self.transition_request = State3

        class State2(StateAgent):
            pass

        class State3(StateAgent):
            def process_state(self, t, dt):
                StateAgent.process_state(self, t, dt)
                self.transition_request = State1

        state1 = State1()
        state2 = State2()
        state3 = State3()

        agent = StateAgent([state1, state3, state2], initial=[State1, State2])
        self.assertItemsEqual(agent.active_states, [state1, state2])

        # Trigger transition request in State1 then check transition to State3
        agent.process_state(0, 0)
        self.assertItemsEqual(agent.active_states, [state2, state3])

        # Trigger transition request in State3 then check transition to State1
        agent.process_state(0, 0)
        self.assertItemsEqual(agent.active_states, [state2, state1])

    def test_multiple_transitions(self):
        """ Tests that multiple transitions can be executed at once. """
        class State1(StateAgent):
            def process_state(self, t, dt):
                StateAgent.process_state(self, t, dt)
                self.transition_request = State2

        class State2(StateAgent):
            def process_state(self, t, dt):
                StateAgent.process_state(self, t, dt)
                self.transition_request = State3

        class State3(StateAgent):
            def process_state(self, t, dt):
                StateAgent.process_state(self, t, dt)
                self.transition_request = State4

        class State4(StateAgent):
            def process_state(self, t, dt):
                StateAgent.process_state(self, t, dt)
                self.transition_request = State1

        state1 = State1()
        state2 = State2()
        state3 = State3()
        state4 = State4()

        agent = StateAgent([state1, state3, state2, state4],
                initial=[State1, State3])
        self.assertItemsEqual(agent.active_states, [state1, state3])

        # Trigger transition request in both State1 and State3
        agent.process_state(0, 0)
        self.assertItemsEqual(agent.active_states, [state2, state4])

        # Trigger transition request in State2 and State4 and check transition
        agent.process_state(0, 0)
        self.assertItemsEqual(agent.active_states, [state1, state3])

    def test_execution(self):
        """ Test that state behaviour is executed for a single active state. """
        class State1(StateAgent):
            def execute(self, t, dt):
                StateAgent.execute(self, t, dt)
                self.test_execution_value += 1
        state1 = State1()
        state1.test_execution_value = 0
        agent = StateAgent([state1], initial=State1)
        self.assertEqual(agent.state_names(), ["State1"])
        self.assertEqual(agent.active_states, [state1])

        # Execute the active state then test that the value was updated
        self.assertEqual(state1.test_execution_value, 0)
        agent.execute(0, 0)
        self.assertEqual(state1.test_execution_value, 1)
        agent.execute(0, 0)
        self.assertEqual(state1.test_execution_value, 2)
        agent.execute(0, 0)
        self.assertEqual(state1.test_execution_value, 3)

    def test_execution_multiple_active_states(self):
        """ Test that state behaviour is executed correctly for multiple active
        states. """
        class State1(StateAgent):
            def execute(self, t, dt):
                StateAgent.execute(self, t, dt)
                self.test_execution_value += 5

        class State2(StateAgent):
            def execute(self, t, dt):
                StateAgent.execute(self, t, dt)
                self.test_execution_value += 15

        class State3(StateAgent):
            def execute(self, t, dt):
                StateAgent.execute(self, t, dt)
                self.test_execution_value += 100

        state1 = State1()
        state1.test_execution_value = 10
        state2 = State2()
        state2.test_execution_value = 20
        state3 = State3()
        state3.test_execution_value = 30

        agent = StateAgent([state1, state3, state2],
                           initial=[State1, State2, State3])
        self.assertItemsEqual(agent.active_states, [state1, state2, state3])

        # Execute active states then test that values were updated
        self.assertEqual(state1.test_execution_value, 10)
        self.assertEqual(state2.test_execution_value, 20)
        self.assertEqual(state3.test_execution_value, 30)
        agent.execute(0, 0)
        self.assertEqual(state1.test_execution_value, 15)
        self.assertEqual(state2.test_execution_value, 35)
        self.assertEqual(state3.test_execution_value, 130)
        agent.execute(0, 0)
        self.assertEqual(state1.test_execution_value, 20)
        self.assertEqual(state2.test_execution_value, 50)
        self.assertEqual(state3.test_execution_value, 230)
