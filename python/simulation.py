#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy
import random

class MultiSimulation(object):

  def __init__(self, base, size=100):
      self.base = base
      self.size = size
      self.a_pvs = []

  def perform(self):
      for i in range(self.size):
          simulation = copy.deepcopy(self.base)
          simulation.perform()
          self.a_pvs.append(simulation.a_pv)

  def mean_pv(self):
      return sum(self.a_pvs)/len(self.a_pvs)


class Simulation(object):
    # a_nav
    # b_nav
    # m_nav
    # a_quantity
    # b_quantity
    # index_val
    # a_cashflows
    # b_cashflows
    # a_pv
    # b_pv

    TRADING_DAYS = 250

    def __init__(self,
                 a_nav=1.0,
                 m_nav=1.0,
                 i=0.025,
                 m=0.03,
                 uat=1.5,
                 dat=0.25,
                 r=0.08,
                 rm=0.10,
                 v=0.30,
                 d=1,
                 years=50,
                 debug=False,
                 show_price=False):
        self.a_nav = a_nav
        self.m_nav = m_nav
        self.b_nav = 2 * m_nav - a_nav
        self.index_val = 100.0
        self.uat = uat
        self.dat = dat
        self.a_cashflows = []
        self.b_cashflows = []
        self.a_pv = 0.0
        self.b_pv = 0.0
        self.r = r
        self.rm = rm
        self.coupon = i + m
        self.v = v
        self.initial_date = d
        self.current_date = self.initial_date
        self.years = years
        self.a_quantity = 10000.0
        self.b_quantity = 10000.0
        self.debug = debug
        self.show_price = show_price

        daily_weight = 1.0/self.TRADING_DAYS
        self.daily_v = self.v * (daily_weight ** 0.5)
        self.daily_rm = self.rm * daily_weight
        self.daily_coupon = self.coupon * daily_weight

    def perform(self):
        while self.current_date <= self.initial_date + self.years * self.TRADING_DAYS:
            self.stock_index_movement()
            self.coupon_settlement()
            self.scheduled_adjustment()
            self.upward_adjustment()
            self.downward_adjustment()
            if self.show_price and self.current_date % 20 == 0:
                args = {
                    current_date:self.current_date,
                    a_quantity: round(self.a_quantity, 2),
                    a_nav: round(a_nav, 2),
                    b_nav: round(b_nav, 2),
                    m_nav: round(m_nav, 2),
                    index_val: round(index_val, 2),
                }
                print("{current_date}\t{a_quantity}\t{a_nav}\t{b_nav}\t{m_nav}\t#{index_val}".format(args))
            self.current_date += 1

    def stock_index_movement(self):
        delta = round(random.normalvariate(self.daily_rm, self.daily_v), 4)
        # print("rm {:.4f}\t v {:.4f} \t delta {:.4f}".format(self.daily_rm, self.daily_v, delta))
        self.index_val = round(self.index_val*(1+delta), 2)
        # old_m_nav = self.m_nav
        self.m_nav = round(self.m_nav*(1+delta), 4)
        self.b_nav = self.m_nav * 2 - self.a_nav

    def coupon_settlement(self):
        interest = self.a_nav * self.daily_coupon
        self.b_nav -= interest
        self.a_nav += interest

    def scheduled_adjustment(self):
        if self.current_date % self.TRADING_DAYS == 0:
            settlement = self.a_nav - 1.0
            a_income = settlement * self.a_quantity
            self.a_nav -= settlement
            self.a_cashflows.append([a_income, self.current_date])
            self.a_pv += round(self.discount(a_income), 4)
            if self.debug:
                print(u"{}\t定折\t{:.2f}\t{:.2f}\t{:.2f}".format(self.current_date, a_income, self.discount(a_income), self.a_pv))

    def upward_adjustment(self):
        if self.m_nav >= self.uat:
            a_settlement = self.a_nav - 1.0
            b_settlement = self.b_nav - 1.0
            a_income = a_settlement * self.a_quantity
            b_income = b_settlement * self.b_quantity
            self.m_nav = 1.0
            self.a_nav -= a_settlement
            self.a_cashflows.append([a_income, self.current_date])
            self.a_pv += round(self.discount(a_income), 4)
            self.b_nav -= b_settlement
            self.b_cashflows.append([b_income, self.current_date])
            self.b_pv += round(self.discount(b_income), 4)
            if self.debug:
                print(u"{}\t上折\t{:.2f}\t{:.2f}\t{:.2f}".format(self.current_date, a_income, self.discount(a_income), self.a_pv))

    def downward_adjustment(self):
        if self.b_nav <= self.dat:
            a_settlement = self.a_nav - self.b_nav
            a_income = a_settlement * self.a_quantity
            self.a_cashflows.append([a_income, self.current_date])
            self.a_pv += self.discount(a_income) # .quantize(decimal.Decimal('.0001'))
            self.a_quantity *= self.b_nav / 1.0
            self.b_quantity *= self.b_nav / 1.0
            self.a_nav = 1.0
            self.b_nav = 1.0
            self.m_nav = 1.0
            if self.debug:
                print(u"{}\t下折\t{:.2f}\t{:.2f}\t{:.2f}".format(self.current_date, a_income, self.discount(a_income), self.a_pv))

    def discount(self, value):
        days = self.current_date - self.initial_date
        return value * ((1 + self.r) ** -(days / self.TRADING_DAYS))
