# -*- coding: utf-8 -*-

# python imports
from math import degrees

# pyfuzzy imports
from fuzzy.storage.fcl.Reader import Reader
from utils import read_rules


class FuzzyController:

    def __init__(self, fcl_path):
        self.system = Reader().load_from_file(fcl_path)
        self.fuzzy_sets = {
            'pa': {
                'up_more_right': [(0, 0), (30, 1), (60, 0)],
                'up_right': [(30, 0), (60, 1), (90, 0)],
                'up': [(60, 0), (90, 1), (120, 0)],
                'up_left': [(90, 0), (120, 1), (150, 0)],
                'up_more_left': [(120, 0), (150, 1), (180, 0)],
                'down_more_left': [(180, 0), (210, 1), (240, 0)],
                'down_left': [(210, 0), (240, 1), (270, 0)],
                'down': [(240, 0), (270, 1), (300, 0)],
                'down_right': [(270, 0), (300, 1), (330, 0)],
                'down_more_right': [(300, 0), (330, 1), (360, 0)]
            },

            'pv': {
                'cw_fast': [(-200, 1), (-100, 0)],
                'cw_slow': [(-200, 0), (-100, 1), (0, 0)],
                'stop': [(-100, 0), (0, 1), (100, 0)],
                'ccw_slow': [(0, 0), (100, 1), (200, 0)],
                'ccw_fast': [(100, 0), (200, 1)],
            }
        }

        self.rules = read_rules()

    def _make_input(self, world):
        return dict(
            cp=world.x,
            cv=world.v,
            pa=degrees(world.theta),
            pv=degrees(world.omega)
        )

    def _make_output(self):
        return dict(
            force=0.
        )

    def get_membership(self, points, value):
        for i, item in enumerate(points):
            if i == 0:
                continue
            x, d = item
            xp, dp = points[i - 1]
            if xp <= value <= x:
                return dp + (dp - d) / (xp - x) * (value - xp)
        return 0.0

    def fuzzify(self, inputs):
        # Calculating membership of current pa value in the fuzzy sets defined for pa
        pa = inputs['pa']
        pa_memberships = {}
        for key, value in self.fuzzy_sets['pa']:
            pa_memberships[key] = self.get_membership(value, pa)

        pv = inputs['pv']
        pv_memberships = {}
        for key, value in self.fuzzy_sets['pv']:
            pv_memberships[key] = self.get_membership(value, pv)

        return pa_memberships, pv_memberships

    def inference(self):
        pass

    def defuzzify(self, output):
        pass

    def calculate(self, inputs, output):
        self.fuzzify(inputs)
        self.inference()
        self.defuzzify(output)

    def decide(self, world):
        output = self._make_output()
        self.system.calculate(self._make_input(world), output)
        self.calculate(self._make_input(world), output)
        return output['force']
