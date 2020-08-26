import sys
import os
from cx_Freeze import setup, Executable


# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["os","matplotlib", "sys", "deap"],
                                    "include_files": [(os.path.join((os.path.dirname(__file__)),
                                    r"ace_zero-v09\ace0\data\blue.json"), 
                                    "blue.json"),
                                    (os.path.join((os.path.dirname(__file__)),
                                    r"ace_zero-v09\ace0\data\ecu_blue_tactics.json"), 
                                    "ecu_blue_tactics.json"),
                                    (os.path.join((os.path.dirname(__file__)),
                                    r"ace_zero-v09\ace0\data\ecu_basic_blue_tactics.json"), 
                                    "ecu_basic_blue_tactics.json"),
                                    (os.path.join((os.path.dirname(__file__)),
                                    r"ace_zero-v09\ace0\data\blue_tactics.json"), 
                                    "blue_tactics.json"),
                                    (os.path.join(os.path.dirname(__file__), r"ace_zero-v09\ace0\data\blue.json"), 
                                    "blue.json"),
                                    (os.path.join(os.path.dirname(__file__), r"ace_zero-v09\ace0\data\ecu_basic_blue_tactics.json"), 
                                    "ecu_basic_blue_tactics.json"),
                                    (os.path.join(os.path.dirname(__file__), r"ace_zero-v09\ace0\data\ecu_blue_tactics.json"), 
                                    "ecu_blue_tactics.json"),
                                    (os.path.join(os.path.dirname(__file__), r"ace_zero-v09\ace0\data\blue_tactics.json"), 
                                    "blue_tactics.json"),
                                    (os.path.join(os.path.dirname(__file__), r"ace_zero-v09\ace0\data\red.json"), 
                                    "red.json"),
                                    (os.path.join(os.path.dirname(__file__), r"ace_zero-v09\ace0\data\blue_tactics - Copy.json"), 
                                    "blue_tactics - Copy.json"),
                                    (os.path.join(os.path.dirname(__file__), r"ace_zero-v09\ace0\data\ecu_blue_tactics - Copy.json"), 
                                    "ecu_blue_tactics - Copy.json")],
                     "excludes": ["tkinter"]}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win64":
    base = "Console"

setup(  name = "GA",
        version = "0.1",
        description = "Trial GA",
        options = {"build_exe": build_exe_options},
        executables = [Executable("driver.py", base=base)])

"""

                     "include_files": [(os.path.join((os.path.dirname(__file__)),
                                        r"ace_zero-v09\mikepsn-ace_zero-04dc9d00f7eb\data\blue.json"), 
                                        "blue.json"),
                                        (os.path.join((os.path.dirname(__file__)),
                                        r"ace_zero-v09\mikepsn-ace_zero-04dc9d00f7eb\data\ecu_blue_tactics.json"), 
                                        "ecu_blue_tactics.json"),
                                        (os.path.join((os.path.dirname(__file__)),
                                        r"ace_zero-v09\mikepsn-ace_zero-04dc9d00f7eb\data\ecu_basic_blue_tactics.json"), 
                                        "ecu_basic_blue_tactics.json"),
                                        (os.path.join((os.path.dirname(__file__)),
                                        r"ace_zero-v09\mikepsn-ace_zero-04dc9d00f7eb\data\blue_tactics.json"), 
                                        "blue_tactics.json"),
                                        (os.path.join(os.path.dirname(__file__), r"data\blue.json"), 
                                        "blue.json"),
                                        (os.path.join(os.path.dirname(__file__), r"data\ecu_basic_blue_tactics.json"), 
                                        "ecu_basic_blue_tactics.json"),
                                        (os.path.join(os.path.dirname(__file__), r"data\ecu_blue_tactics.json"), 
                                        "ecu_blue_tactics.json"),
                                        (os.path.join(os.path.dirname(__file__), r"data\blue_tactics.json"), 
                                        "blue_tactics.json"),
                                        (os.path.join(os.path.dirname(__file__), r"data\red.json"), 
                                        "red.json"),
                                        (os.path.join(os.path.dirname(__file__), r"data\blue_tactics - Copy.json"), 
                                        "blue_tactics - Copy.json"),
                                        (os.path.join(os.path.dirname(__file__), r"data\ecu_blue_tactics - Copy.json"), 
                                        "ecu_blue_tactics - Copy.json")],

"""