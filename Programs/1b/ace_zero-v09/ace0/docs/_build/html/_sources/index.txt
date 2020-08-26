.. ace_zero documentation master file, created by
   sphinx-quickstart on Tue Sep 13 22:38:57 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to ace_zero's documentation!
====================================

ACE ZERO is a prototype environment for undertaking multi-agent simulation
research. Click on the Modules Index link below to find the source code 
documentation. 

Contents:

.. toctree::
   :maxdepth: 4

Getting Started
===============

You will need to install Python 2.7 with the Python scientific computing stack
(NumPy, SciPy, matplotlib etc.) We have been using the Anaconda scientific
Python distribution. You can download versions for Windows, Mac and Linux from
`Continuum Analytics <http://www.continuum.io/>`_.

XCombat 
=======
XCombat is (currently) a Windows 3D visualisation tool for animating and visualising
simulation runs. XCombat is executed on the command line with a history (.his) file 
as follows::

    > xcombat.exe myhistory.his

XCombat can be run separately from ACE ZERO or it can be called from within
ACE ZERO so you immediately see the results of a simulation run.

You can install XCombat anywhere you like and tell ACE ZERO where to find it (see below). 

Running ACE ZERO
================

ACE ZERO is run on the command line as follows::

    > python ace_zero.py --noxcombat 

It is useful to specifiy a specific scenario and also to tell ACE ZERO where to find
the xcombat executable. This is done as follows::

    > python .\ace_zero.py --xcombat_path C:\Users\mikep\Desktop\xcombat34\xcombat34.exe --scenario .\test\test_goal_agent\goal_agent_scenario.json

Change the xcombat path to where you have installed it. In the above example the scenario being run is a simple one which just tests out a series
of commands given to a test agent known as the goal agent.

Optional
========
If you want to build the docs you will also need the sphinx_rtd_theme. You can install
it as follows::

    conda install sphix_rtd_theme

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

