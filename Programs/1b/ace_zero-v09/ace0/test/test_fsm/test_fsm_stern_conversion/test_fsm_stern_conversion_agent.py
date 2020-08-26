import os
from unittest import TestCase

import ace_zero


class TestFSMSternConversionAgent(TestCase):
    def setUp(self):
        # Change working directory to the directory of this test so paths work
        abspath = os.path.abspath(__file__)
        dname = os.path.dirname(abspath)
        os.chdir(dname)

    def test_run_default(self):
        ace_zero.run_ace_zero(scenario="scenario.json", noxcombat=True, graph=True)
