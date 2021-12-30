# -*- coding: utf-8 -*-

# python imports
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

    def get_membership(self, points, value):
        for i, item in enumerate(points):
            if i == 0:
                continue
            x, d = item
            xp, dp = points[i - 1]
            if xp <= value <= x:
                return dp + float(dp - d) / (xp - x) * (value - xp)
        return 0.0

    def fuzzify(self, inputs):
        # Calculating membership of current pa value in the fuzzy sets defined for pa
        pa = inputs['pa']
        pa_memberships = {}
        for key in self.fuzzy_sets['pa']:
            value = self.fuzzy_sets['pa'][key]
            pa_memberships[key] = self.get_membership(value, pa)

        pv = inputs['pv']
        pv_memberships = {}
        for key in self.fuzzy_sets['pv']:
            value = self.fuzzy_sets['pv'][key]
            pv_memberships[key] = self.get_membership(value, pv)

        cp = inputs['cp']
        cp_memberships = {}
        for key in self.fuzzy_sets['cp']:
            value = self.fuzzy_sets['cp'][key]
            cp_memberships[key] = self.get_membership(value, cp)

        cv = inputs['cv']
        cv_memberships = {}
        for key in self.fuzzy_sets['cv']:
            value = self.fuzzy_sets['cv'][key]
            cv_memberships[key] = self.get_membership(value, cv)

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
            result_fuzzy_vars[res_var][res_set] = max(result_fuzzy_vars[res_var], power)
        return result_fuzzy_vars

    def defuzzify(self, fuzzy_result):
        result = {}
        for var in fuzzy_result:
            var_dict = fuzzy_result[var]

            if var not in result:
                result[var] = {}

            for subset_name in self.fuzzy_sets[var]:
                subset_points = self.fuzzy_sets[var][subset_name]

                if subset_name not in result[var]:
                    result[var][subset_name] = []

                max_value = fuzzy_result[var][subset_name]
                for i, point in enumerate(subset_points):
                    x = point[0]
                    d = point[1]

                    # Split a point into multiple points
                    if d > max_value:
                        if i == 0:
                            new_x = get_x_of(max_value, point, subset_points[1])
                            result[var][subset_name].append((x, max_value))
                            result[var][subset_name].append((new_x, max_value))
                        elif i == len(subset_points) - 1:
                            new_x = get_x_of(max_value, subset_points[-2], point)
                            result[var][subset_name].append((x, max_value))
                            result[var][subset_name].append((new_x, max_value))
                        else:
                            new_x1 = get_x_of(max_value, point, subset_points[i+1])
                            new_x2 = get_x_of(max_value, subset_points[i-1], point)
                            result[var][subset_name].append((new_x1, max_value))
                            result[var][subset_name].append((new_x2, max_value))
                    else:
                        result[var][subset_name].append(point)

        result_of_results = {}
        for var in result:
            var_dict = result[var]
            list_of_lists = []
            while len(var_dict) != 0:
                minimum_set = []
                minimum_point = float('inf')
                minimum_name = ''
                for subset_name in var_dict:
                    subset_points = var_dict[subset_name]
                    if minimum_point > subset_points[0][0]:
                        minimum_point = subset_points[0][0]
                        minimum_set = subset_points
                        minimum_name = subset_name
                list_of_lists.append(minimum_set)
                del var_dict[minimum_name]

            all_points = []
            for points_list in list_of_lists:
                all_points.extend(points_list)

            all_points = mix_points(all_points)
            centroid = get_centroid(all_points)
            result_of_results[var] = centroid

        return result_of_results

    def calculate(self, inputs):
        fuzzy_values = self.fuzzify(inputs)
        fuzzy_result = self.inference(fuzzy_values)
        return self.defuzzify(fuzzy_result)

    def decide(self, world):
        # output = self._make_output()
        # self.system.calculate(self._make_input(world), output)
        output = self.calculate(self._make_input(world))
        return output['force']

