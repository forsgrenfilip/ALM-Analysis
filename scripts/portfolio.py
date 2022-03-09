# Portfoilio handler
import numpy as np
class portfolio(object):

    def __init__(self, values, time, scenario, strategy= 'stocksOnly', wheights='even', duration=False):

    #### Declare local varaibles

        self.values = values
        self.time = time
        self.scenario = scenario
        self.stocks = scenario.stocks
        self.bonds = scenario.bonds
        self.bondDuration = []
        for b in self.bonds:
            try:
                self.bondDuration.append(int(b[-2:]))
            except:
                pass
        self.stockLogReturns = scenario.stockLogReturns
        self.bondLogReturns = scenario.bondLogReturns
        self.strategy = strategy
        self.wheights = wheights
        self.duration = duration


    #### Call update

    def updateValues(self):
        if self.strategy == 'stocksOnly':
            self.values = self.stocksOnly()
        elif self.strategy == 'a':
            self.updateA()
        elif self.strategy == 'b':
            self.values = self.updateB()
        elif self.strategy == 'c':
            self.values = self.updateC()
        elif self.strategy == 'd':
            self.values = self.updateD()

    #### Call rebalance

    def rebalance(self, cf=0):
        if self.strategy == 'stocksOnly':
            self.stocksOnlyRebalance(cf)
        elif self.strategy == 'a':
            self.rebalanceA(cf)
        elif self.strategy == 'b':
            self.rebalanceB(cf)
        elif self.strategy == 'c':
            self.rebalanceC(cf)
        elif self.strategy == 'd':
            self.rebalanceD(cf)



    #### UPDATE VALUES

    def stocksOnly(self):
        if len(self.values) == len(self.stocks):
            values = self.values
        else:
            print(f'lenght of values {len(self.values)} does not match lenght of investments {len(self.stocks)}.')
        i = 0
        if self.time == -1:
            pass
        else:
            for s in self.stocks:
                values[i] = values[i]*np.exp(self.stockLogReturns[s].iloc[self.time])
                i+=1
        return values

    def updateA(self):
        if self.time == -1:
            pass
        else:
            self.values = self.values*np.exp(self.bondLogReturns['Y15'].iloc[self.time])
        return

    def updateB(self):
        if len(self.values) == len(self.stocks) + 1:
            values = self.values
        else:
            print(f'lenght of values {len(self.values)} does not match lenght of investments {len(self.stocks) +1}.')
        i = 0
        if self.time == -1:
            pass
        else:
            for s in self.stocks:
                values[i] = values[i]*np.exp(self.stockLogReturns[s].iloc[self.time])
                i+=1
            values[-1] = values[-1]*np.exp(self.bondLogReturns['Y05'].iloc[self.time])
        return values

    def updateC(self):
        if len(self.values) == len(self.stocks) + 1:
            values = self.values
        else:
            print(f'lenght of values {len(self.values)} does not match lenght of investments {len(self.stocks) +1}.')
        i = 0
        if self.time == -1:
            pass
        else:
            for s in self.stocks:
                values[i] = values[i]*np.exp(self.stockLogReturns[s].iloc[self.time])
                i+=1
            values[-1] = values[-1]*np.exp(self.bondLogReturns['Y05'].iloc[self.time])
        return values

    def updateD(self):
        if len(self.values) == len(self.stocks) + 1:
            values = self.values
        else:
            print(f'lenght of values {len(self.values)} does not match lenght of investments {len(self.stocks) +1}.')
        i = 0
        if self.time == -1:
            pass
        else:
            for s in self.stocks:
                values[i] = values[i]*np.exp(self.stockLogReturns[s].iloc[self.time])
                i+=1
            if not self.duration:
                print('specify wanted duration of bond investment when initializing portfolio object, using duration=<int object>')
            else:
                high = next(x[0] for x in enumerate(self.bondDuration) if x[1] > self.duration)
                low = high - 1
                wLow = (self.bondDuration[high]-self.duration)/(self.bondDuration[high]-self.bondDuration[low])
                wHigh = 1 - wLow
                bondsValue = values[-1]
                values[-1] = bondsValue*wLow*np.exp(self.bondLogReturns[self.bonds[low]].iloc[self.time])
                values[-1] += bondsValue*wHigh*np.exp(self.bondLogReturns[self.bonds[high]].iloc[self.time])
        return values



    #### REBALANCE

    def stocksOnlyRebalance(self, cf):
        self.values = self.values + (cf/len(self.stocks))
        return

    def rebalanceA(self, cf):
        self.values = self.values + cf
        return

    def rebalanceB(self, cf):
        if cf > 0:
            self.values[:10] = self.values[:10] + (cf/2)/len(self.stocks)
            self.values[-1] = self.values[-1] + cf/2
        else:
            for i in range(len(self.values)):
                ratio = self.values[i]/np.sum(self.values)
                self.values[i] = self.values[i] + (cf*ratio)
        return

    def rebalanceC(self, cf):
        value = sum(self.values) + cf
        for i in range(len(self.stocks)):
            self.values[i] =  (value/2)/len(self.stocks)
        self.values[-1] = (value/2)
        return

    def rebalanceD(self, cf):
        value = sum(self.values) + cf
        for i in range(len(self.stocks)):
            self.values[i] =  (value/2)/len(self.stocks)
        self.values[-1] = (value/2)
        return