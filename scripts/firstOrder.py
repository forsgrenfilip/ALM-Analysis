# First Order Dept
import numpy as np
from liveProbability import liveProbability
from makehamPensionPopulationEvolution import makehamPensionPopulationEvolution
from NSRate import NSRate
class firstOrder(object):

    def __init__(self, G0, age0, makehamParameters, maxT=360, z=65, s=120, PPAmount=10000, discountRate=-.02, guaranteedRate=0.02):

        self.G0 = G0
        self.age0 = age0
        self.makehamParameters = makehamParameters

        self.maxT = maxT
        self.z = z
        self.s = s
        self.PPAmount = PPAmount
        self.discountRate = np.log(1+discountRate)/12
        self.guaranteedRate = np.log(1+guaranteedRate)/12

        self.b = self.getFirstPayout()/12
        self.reserve = self.getFirstReserves()
        self.expReserve = self.getExpFirstOrderReserve()

        self.cf = self.getCF()
        
    def getFirstPayout(self):
        ## PP:
        ages = np.arange(self.age0, self.z, 1/12)
        t = 1
        scaling = 0
        for age in ages:
            scaling += liveProbability(self.age0,age+(1/12),self.makehamParameters) * np.exp(-self.guaranteedRate*t)
            t += 1
        G = self.G0 + self.PPAmount * scaling

        ## PO:
        ages = np.arange(self.z,self.s,1/12)
        scaling = 0
        for age in ages:
            scaling += liveProbability(self.age0,age+(1/12),self.makehamParameters) * np.exp(-self.guaranteedRate*t)
            t += 1

        b = G / (scaling/12)
        return b

    def getFirstReserves(self):

        reserves = np.zeros((self.s-self.age0)*12+1)
        reserves[0] = self.G0
        ages = np.arange(self.age0,self.s,(1/12))
        i = 1

        for age in ages:
            #PP
            if age < self.z:
                q = 1 - liveProbability(age,age+(1/12),self.makehamParameters)
                riskPremium = reserves[i-1]*np.exp(self.guaranteedRate)*(q/(1-q))
                reserves[i] = reserves[i-1]*np.exp(self.guaranteedRate) + self.PPAmount + riskPremium

            #PO
            else:
                q = 1 - liveProbability(age,age+(1/12),self.makehamParameters)
                riskPremium = reserves[i-1]*np.exp(self.guaranteedRate)*(q/(1-q))
                reserves[i] = reserves[i-1]*np.exp(self.guaranteedRate) - self.b + riskPremium
            i += 1
            
        return reserves[:self.maxT]

    def getExpFirstOrderReserve(self):

        expFirstOrderReserve = np.zeros(len(self.reserve))
        population = makehamPensionPopulationEvolution(self.age0,self.s,self.makehamParameters)
        populations = population.populationEvolution
        for i in range(len(self.reserve)):
            expFirstOrderReserve[i] = np.sum(populations[i,[0,3]]) * self.reserve[i]
        return expFirstOrderReserve

    def getCF(self):

        cf = np.zeros((self.s-self.age0)*12+1)
        ages = np.arange(self.age0,self.s,(1/12))
        population = makehamPensionPopulationEvolution(self.age0,self.s,self.makehamParameters)
        populations = population.populationEvolution
        moveProb = population.moveProb
        i = 0

        for age in ages:
            #PP
            if age < self.z:
                cf[i] = -self.PPAmount*populations[i,0] + self.reserve[i]*moveProb
            #PO
            else:
                cf[i] = self.b*populations[i,3]

            i += 1
            
        return cf

    def getBE(self, scenario=0, horizon=720, dur=False, yearFraction=12):

        if scenario == 0:
            rate = self.discountRate
            BE = np.zeros(self.maxT)
            D_t0 = 0
            D_n0 = 0
            D_t120 = 0
            D_n120 = 0
            for t in range(len(BE)):
                for i in range(t,horizon):
                    BE[t] += self.cf[i] * np.exp(-np.log(1 + rate) * (i-t)/12)
                    if t == 0:
                        D_t0 += self.cf[i] * np.exp(-np.log(1 + rate) * (i-t)/12) * (i-t)
                        D_n0 += self.cf[i] * np.exp(-np.log(1 + rate) * (i-t)/12)
                    if t == self.maxT-1:
                        D_t120 += self.cf[i] * np.exp(-np.log(1 + rate) * (i-t)/12) * (i-t)
                        D_n120 += self.cf[i] * np.exp(-np.log(1 + rate) * (i-t)/12)
            self.be = BE
            D0 = D_t0/D_n0
            D120 = D_t120/D_n120
            self.beD = ((D0+D120))/2/12

        else:
            BE = np.zeros(self.maxT)
            if dur:
                D = np.zeros(self.maxT)
            for t in range(len(BE)):
                try:
                    beta = scenario.NSParameters[t]
                except:
                    beta = -np.log(1.02)/12 #scenario.NSParameters[-1]
                if dur:
                    D_t = 0
                    D_n = 0
                for i in range(t,horizon):
                    rate = NSRate(beta,(i+1)/yearFraction)
                    if rate < -0.01:
                        rate = -0.01
                    BE[t] += self.cf[i] * np.exp(-np.log(1 + rate) * (i-t)/12)
                    if dur:
                        D_t += self.cf[i] * np.exp(-np.log(1 + rate) * (i-t)/12) * (i-t)
                        D_n += self.cf[i] * np.exp(-np.log(1 + rate) * (i-t)/12)
                if dur:
                    D[t] = (D_t/D_n)/12
                
            self.be = BE
            if dur:
                self.beD = D
        return

    def getBE2(self, scenario=0, lenght=120):
        
        Tau = np.arange(1,721,1)
        BE = np.zeros(lenght)

        for i in range(len(BE)):
            betas = scenario.NSParameters[i]
            cf = self.cf[i:-1]
            l = 0.7308 / 12
            r = np.zeros(len(cf))
            bestEst = np.zeros(len(cf))
            tau = Tau[0:len(Tau)-i]
            r = betas[0] + betas[1] * ((1 - np.exp(- l * tau))/ (l * tau)) + betas[2] * (((1 - np.exp(- l * tau))/ (l * tau))- np.exp(- l * tau))
            r[r < -0.01] = -0.01
            bestEst[:] = cf[:] * np.exp(-np.log(1 + r) * tau/12)
            BE[i] = sum(bestEst)
        
        self.be = BE
        return 