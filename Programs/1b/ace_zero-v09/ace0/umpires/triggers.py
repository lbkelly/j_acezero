"""
    Triggers for terminating the simulation.
"""

__author__ = 'miquelramirez'

class MaxTimeElapsed(object):
    """ Specifies the maximum simulation time allowed. """

    def __init__(self, max_time=180):
        self.max_time_elapsed = max_time

    def check(self, obj):
        """ Returns true if the current_time is greater than the elapsed time. """
        return obj.current_time > self.max_time_elapsed
