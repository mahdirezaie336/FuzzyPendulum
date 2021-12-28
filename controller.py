# -*- coding: utf-8 -*-

# python imports
from math import degrees

# pyfuzzy imports
from fuzzy.storage.fcl.Reader import Reader
from utils import read_rules, load_fuzzy_sets


class FuzzyController:

    def __init__(self, fcl_path):
        self.system = Reader().load_from_file(fcl_path)
        self.fuzzy_sets = load_fuzzy_sets()
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
