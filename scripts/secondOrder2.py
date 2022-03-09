import copy
import numpy as np
from liveProbability import liveProbability
from makehamPensionPopulationEvolution import makehamPensionPopulationEvolution
from NSRate import NSRate
class secondOrder2(object):

    def __init__(self, V0, age0, makehamParameters, portfolio, firstOrderReserve, maxT=360, z=65, s=120, b=14042.115533443966, PPAmount=10000, discountRate=-.02, guaranteedRate=0.02):

        self.V0 = V0
        self.age0 = age0
        self.makehamParameters = makehamParameters
        self.portfolio = copy.deepcopy(portfolio)
        self.assetPortfolio = copy.deepcopy(portfolio)
        self.firstOrderReserve = firstOrderReserve

        self.maxT = maxT
        self.z = z
        self.s = s
        self.b = b
        self.PPAmount = PPAmount
        self.discountRate = np.log(1+discountRate)/12
        self.guaranteedRate = np.log(1+guaranteedRate)/12

        population = makehamPensionPopulationEvolution(self.age0,self.s,self.makehamParameters)
        self.populations = population.populationEvolution
        self.moveProb = population.moveProb

        self.reserve, self.assets = self.getReserves()
        self.expSecondOrderReserve = self.getExpReserve()

    def getP(self, age, value):
        #PP
        if age < self.z:
            q = 1 - liveProbability(age,age+(1/12),self.makehamParameters)
            riskPremium = value*np.exp(self.guaranteedRate)*(q/(1-q))
            p = self.PPAmount + riskPremium

            B = 0
        #PO
        else:
            q = 1 - liveProbability(age,age+(1/12),self.makehamParameters)
            riskPremium = value*np.exp(self.guaranteedRate)*(q/(1-q))
            
            scaleAge = np.arange(age,self.s,(1/12))
            scale = 0
            t = 0
            for a in scaleAge:
                beta = self.portfolio.scenario.NSParameters[min(t,self.maxT)]
                rate = -np.log(1.02)/12 #  np.log(1-NSRate(beta,t/12))/12
                liveProb = liveProbability(age,a+(1/12),self.makehamParameters)
                scale += np.exp(rate*t) * liveProb
                t+=1

            B = value/scale
            if B < self.b:
                B = self.b
            p = -B + riskPremium

        return p, B

    def getReserves(self):
        if self.portfolio == 0:
            print('Portfolio needs to be defined')
        ages = np.arange(self.age0,self.s, 1/12)
        reserve = np.zeros(len(ages)+1)
        assets = np.zeros(len(ages)+1)
        assets[0] = self.V0
        reserve[0] = self.V0
        t = 0

        for age in ages:
            self.portfolio.time = t
            self.portfolio.updateValues()
            values = self.portfolio.values
            value = np.sum(values)
            p,B = self.getP(age,value)
            reserve[t+1] = value + p
            self.portfolio.rebalance(p)
            
            self.assetPortfolio.time = t
            self.assetPortfolio.updateValues()
            values = self.assetPortfolio.values
            value = np.sum(values)
            cf = self.getCF(age,value,t,B)
            assets[t+1] = value + cf
            self.assetPortfolio.rebalance(cf)
            
            t+=1
            if t >= self.maxT:
                break
        return reserve[:self.maxT], assets[:self.maxT]

    def getExpReserve(self):
        expSecondOrderReserve = np.zeros(len(self.reserve))
        population = makehamPensionPopulationEvolution(self.age0,self.s,self.makehamParameters)
        populations = population.populationEvolution
        for i in range(len(self.reserve)):
            expSecondOrderReserve[i] = np.sum(populations[i,[0,3]]) * self.reserve[i]
        return expSecondOrderReserve

    def getCF(self, age, value, i, B):
        #PP
        if age < self.z:
            cf = self.PPAmount*self.populations[i,0] -  value*self.moveProb #eller self.firstOrderReserve[i]?
        #PO
        else:
            cf = -B*self.populations[i,3]
        return cf