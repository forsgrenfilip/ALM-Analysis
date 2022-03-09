# Scenario handler
import numpy as np
class scenarioHandler(object):
    def __init__(self, df, estNS=False, l=0.7308):
        self.data = df
        self.periods = np.arange(df['Period'].min(),df['Period'].max()+1,1)
        try:
            self.scenario = np.arange(df['Scenario'].min(),df['Scenario'].max()+1,1)
        except:
            pass
        self.stocks = df.columns[2:12]
        self.bonds = df.columns[12:17]
        self.bondDuration = []
        for b in self.bonds:
            try:
                self.bondDuration.append(int(b[-2:]))
            except:
                pass

        if estNS:
            NSParameters = np.array([])
            M = []
            for t in self.bondDuration:
                M.append([1,(1-np.exp(-l*t))/(l*t+0.0000001),((1-np.exp(-l*t))/(l*t+0.0000001)) - np.exp(-l*t)])
            M = np.array(M)
            for p in range(len(self.periods)):
                R = []
                for t in range(len(self.bondDuration)):
                    R.append(df[self.bonds[t]].iloc[p])
                R = np.array(R)
                NSParameters = np.append(NSParameters,np.matmul(np.matmul(np.linalg.inv(np.matmul(M.T,M)),M.T),R))
            self.NSParameters = NSParameters.reshape(-1, 3)

            # Bond values
            for t in range(len(self.bondDuration)):
                zcbValue = []
                for p in range(len(self.periods)):
                    zcbValue.append(100/pow(1+df[self.bonds[t]].iloc[p],self.bondDuration[t]))
                df[self.bonds[t]] = zcbValue
                df['b1'] = self.NSParameters[:,0]
                df['b2'] = self.NSParameters[:,1]
                df['b3'] = self.NSParameters[:,2]

        else:
            self.NSParameters = self.data[df.columns[17:20]].to_numpy()

        self.stockLogReturns = np.log(df[self.stocks]).diff().dropna()
        self.bondLogReturns = np.log(df[self.bonds]).diff().dropna()

    def split(self):
        self.scenarioArray = []
        for i in self.scenario:
            self.scenarioArray.append(scenarioHandler(self.data[(self.data['Scenario'] == i)]))
        return