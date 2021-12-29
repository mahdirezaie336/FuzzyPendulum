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

        cp = inputs['cp']
        cp_memberships = {}
        for key, value in self.fuzzy_sets['cp']:
            cp_memberships[key] = self.get_membership(value, cp)

        cv = inputs['cv']
        cv_memberships = {}
        for key, value in self.fuzzy_sets['cv']:
            cv_memberships[key] = self.get_membership(value, cv)

        r = {'pa': pa_memberships, 'pv': pv_memberships, 'cp': cp_memberships, 'cv': cv_memberships}
        return r

    def inference(self, fuzzy_values):
        result_fuzzy_vars = {}
        for rule_name, rule_dict in self.rules:
            power = 0
            for or_condition in rule_dict['IF']:
                min_membership = 1
                for and_condition in or_condition:
                    var_name = and_condition[0]
                    var_value = and_condition[1]
                    min_membership = min(min_membership, fuzzy_values[var_name][var_value])
                power = max(power, min_membership)

            res_var = rule_dict['THEN'][0]
            res_set = rule_dict['THEN'][1]
            if res_var not in result_fuzzy_vars:
                result_fuzzy_vars[res_var] = {}
            result_fuzzy_vars[res_var][res_set] = max(result_fuzzy_vars[res_var].get(res_set, 0), power)
        return result_fuzzy_vars

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
