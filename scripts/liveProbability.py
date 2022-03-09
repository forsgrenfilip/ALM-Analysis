# survival function
import numpy as np
def liveProbability(startAge, endAge, parameters):

    alpha = parameters[0]
    beta = parameters[1]
    gamma = parameters[2]

    liveProb = (
                (np.exp(-alpha*endAge  -(beta/gamma)*(np.exp(gamma*endAge  )-1))) /
                (np.exp(-alpha*startAge-(beta/gamma)*(np.exp(gamma*startAge)-1)))
                )
    return liveProb