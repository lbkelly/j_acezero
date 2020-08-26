import helpers
import os

"""
A test script for saving out initial values to a JSON file
"""

__author__ = 'lbkelly'


class WriteInitial:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.altitude = 10000
        self.heading = 0
        self.speed = 100

    def update_initial_values(self, x, y, altitude, heading, speed):
        self.x = x
        self.y = y
        self.altitude = altitude
        self.heading = heading
        self.speed = speed

        initial = {
                        "callsign": "viper",
                        "id": 0,
                        "side": 1,
                        "metric": "Imperial/Nautical",
                        "x": self.x,
                        "y": self.y,
                        "z": self.altitude,
                        "psi": self.heading,
                        "theta": 0.0,
                        "phi": 0.0,
                        "v": self.speed,
                        "weight": 100.0,
                        "fuel": 100.0,
                        "v_min": 100,
                        "v_max": 1000,
                        "v_K": 0.1,
                        "theta_K": 0.005,
                        "psi_K": 10.0
                    }
        helpers.save_chromosome_to_file(initial,
                                        (os.path.dirname(__file__)) +
                                        r"\ace_zero-v09\ace0\data\blue.json")

    @staticmethod
    def save_initial_default_values():
        initial = {
            "callsign": "viper",
            "id": 0,
            "side": 1,
            "metric": "Imperial/Nautical",
            "x": 0.0,
            "y": 5.0,
            "z": 15000.0,
            "psi": 0.0,
            "theta": 0.0,
            "phi": 0.0,
            "v": 400.0,
            "weight": 100.0,
            "fuel": 100.0,
            "v_min": 100,
            "v_max": 1000,
            "v_K": 0.1,
            "theta_K": 0.005,
            "psi_K": 10.0
        }

        helpers.save_chromosome_to_file(initial,
                                        (os.path.dirname(__file__)) +
                                        r"\ace_zero-v09\ace0\data\blue.json")
