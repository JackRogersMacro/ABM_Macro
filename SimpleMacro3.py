"""
Simple Macroeconomic Model with Satisficing Behaviour
Authors: Hyun Chang Yi and Sarunas Girdenas
LastModified: 04/06/2014
"""
# from datetime import datetime # import this to calculate script execution time
# startTime=datetime.now()

from random import randrange, choice, randint
from random import uniform as uniform_range
from numpy.random import uniform
import matplotlib.pyplot as plt
from scipy import mean
from math import log


#In this model we have three types of agents: Households, Firms and Central Bank

# Bank sets nominal interest rate, operate capital market, clear payments and records economy
class Bank:

    def __init__(self,TrblActn=0.05, TrbSatLv=0.05, LAMBDA=0.05, gamma=0.5,
                inertia=0.9, interest=0.05, periods=2, delta=0.005, min_irate=0.001):
        self.TrblActn, self.TrbSatLv, self.LAMBDA, self.gamma, self.inertia = TrblActn, TrbSatLv, LAMBDA, gamma, inertia
        self.periods, self.delta, self.min_irate = periods, delta, min_irate
        # self.irate_nodes = range(int(max_irate/unit) + 1)   # decision nodes over interest rates
        self.lqdty, self.irate = 0, interest
        self.p, self.f, self.i, self.r, self.c, self.a = [], [], [], [], [], []
        # self.alp_i, self.alp_p = 1, 1
        self.inflation = 0
        self.price = 1
        self.sl_output, self.sl_infltn, self.val_output, self.val_infltn = 0, 0, 0, 0
        self.ActionChanged = True
        
    def set_interest(self, household, firm):
        # Set nominal interest rate as 0,1,2,...,i,i+1,... where  i stands for 0.1*i percent and announce to the public
        #current_coefs = [self.alp_i, self.alp_p]
        current_irate = self.irate
        Tremble = uniform() < self.TrblActn
        Inertia = uniform() < self.inertia
        satisficing_output = self.val_output >= self.sl_output
        satisficing_infltn = self.val_infltn >= self.sl_infltn
        if not(Inertia):
            if Tremble or not(satisficing_output) or not(satisficing_infltn):
                    self.irate = uniform_range(max(self.min_irate, self.irate-(self.delta)), self.irate+(self.delta))
            else:
                self.irate = uniform_range(max(self.min_irate, self.irate-(self.delta)), self.irate+(self.delta))
        # self.irate = min(self.irate, int(self.max_irate/self.unit))
        if current_irate == self.irate:
            self.ActionChanged = False
        # if not(Inertia):
        #     if (Tremble or not(satisficing_output) or not(satisficing_infltn)):
        #         self.alp_i = randint(max(-2, self.alp_i - self.delta), min(5, self.alp_i + self.delta))
        #         self.alp_p = randint(max(-2, self.alp_p - self.delta), min(5, self.alp_p + self.delta))
        # # Rule for random choice randint(max(0, self.irate - self.delta), self.irate + self.delta)
        # self.irate = int(min(max(0, self.alp_i*household.c[irate_node] 
        #     + self.alp_p*self.inflation), self.max_irate/self.unit))
        # if current_coefs == [self.alp_i, self.alp_p] :
        #     self.ActionChanged = False
        Tremble = uniform() < self.TrbSatLv
        lamda = uniform()**self.gamma
        if not(Tremble):
            self.sl_output += lamda*self.LAMBDA*min(self.val_output - self.sl_output, 0)
            self.sl_infltn += lamda*self.LAMBDA*min(self.val_infltn - self.sl_infltn, 0)
        else:
            self.sl_output += lamda*(self.val_output-self.sl_output)
            self.sl_infltn += lamda*(self.val_infltn-self.sl_infltn)
        household.irate = firm.irate = self.irate

    def channel(self, household, firm):
        # borrow money from household and lend it to firm
        self.lqdty = min(household.saving, firm.capital_demand)
        household.asset += max(0, household.saving - self.lqdty)
        firm.capital = self.lqdty
        # firm.capital = self.lqdty = household.saving

    def transfer_evaluate(self, household, firm): 
        # pay return from deposit and profit from firm to household
        # print '3. before transfer', household.asset, (1 + self.irate*self.unit)*self.lqdty, firm.profit
        household.asset = 0.3 + household.asset*(1.01) + (1 + self.irate)*self.lqdty + firm.profit
        # print '3. after transfer :', self.price, household.asset
        output = household.consumption/(self.price*1.0)
        #infltn = -self.inflation
        if len(self.p) >= self.periods:
            infltn = -(self.price - mean(self.p[-self.periods:]))**2
        else:
            infltn = 0
        #household.asset = int((1 + self.irate*self.unit)*self.lqdty + firm.profit)
        self.p.append(self.price)
        if len(self.p) <= 2:
            self.inflation = 0
        else:
            self.inflation = (self.p[-1]-self.p[-2])/self.p[-2]
        self.f.append(firm.profit)
        self.i.append(self.irate*100)
        self.r.append(self.lqdty)
        self.c.append(output)
        self.a.append(household.asset)
        # evaluate current economy in terms of consumption level and price volatility
        rho = uniform()**self.gamma
        if not(self.ActionChanged):
            self.val_output += rho*(output - self.val_output)
            self.val_infltn += rho*(infltn - self.val_infltn)
        else:
            self.val_output, self.val_infltn = output, infltn    

        
class Household:

    def __init__(self, bank, firm, TrblActn=0.05, TrbSatLv=0.05, LAMBDA=0.05, gamma=0.5,
                inertia=0.5, asset=5, delta=0.1, irate_unit=0.005, irate_max=0.1):
        self.TrblActn, self.TrbSatLv, self.LAMBDA, self.gamma, self.inertia = TrblActn, TrbSatLv, LAMBDA, gamma, inertia
        self.delta = delta
        self.irate_unit, self.irate_max = irate_unit, irate_max
        self.irate_nodes = range(int(irate_max/irate_unit))
        self.asset = asset
        self.price = self.saving = self.irate = 1
        self.consumption = 1
        self.c = [0.3 for n in self.irate_nodes]
        self.sl_c = self.val_c = self.sl_asset = self.val_asset = \
            [0 for n in self.irate_nodes]
        self.ActionChanged = True

    def irate_node(self, irate):
        irate = min(self.irate_max - self.irate_unit, irate)
        return int(irate/self.irate_unit)

    def consume(self):       # choose how much to consume and save
        irate_node = self.irate_node(self.irate)
        # print '1. consumption:', self.asset
        self.consumption = self.c[irate_node]
        Tremble = uniform() < self.TrblActn
        Inertia = uniform() < self.inertia
        satisficing_consuption = self.val_c[irate_node] >= self.sl_c[irate_node]
        satisficing_asset = self.val_asset[irate_node] >= self.sl_asset[irate_node]
        if not(Inertia):
            if not(Tremble):
                if (not(satisficing_consuption) and (satisficing_asset)):
                    self.c[irate_node] = uniform_range(self.c[irate_node], min(1, self.c[irate_node]*(1+self.delta)))
                #     self.c[irate_node] = uniform_range(self.c[irate_node], 
                #         min(self.asset/self.price, self.c[irate_node] + self.delta))
                elif (satisficing_consuption and not(satisficing_asset)):
                    self.c[irate_node] = uniform_range(max(0, self.c[irate_node]*(1-self.delta)), self.c[irate_node])
                #     self.c[irate_node] = uniform_range(max(0, self.c[irate_node] - self.delta), 
                #         self.c[irate_node])
                elif (not(satisficing_consuption) and not(satisficing_asset)):
                    # self.c[irate_node] = uniform_range(max(0, self.c[irate_node] - self.delta), 
                    #     min(self.asset/self.price, self.c[irate_node] + self.delta))
                    self.c[irate_node] = uniform_range(max(0, self.c[irate_node]*(1-self.delta)), min(1, self.c[irate_node]*(1+self.delta)))
                    # self.c[irate_node] = uniform_range(max(0, self.c[irate_node]*(1-self.delta)), min(self.asset, self.c[irate_node]*(1+self.delta)))
                    # self.c[irate_node] = uniform_range(0, self.asset/self.price)
                # else:
                #     self.c[irate_node] = min(self.c[irate_node], self.asset/self.price)
            else:
                # self.c[irate_node] = uniform_range(max(0, self.c[irate_node] - self.delta), 
                #     min(self.asset/self.price, self.c[irate_node] + self.delta))
                self.c[irate_node] = uniform_range(max(0, self.c[irate_node]*(1-self.delta)), min(1, self.c[irate_node]*(1+self.delta)))
        # else:
        #     self.c[irate_node] = min(self.c[irate_node], self.asset/self.price)
        if self.consumption == self.c[irate_node]:
            self.ActionChanged = False        
        # self.consumption = self.c[irate_node]
        self.consumption = self.asset*self.c[irate_node]
        self.saving = self.asset - self.consumption
        self.asset = 0
        # print '1. after consumption: saving and consumption', self.saving, self.consumption
        Tremble = uniform() < self.TrbSatLv
        lamda = uniform()**self.gamma
        if not(Tremble):
            self.sl_c[irate_node] += lamda*self.LAMBDA*min(self.val_c[irate_node] - self.sl_c[irate_node],0)
            self.sl_asset[irate_node] += lamda*self.LAMBDA*min(self.val_asset[irate_node] - self.sl_asset[irate_node],0)
        else:
            self.sl_c[irate_node] += lamda*(self.val_c[irate_node] - self.sl_c[irate_node])
            self.sl_asset[irate_node] += lamda*(self.val_asset[irate_node] - self.sl_asset[irate_node])

    def evaluate(self):     
        # evaluate current saving and consumption decision in terms of current consumption level and next period asset
        irate_node = self.irate_node(self.irate)
        if self.asset <= 0:
            print 'negative asset', self.asset
            self.asset = 10
        rho = uniform()**self.gamma
        if not(self.ActionChanged):
            self.val_c[irate_node] += rho*(self.consumption/self.price - self.val_c[irate_node])
            self.val_asset[irate_node] += rho*(self.asset - self.val_asset[irate_node])
        else:
            self.val_c[irate_node] = self.consumption/self.price
            self.val_asset[irate_node] = self.asset


class Firm:

    def __init__(self, bank, TrblActn=0.05, TrbSatLv=0.05, LAMBDA=0.05, gamma=0.5, capital_power=0.4,
                inertia=0.9, delta=0.05, techs=[1, 1], irate_unit=0.005, irate_max=0.1, depreciate=0.05):
        self.TrblActn,self.TrbSatLv,self.LAMBDA, self.gamma, self.inertia = \
            TrblActn, TrbSatLv, LAMBDA, gamma, inertia
        self.capital, self.irate, self.profit, self.delta, self.techs = \
            100, 0, 0, delta, techs
        self.tech = choice(techs)
        self.depreciate = depreciate
        self.capital_power = capital_power
        self.irate_unit, self.irate_max = irate_unit, irate_max
        self.irate_nodes = range(int(irate_max/irate_unit))
        self.capital_demand = 0
        self.SatLv, self.Val = 0, 0
        self.markup = [uniform() for n in self.irate_nodes]
        self.price = [uniform_range(0.9, 1.0) for n in self.irate_nodes]
        self.k = 10
        # self.k = [10 for n in self.irate_nodes]
        self.SatLv = self.Val = [0 for n in self.irate_nodes]
        self.ActionChanged = True

    def irate_node(self, irate):
        irate = min(self.irate_max - self.irate_unit, irate)
        return int(irate/self.irate_unit)        

    def borrow(self, bank):     # set price and announce it to the public
        # self.capital_demand = self.k
        # Tremble = uniform() < self.TrblActn
        # Inertia = uniform() < self.inertia
        # Satisficing = self.Val[irate_node] >= self.SatLv[irate_node]
        # if not(Inertia):
        #     if Tremble or not(Satisficing):
        #         self.k = uniform_range(max(10, self.k*(1-self.delta)), self.k*(1+self.delta))

        # if self.capital_demand != self.k:
        #     self.ActionChanged = True
        # print 'borrow: ', self.capital_power*bank.price*self.tech
        self.capital_demand = (self.irate/(self.capital_power*bank.price*self.tech))**(1/(self.capital_power-1))

    def set_price(self, bank, household):     # set price and announce it to the public
        irate_node = self.irate_node(self.irate)
        self.current_price = self.price[irate_node]
        Tremble = uniform() < self.TrblActn
        Inertia = uniform() < self.inertia
        Satisficing = self.Val[irate_node] >= self.SatLv[irate_node]
        # print 'price range:', self.price[irate_node]*(1-self.delta), self.price[irate_node]*(1+self.delta)
        if not(Inertia):
            if Tremble or not(Satisficing):
                    self.price[irate_node] = uniform_range(self.price[irate_node]*(1-self.delta), self.price[irate_node]*(1+self.delta))
        if self.current_price != self.price[irate_node]:
        # if self.ActionChanged or self.current_price != self.price[irate_node]:            
            self.ActionChanged = True        
        # current_markup = self.markup[irate_node]
        # Tremble = uniform() < self.TrblActn
        # Inertia = uniform() < self.inertia
        # Satisficing = self.Val[irate_node] >= self.SatLv[irate_node]
        # if not(Inertia):
        #     if Tremble or not(Satisficing):
        #         self.markup[irate_node] = uniform_range(max(0, self.markup[irate_node]*(1-self.delta)), self.markup[irate_node]*(1+self.delta))
        # if self.ActionChanged or current_markup != self.markup[irate_node]:
        #     self.ActionChanged = True
        # price = (1+self.markup[irate_node])*(self.irate*self.unit)*(self.capital**(1-self.capital_power))/(self.capital_power*self.tech)
        household.price = bank.price = max(0.01, self.price[irate_node])
        Tremble = uniform() < self.TrbSatLv
        lamda = uniform()**self.gamma
        if not(Tremble):
            self.SatLv[irate_node] += lamda*self.LAMBDA*min(self.Val[irate_node] - self.SatLv[irate_node], 0)
        else:
            self.SatLv[irate_node] += lamda*(self.Val[irate_node] - self.SatLv[irate_node])

    def produce_evaluate(self, bank, household):       # produce to meet demand, calculate profit and evaluate current pricing decision
        irate_node = self.irate_node(self.irate)        
        self.tech = choice(self.techs)
        capacity = bank.price*self.tech*(self.irate/(self.capital_power*bank.price*self.tech))**(self.capital_power/(self.capital_power-1))
        if household.consumption > capacity:
            household.asset += household.consumption - capacity
            household.consumption =  capacity
        self.profit = household.consumption - (self.irate + self.depreciate)*self.capital
        rho = uniform()**self.gamma
        if self.ActionChanged:
            self.Val[irate_node] = self.profit
        else:
            self.Val[irate_node] += rho*(self.profit - self.Val[irate_node])
        # print '2. produce: asset, capital, capacity, profit', household.asset, self.capital, capacity, self.profit


b = Bank(TrblActn=0.01, TrbSatLv=0.01, LAMBDA=0.01)
f = Firm(b, TrblActn=0.01, TrbSatLv=0.01, LAMBDA=0.01)
h = Household(b,f, TrblActn=0.01, TrbSatLv=0.01, LAMBDA=0.01)

Time = 10000

for t in range(Time):
    b.set_interest(h, f)
    if t < 5000:
        b.irate = h.irate = f.irate = 0.05
    else:
        b.irate = h.irate = f.irate = 0.08
    f.borrow(b)
    # if t % 20 == 0:
    f.set_price(b, h)
    h.consume()
    b.channel(h, f)
    f.produce_evaluate(b, h)
    b.transfer_evaluate(h, f)
    # h.evaluate()

data = [b.p, b.f, b.r, b.c, b.i, b.a]
data_name = ['Price', 'Profit', 'Capital' ,'Consumption', 'Nominal Interest', 'Asset']
# fig, ax0 = plt.subplots()
# plot_args = {'markersize' : 8, 'alpha' : 0.6}
# ax0.plot(data[3], label=data_name[3], **plot_args)
# ax0.plot([i*20 for i in data[4]], label=data_name[4], **plot_args)
# ax0.plot(data[5], label=data_name[5], **plot_args)
# ax0.legend(loc='upper left')
# plt.show()
fig, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, figsize=(12, 8))
#fig.tight_layout()
fig.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.2, hspace=0.2)
axes =[ax1, ax2, ax3, ax4, ax5, ax6]
plot_args = {'markersize' : 8, 'alpha' : 0.6}
ylims = [[0, 1.2], [0, 10], [0, 10], [0, 10], [0, 10], [5, 10]]

for i,d in enumerate(data):
    axes[i].set_axis_bgcolor('white')
    axes[i].plot(d)
    #axes[i].plot(d, 'o', markerfacecolor='orange', label=data_name[i], **plot_args)
    #axes[i].legend(loc='upper left')
    axes[i].set_title('{}'.format(data_name[i]))
    if i in [0, ]:
        axes[i].set_ylim(ylims[i])

plt.show()


# blocks = 100
# b_name = ['b_'+i for i in data_name]
# b_data = [[] for i in data_name]

# for j, d in enumerate(data):

#     for i in range(len(d)/blocks):
#         b_data[j].append(sum(d[blocks*i:blocks*(i+1)])/(blocks*1.0))


# fig, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, figsize=(12, 8))
# #fig.tight_layout()
# fig.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.2, hspace=0.2)
# axes =[ax1, ax2, ax3, ax4, ax5, ax6]
# plot_args = {'markersize' : 8, 'alpha' : 0.6}
# ylims = [[0, 100], [-2, 2], [0, 0.5], [0, 100], [0, 0.5], [0, 200000]]

# for i, d in enumerate(b_data):

#     axes[i].set_axis_bgcolor('white')
#     axes[i].plot(d, 'o', markerfacecolor='orange')
#     #axes[i].plot(d, 'o', markerfacecolor='orange', label=data_name[i], **plot_args)
#     #axes[i].legend(loc='upper left')
#     axes[i].set_title('{}'.format(b_name[i]))
#     #axes[i].set_ylim(ylims[i])

# plt.show()
    
# print 'Computation time:', datetime.now()-startTime, 'seconds.'