# Nelson siegel interest-curve
import numpy as np
def NSRate(beta, t, l=0.7308):
    rate = beta[0] + beta[1]*( (1-np.exp(-l*t))/(l*t+0.000000000001) ) + beta[2] * ( ((1-np.exp(-l*t))/(l*t+0.000000000001)) - np.exp(-l*t) )
    return rate
