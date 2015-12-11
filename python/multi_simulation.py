#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy
import simulation

class MultiSimulation(object):

  def __init__(base, size=100):
      self.base = base
      self.size = size
      self.a_pvs = []

  def perform(self):
      for i in range(self.size):
          simulation = copy.deepcopy(self.base)
          simulation.perform()
          self.a_pvs.append(simulation.a_pv)

  def mean_pv(self):
      return sum(self.a_pvs) / len(a_pvs)
