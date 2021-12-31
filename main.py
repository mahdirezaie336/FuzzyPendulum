#!/usr/bin/env python
# -*- coding: utf-8 -*-

# project imports
import time

from conf import ConfigReader
from world import World
from controller import FuzzyController
from manager import Manager


conf = ConfigReader()

if __name__ == '__main__':
    world = World(**conf.world_config())
    controller = FuzzyController(**conf.controller_config())
    # fr = {'force': {'left_slow': 0.35800231303930197, 'left_fast': 0.35800231303930197, 'right_slow': 0.0,
    #                 'stop': 0.5298801662440145, 'right_fast': 0.0}}
    # print controller.defuzzify(fr)
    # time.sleep(100)
    manager = Manager(world, controller, **conf.simulation_config())
    manager.run()
