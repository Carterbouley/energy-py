import pulp

from pulp import LpProblem, LpMinimize, LpVariable, LpStatus

"""
all efficiencies are HHV

you cant use divide by with pulp
have to do obj first then do constraints

obj needs all the costs
- gas
- elect

balances need
- steam
- elect

"""

class GasTurbine(object):
    lb = 50
    ub = 100

    def __init__(
            self,
            prob,
            size,
            name,
    ):
        self.prob = prob

        #  MW
        self.size = size

        self.effy = {
            'electrical': 0.28,
            'thermal': 0.4
        }

        #  %
        self.cont = LpVariable(name, 0, self.ub)

        # self.binary = LpVariable(
        #     '{}_binary'.format(name),
        #     0,
        #     1,
        #     cat='Integer'
        # )

        self.binary = LpVariable('bin', lowBound=0, upBound=1, cat='Integer')

        #  MW
        self.load = self.cont * (1/100)

    def steam_generated(self):
        """ t/h """
        heat_generated = self.size * self.load * (1 / self.effy['electrical']) * self.effy['thermal']
        return heat_generated * (1 / enthalpy) * 3.6

    def gas_burnt(self):
        """  MW HHV """
        return self.size * self.load * (1 / self.effy['electrical'])

    def power_generated(self):
        """  MW """
        return self.load * self.size


class Boiler(object):

    def __init__(
            self,
            prob,
            size,
            name,
            min_turndown=0.0,
            parasitics=0.0
    ):
        self.prob = prob
        self.effy = {
            'thermal': 0.8
        }

        #  t/h
        self.load = LpVariable(name, min_turndown, size)
        #  MW
        self.parasitics = parasitics

    def steam_generated(self):
        """ t/h """
        return self.load

    def gas_burnt(self):
        """ MW HHV """
        #  https://www.tlv.com/global/TI/calculator/steam-table-temperature.html
        #  30 barG, 250 C vapour - liquid enthalpy at 100C
        #  MJ/kg = kJ/kg * MJ/kJ

        #  MW = t/h * kg/t * hr/sec * MJ/kg / effy
        return self.load * (1/3.6) * enthalpy * (1/self.effy['thermal'])

    def power_generated(self):
        """ MW """
        return self.parasitics


enthalpy =  (2851.34 - 418.991) / 1000
gas_price = 20
electricity_price = 1000

prob = LpProblem('cost minimization', LpMinimize)

assets = [
    GasTurbine(prob=prob, size=10, name='gt1'),
    Boiler(prob=prob, size=100, name='blr1')
]

#  need to form objective function first
prob += sum([asset.gas_burnt() for asset in assets]) * gas_price \
    - sum([asset.power_generated() for asset in assets]) * electricity_price

#  then add constraints
prob += sum([asset.steam_generated() for asset in assets]) == 10

#  asset constraints
prob += assets[0].cont - assets[0].ub * assets[0].binary <= 0
prob += assets[0].lb * assets[0].binary - assets[0].cont <= 0

prob.writeLP('chp.lp')

prob.solve()

print(LpStatus[prob.status])

for v in prob.variables():
    print('{} {}'.format(v.name, v.varValue))
