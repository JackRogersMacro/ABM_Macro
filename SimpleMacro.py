"""
Simple Macroeconomic Model with Satisficing Behaviour
Authors: Hyun Chang Yi and Sarunas Girdenas
LastModified: 04/06/2014
"""
from datetime import datetime # import this to calculate script execution time
startTime=datetime.now()

from random import randrange, choice, randint
from numpy.random import uniform
from math import sqrt
import matplotlib.pyplot as plt
from numpy import array, abs, histogram
from scipy import mean
from math import log


#In this model we have three types of agents: Households, Firms and Central Bank

#Here we define Market for a Firm and a Household
class Bank:

    def __init__(self,TrblProbAction=0.05,TrblProbSatLv=0.05,Lambda=0.05,gamma=0.5,inertia=0.5,interest=10,Periods=2,StepSize=10,initial_interest=10):
        self.TrblProbAction,self.TrblProbSatLv,self.Lambda, self.gamma, self.inertia = TrblProbAction,TrblProbSatLv,Lambda, gamma, inertia
        self.Wfr, self.Stbl, self.liquidity, self.interest, self.recent_prices, self.StepSize = 0, 0, 0, interest, [1 for t in range(Periods)], StepSize
        self.inflation = log(self.recent_prices[-1])-log(self.recent_prices[-2])
        self.SatLvWfr, self.SatLvStbl, self.ValWfr, self.ValStbl = 0, 0, 0, 0
        self.ActionChanged = True
        self.initial_interest = initial_interest
        
    def set_interest(self,household,firm,alpha_i=0.5,alpha_infl=0.5): 
        # Set nominal interest rate as 0,1,2,...,i,i+1,... where  i stands for 0.1*i percent and announce to the public
        self.inflation = log(self.recent_prices[-1])-log(self.recent_prices[-2])
        CurrentRate = self.interest
        self.alpha_i, self.alpha_infl = alpha_i, alpha_infl # Policy maker preferences in Taylor rules
        Tremble = uniform() < self.TrblProbAction
        Inertia = uniform() < self.inertia
        Satisficing_Wfr = self.ValWfr >= self.SatLvWfr
        Satisficing_Stbl = self.ValStbl >= self.SatLvStbl
        if not(Inertia):
            if not(Tremble):
                if (not(Satisficing_Wfr) or not(Satisficing_Stbl)):
                        if t == 0:
                            self.interest = initial_interest
                        else: 
                            self.interest = max(0,alpha_i*household.cons+alpha_infl*(self.inflation)) # Rule for random choice randint(max(0, self.interest - self.StepSize), self.interest + self.StepSize)                  
            else:
                    if t == 0:
                        self.interest = initial_interest
                    else: 
                        self.interest = max(0,alpha_i*household.cons+alpha_infl*self.inflation) # Rule for random choice     randint(max(0, self.interest - self.StepSize), self.interest + self.StepSize)

        if CurrentRate == self.interest:
            self.ActionChanged = False

        Tremble = uniform() < self.TrblProbSatLv
        lamda = uniform()**self.gamma

        if not(Tremble):
            self.SatLvWfr += lamda*self.Lambda*min(self.ValWfr - self.SatLvWfr, 0)
            self.SatLvStbl += lamda*self.Lambda*min(self.ValStbl - self.SatLvStbl, 0)
        else:
            self.SatLvWfr += lamda*(self.ValWfr-self.SatLvWfr)
            self.SatLvStbl += lamda*(self.ValStbl-self.SatLvStbl)

        household.interest, firm.interest = self.interest, self.interest

    def channel(self,household,firm): # borrow money from household and lend it to firm
        self.liquidity = household.saving
        firm.captial = self.liquidity

    def transfer_evaluate(self,household,firm): 
        # pay return from deposit and profit from firm to household
        household.asset = (1 + self.interest/1000.0)*self.liquidity + firm.profit

        # evaluate current economy in terms of consumption level and price volatility
        self.Wfr = household.cons
        self.Stbl = -(firm.price - mean(self.recent_prices))**2
        self.recent_prices.pop(0)
        self.recent_prices.append(firm.price)        

        rho = uniform()**self.gamma
        if not(self.ActionChanged):
            self.ValWfr += rho*(self.Wfr - self.ValWfr)
            self.ValStbl += rho*(self.Stbl - self.ValStbl)
        else:
            self.ValWfr, self.ValStbl = self.Wfr, self.Stbl


class Household:

    def __init__(self,TrblProbAction=0.05,TrblProbSatLv=0.05,Lambda=0.05,gamma=0.5,inertia=0.5,asset=1000, cons=20, StepSize=10):
        self.TrblProbAction,self.TrblProbSatLv,self.Lambda, self.gamma, self.inertia = TrblProbAction,TrblProbSatLv,Lambda, gamma, inertia
        self.asset, self.price, self.cons, self.saving, self.interest, self.StepSize = asset, 0, cons, 0, 0, StepSize
        self.SatLvCons, self.ValCons, self.SatLvAsset, self.ValAsset = 0, 0, 0, 0
        self.ActionChanged = True

    def consume(self):       # choose how much to consume and save
        current_cons = self.cons
        Tremble = uniform() < self.TrblProbAction
        Inertia = uniform() < self.inertia
        Satisficing_Cons = self.ValCons >= self.SatLvCons
        Satisficing_Asset = self.ValAsset >= self.SatLvAsset
        if not(Inertia):
            if not(Tremble):
                if (not(Satisficing_Cons) and Satisficing_Asset):
                    self.cons = randint(self.cons, min(self.asset, self.cons + self.StepSize))
                elif (Satisficing_Cons and not(Satisficing_Asset)):
                    self.cons = randint(max(0, self.cons - self.StepSize), self.cons)
                elif (not(Satisficing_Cons) and not(Satisficing_Asset)):
                    self.cons = randint(max(0, self.cons - self.StepSize), min(self.asset, self.cons + self.StepSize))
            else:
                self.cons = randint(max(0, self.cons - self.StepSize), min(self.asset, self.cons + self.StepSize))

        self.cons = min(self.cons, self.asset//self.price)

        if current_cons == self.cons:
            self.ActionChanged = False

        self.saving = self.asset - self.cons

        Tremble = uniform() < self.TrblProbSatLv
        lamda = uniform()**self.gamma
        if not(Tremble):
            self.SatLvCons += lamda*self.Lambda*min(self.ValCons - self.SatLvCons,0)
            self.SatLvAsset += lamda*self.Lambda*min(self.ValAsset - self.SatLvAsset,0)
        else:
            self.SatLvCons += lamda*(self.ValCons - self.SatLvCons)
            self.SatLvAsset += lamda*(self.ValAsset - self.SatLvAsset)

    def evaluate(self):     # evaluate current saving and consumption decision in terms of current consumption level and next period asset

        if self.asset <= 0:
            print 'negative asset', self.asset
            self.asset = 10

        rho = uniform()**self.gamma
        if not(self.ActionChanged):
            self.ValCons += rho*(self.cons - self.ValCons)
            self.ValAsset += rho*(self.asset - self.ValAsset)
        else:
            self.ValCons = self.cons
            self.ValAsset = self.asset

class Firm:

    def __init__(self,TrblProbAction=0.05,TrblProbSatLv=0.05,Lambda=0.05,gamma=0.5,inertia=0.5, price=10, StepSize=10, techs=[0.1, 0.1]):
        self.TrblProbAction,self.TrblProbSatLv,self.Lambda, self.gamma, self.inertia = TrblProbAction,TrblProbSatLv,Lambda, gamma, inertia
        self.captial, self.price, self.interest, self.profit, self.StepSize, self.techs = 0, price, 0, 0, StepSize, techs
        self.SatLv, self.Val = 0, 0
        self.ConsChanged = True

    def set_price(self,household,bank):     # set price and announce it to the public
        current_price = self.price
        Tremble = uniform() < self.TrblProbAction
        Inertia = uniform() < self.inertia
        Satisficing = self.Val >= self.SatLv
        if not(Inertia):
            if not(Tremble):
                if not(Satisficing):
                    self.price = randint(max(1, self.price - self.StepSize), self.price + self.StepSize)
            else:
                self.price = randint(max(1, self.price - self.StepSize), self.price + self.StepSize)

        if current_price == self.price:
            self.ActionChanged = False

        household.price, bank.price = self.price, self.price

        Tremble = uniform() < self.TrblProbSatLv
        lamda = uniform()**self.gamma
        if not(Tremble):
            self.SatLv += lamda*self.Lambda*min(self.Val-self.SatLv,0)
        else:
            self.SatLv += lamda*(self.Val - self.SatLv)

    def produce_evaluate(self,household):       # produce to meet demand, calculate profit and evaluate current pricing decision
        tech = choice(self.techs)
        self.profit = self.price*household.cons - (self.interest/1000.0)*self.captial - tech*self.price*(household.cons**2)/((self.captial**(0.1))*1.0)
        
        rho = uniform()**self.gamma
        if not(self.ActionChanged):
            self.Val += rho*(self.profit - self.Val)
        else:
            self.Val = self.profit

b = Bank()
h = Household()
f = Firm()

Time = 90000

p=[]
i=[]
c=[]
a=[] # in the real term
pi=[]

for t in range(Time):
    b.set_interest(h,f)
    f.set_price(h,b)
    h.consume()
    b.channel(h,f)
    f.produce_evaluate(h)
    b.transfer_evaluate(h,f)
    h.evaluate()

    p.append(f.price)
    i.append(b.interest)
    c.append(h.cons)
    a.append(h.asset//f.price)
    if t > 1:
        pi.append(log(p[t])-log(p[t-1]))


data = [pi,i,c,a]
data_var = ['inflation','interest','consumption','asset']

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
#fig.tight_layout()
fig.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.2, hspace=0.2)

axes =[ax1,ax2,ax3,ax4]
plot_args = {'markersize' : 8, 'alpha' : 0.6}

ylims = [[-.5,.5],[0,30],[0,60],[0,200000]]

for i,d in enumerate(data):

    axes[i].set_axis_bgcolor('white')
    axes[i].plot(d, 'o', markerfacecolor='orange', **plot_args)
    axes[i].legend(loc='upper left')
    axes[i].set_title('{}'.format(data_var[i]))
    axes[i].set_ylim(ylims[i])

plt.show()


    
print 'Computation time:', datetime.now()-startTime, 'seconds.'




