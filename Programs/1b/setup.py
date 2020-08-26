# from distutils.core import setup
# import py2exe
# import sys
# sys.setrecursionlimit(5000)
# sys.argv.append('py2exe')
# setup(
#   options = {
#     'py2exe' : {
#         'compressed': 1,
#         'optimize': 2,
#         'includes': ['ace_zero'],
#         'bundle_files': 3, #Options 1 & 2 do not work on a 64bit system
#         'dist_dir': 'GA_exe',  # Put .exe in dist/
#         'xref': False,
#         'skip_archive': False,
#         'ascii': False,
#         }
#         },
#   zipfile=None,
#   console = ['driver.py'],
# )

# from distutils.core import setup
# import py2exe
# import sys
# import namedlist
# import behaviour3py
#
# sys.setrecursionlimit(5000)
# sys.argv.append('py2exe')
# setup(
#   options = {
#     'py2exe' : {
#         'compressed': 1,
#         'optimize': 2,
#         'includes': [],
#         'excludes': ['_gtkagg', '_tkagg'],
#         'dll_excludes': ['libgdk-win32-2.0-0.dll',
#                          'libgobject-2.0-0.dll'],
#         'bundle_files': 3, #Options 1 & 2 do not work on a 64bit system
#         'dist_dir': 'GA_exe',  # Put .exe in dist/
#         'xref': False,
#         'skip_archive': False,
#         'ascii': False,
#         }
#         },
#   zipfile=None,
#   console = ['driver.py'],
# )
from cx_Freeze import setup, Executable
import sys
import ace_zero
import matplotlib
import agents
# import fsm_agent
# from fsm_agent import stern_conversion


build_exe_options = {"packages": ["os", "numpy", "matplotlib"],
                     # "includes": ["numpy", "ace_zero", "matplotlib"],
                     "includes": ["numpy", "matplotlib"],
                     "zip_exclude_packages": "ace_zero",
                     "include_files": ["checkpoint2.pkl",
                                       "checkpoint.pkl",
                                       "r1_testset.pkl",
                                       "r2_testset.pkl",
                                       "r3_test_set.pkl",
                                       # "pms.json",
                                       "ace_zero-v09\\ace0\\data\\blue.json",
                                       "ace_zero-v09\\ace0\\data\\red.json",
                                       "ace_zero-v09\\ace0\\data\\blue_tactics.json",
                                       "ace_zero-v09\\ace0\\data\\red_tactics.json",
                                       ]}
base = None

"""
Set up script to freeze the program with cx_freeze into a .exe file
"""
setup(name="GA DRIVER",
      version="0.1",
      description="wvr 1v1",
      options={"build_exe": build_exe_options},
      executables=[Executable("driver_round3.py", base=base)]
)