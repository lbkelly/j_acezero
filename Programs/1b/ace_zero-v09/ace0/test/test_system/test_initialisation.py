from unittest import TestCase
import ace_zero
import os


class TestInitialisation(TestCase):
    """ Test ACE Zero initialisation including argument handling. """

    def setUp(self):
        # Change working directory to the directory of this test so paths work
        abspath = os.path.abspath(__file__)
        dname = os.path.dirname(abspath)
        os.chdir(dname)

    def test_default_arguments(self):
        """ Tests that calling ACE Zero with no arguments produces the expected
         default values. """
        test_args = []
        expected_output = {'scenario': None, 'graph': False, 'critics': False,
                           'xcombat_path': None, 'noxcombat': False}
        parsed_args = ace_zero.parse_arguments(test_args)
        self.assertEqual(vars(parsed_args), expected_output)

    def test_arguments_parsed_correctly(self):
        """ Tests that the command line arguments are parsed correctly. """
        test_args = ['--scenario', 'TestScenario', '--graph',
                     '--noxcombat', '--xcombat_path', 'TestPath', '--critics']
        expected_output = {'scenario': 'TestScenario', 'graph': True,
                           'xcombat_path': 'TestPath', 'critics': True,
                           'noxcombat': True}
        parsed_args = ace_zero.parse_arguments(test_args)
        self.assertEqual(vars(parsed_args), expected_output)

    def test_find_xcombat(self):
        """ Tests that the XCombat executable is found correctly in a
        subdirectory. """
        subdir = "test_find_xcombat_temp_directory"
        xcombat_filename = "testxcombatfile.exe"

        # Get the absolute path to the test xcombat executable
        abspath = os.path.abspath(__file__)
        dname = os.path.dirname(abspath)
        subdir_path = os.path.join(dname, subdir)
        xcombat_path = os.path.join(subdir_path, xcombat_filename)

        # Create a test xcombat executable in a subdirectory
        if not os.path.exists(subdir_path):
            os.mkdir(subdir_path)
        open(xcombat_path, 'w').close()

        # Check that the test file is found correctly by find_xcombat()
        self.assertEqual(ace_zero.find_xcombat(), xcombat_path)

        # Remove the test file and directory
        os.remove(xcombat_path)
        os.rmdir(subdir)
