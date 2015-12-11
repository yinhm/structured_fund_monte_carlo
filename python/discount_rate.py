#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse

from simulation import Simulation, MultiSimulation

def print_head():
    print(u"-" * 80)
    print(u"利率上浮\t折现率\t平均PV")    

def discount_rate(args):
    print(u"折现率分析 - 样本数：{}".format(args.samples))
    print_head()

    for premium in [3.0, 4.0, 5.0]:
        for r in [5.0, 8.0, 10.0]:
            m0 = float(premium) / 100
            r0 = float(r) / 100
            base = Simulation(m=m0, r=r0, debug=args.debug)
            multi_sim = MultiSimulation(base, size=args.samples)
            multi_sim.perform()

            print("{:.0%}\t{:.0%}\t{:.2f}".format(m0, r0, multi_sim.mean_pv()))


def m_nav(args):
    print("母基金净值分析 - 样本数：{}".format(args.samples))
    print_head()

    for premium in ["3", "4", "5"]:
        for m_nav in ["0.65", "0.80", "1.00", "1.20", "1.45"]:
            m0 = float(premium)/100
            m_nav0 = float(m_nav) / 100
            base = Simulation(m=m0, m_nav=m_nav0, debug=args.debug)
            multi_sim = MultiSimulation(base, size=args.samples)
            multi_sim.perform()
            print("{}%\t{}%\t{:.2f}".format(premium, m_nav, multi_sim.mean_pv()))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=u"模特卡罗模拟分级A定价")
    parser.add_argument("-debug", action='store_true')
    parser.add_argument("-samples", help=u"样本数", default=100, type=int)
    parser.add_argument("-discount_rate", action='store_true', help=u"折现率分析")
    parser.add_argument("-mnav", action='store_true', help=u"母基金净值")

    args = parser.parse_args()
    if args.discount_rate:
        discount_rate(args)
    if args.mnav:
        m_nav(args)

    
