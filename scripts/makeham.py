import numpy as np
import scipy.optimize as optimize

class makeham(object):
       
    def __init__(self, estFOM, ages, gamma=0.12):
        self.ages = ages
        self.estFOM = estFOM
        self.parameters = self.optParams(self.estFOM, gamma)

    def sqrError(self,gamma):
        m = np.sum(self.estFOM)
        g = 0
        f1 = 0
        f2 = 0

        for i in range(len(self.ages)):
            g += self.estFOM[i] * np.exp(gamma*self.ages[i])
            f1 += np.exp(gamma*self.ages[i])
            f2 += np.exp(2*gamma*self.ages[i])
        
        alpha = (m*f2 - g*f1)/(len(self.ages)*f2-np.square(f1))
        beta = (m*f1 - len(self.ages)*g)/(np.square(f1)-len(self.ages)*f2)

        sumSqrError = 0
        for i in range(len(self.estFOM)):
            sumSqrError += np.square(self.estFOM[i] - (alpha + beta*np.exp(gamma*(self.ages[i]))))
        return sumSqrError

    def optParams(self, estFOM, gamma):

        opt = optimize.minimize(self.sqrError, gamma)
        gamma = opt.x[0]

        m = np.sum(self.estFOM)
        g = 0
        f1 = 0
        f2 = 0

        for i in range(len(self.ages)):
            g += self.estFOM[i] * np.exp(gamma*self.ages[i])
            f1 += np.exp(gamma*self.ages[i])
            f2 += np.exp(2*gamma*self.ages[i])
        
        alpha = (m*f2 - g*f1)/(len(self.ages)*f2-np.square(f1))
        beta = (m*f1 - len(self.ages)*g)/(np.square(f1)-len(self.ages)*f2)

        parameters = [alpha, beta, gamma]
        return parameters