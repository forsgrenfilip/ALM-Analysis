# Population
import numpy as np
from liveProbability import liveProbability
class makehamPensionPopulationEvolution(object):
    
    def __init__(self, startAge, endAge, makehamParameter, pensionAge=65, moveProb=.0016821426, step=1/12, initalPopulation=[1,0,0,0]):
        self.makehamParameter = makehamParameter
        self.moveProb = moveProb
        self.step = step
        self.pensionAge = pensionAge
        self.steps = np.arange(startAge,endAge,step)
        self.populationEvolution = self.popEv(initalPopulation)

    def transitionMatrix(self, age):

        PPtoDE = 1 - liveProbability(age, age+self.step, self.makehamParameter)

        if age < self.pensionAge:
            PPtoOUT = (1 - PPtoDE)*self.moveProb
        else:
            PPtoOUT = 0

        PPtoPP = 1 - PPtoDE - PPtoOUT
        matrix = np.array(([PPtoPP,0,0],[PPtoDE,1,0],[PPtoOUT,0,1]))
        return matrix    

    def popEv(self, initalPopulation ):
        populations = np.zeros((len(self.steps)+1,len(initalPopulation)))
        populations[0] = initalPopulation

        i = 0
        for age in self.steps:
            matrix = self.transitionMatrix(age)
            populations[i+1,:3] = np.matmul(matrix,populations[i,:3])
            if age > self.pensionAge:
                populations[i,3] = populations[i,0]
                populations[i,0] = 0
            i+=1

        return populations