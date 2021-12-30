# -*- coding: utf-8 -*-

# python imports
import time
from math import degrees

# pyfuzzy imports
from fuzzy.storage.fcl.Reader import Reader
from utils import *


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

    def fuzzify(self, inputs):
        # Calculating membership of current pa value in the fuzzy sets defined for pa
        pa = inputs['pa'] % 360
        pa_memberships = {}
        for key in self.fuzzy_sets['pa']:
            value = self.fuzzy_sets['pa'][key]
            pa_memberships[key] = get_value_from_points(value, pa)

        pv = inputs['pv']
        pv_memberships = {}
        for key in self.fuzzy_sets['pv']:
            value = self.fuzzy_sets['pv'][key]
            pv_memberships[key] = get_value_from_points(value, pv)

        cp = inputs['cp']
        cp_memberships = {}
        for key in self.fuzzy_sets['cp']:
            value = self.fuzzy_sets['cp'][key]
            cp_memberships[key] = get_value_from_points(value, cp)

        cv = inputs['cv']
        cv_memberships = {}
        for key in self.fuzzy_sets['cv']:
            value = self.fuzzy_sets['cv'][key]
            cv_memberships[key] = get_value_from_points(value, cv)

        r = {'pa': pa_memberships, 'pv': pv_memberships, 'cp': cp_memberships, 'cv': cv_memberships}
        return r

    def inference(self, fuzzy_values):
        result_fuzzy_vars = {}
        for rule_name in self.rules:
            rule_dict = self.rules[rule_name]
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
                for subset in self.fuzzy_sets[res_var]:
                    result_fuzzy_vars[res_var][subset] = 0.0
            result_fuzzy_vars[res_var][res_set] = max(result_fuzzy_vars[res_var][res_set], power)

        return result_fuzzy_vars

    def defuzzify(self, fuzzy_result):
        result = {}
        for var in fuzzy_result:
            all_points = []
            for subset_name in get_subset_names(var):
                subset_points = self.fuzzy_sets[var][subset_name]
                max_value = fuzzy_result[var][subset_name]
                all_points.extend(cut_points(subset_points, max_value))
            all_points = mix_points(all_points)
            result[var] = get_centroid(all_points)

        return result

    def calculate(self, inputs):
        fuzzy_values = self.fuzzify(inputs)
        fuzzy_result = self.inference(fuzzy_values)
        return self.defuzzify(fuzzy_result)

    def decide(self, world):
        # output = self._make_output()
        # self.system.calculate(self._make_input(world), output)
        # print self._make_input(world)
        # time.sleep(10)
        output = self.calculate(self._make_input(world))
        return output['force']

