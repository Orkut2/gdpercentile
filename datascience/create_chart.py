import numpy as np
import pandas as pd
import matplotlib.pyplot as mpl
from math import log

# create pandas series
# columns: rank, accum_victors

total_victors = np.array([],dtype=int)

with open("victors.txt", "r") as file:
    for line in file:
        try:
            total_victors = np.concatenate(( total_victors, [total_victors[-1] + int(line)] ))
        except:
            total_victors = np.concatenate(( total_victors, [int(line)] ))

print(total_victors)

# fitting only ranks 11-150 because the top 10 have such noisy data that they mess with the results

def logpower(a,b):
    return np.array([ (a * log(x)**b) for x in range(11,151) ])

def fit_error(test_curve):
    errors = np.array( test_curve - total_victors[10:] )
    if min(errors) < 0:
        return np.inf
    return sum(np.array( errors**2 ))/len(errors)


#recursively zoom in by a factor of 3 toward the minimum (because 3 is odd so it has a center)

coarse=3
map_size = 3**coarse

#start at 0-9 on both axes
a_center = 4.5
b_center = 4.5
scale = 9/map_size

spread = np.inf
while spread >= 0.1: #change this value to require better or faster fit
    best_so_far = np.inf
    best_i = 0
    best_j = 0
    
    error_map = np.zeros((1 + map_size,1 + map_size))
    a_bound = a_center - (map_size/2)*scale
    b_bound = b_center - (map_size/2)*scale

    i=0
    j=0
    while i<=map_size:
        while j<=map_size:
            error_map[i][j] = fit_error( logpower(a_bound + i*scale , b_bound + j*scale) )
            if error_map[i][j] < best_so_far:
                best_so_far = error_map[i][j]
                best_i = i
                best_j = j
            j+=1
        j=0
        i+=1

    finite_errors = error_map[np.isfinite(error_map)] #the best fit that doesn't go under by definition is on the edge, so no amount of zooming will ever eliminate infs
    spread = max(finite_errors) - min(finite_errors)
    a_center = a_bound + best_i*scale
    b_center = b_bound + best_j*scale
    scale *= 1/3

a = a_center
b = b_center
print(f"a = {a} ; b = {b} ; error = {fit_error(logpower(a,b))}")
best_estimate = logpower(a,b)

mpl.plot( range(11,151) , total_victors[10:] )
mpl.plot( range(11,151) , best_estimate )
mpl.savefig("local_fit.png")

# algorithm to find the best fit log-power law
# because players typically jump in layers of 2/3 - 1/3 of their current hardest's rank
# and there's exponential decay on how many of them succeed
mpl.figure()
mpl.xlim(0,2000)
number_of_extreme_demons = 1620
extrapolation = np.array([ (a*log(x)**b) for x in range(11,2001) ])
mpl.plot( range(11,151) , total_victors[10:] )
mpl.plot( range(11,2001) , extrapolation )
final_estimate = int(round(a * log(number_of_extreme_demons)**b))
mpl.plot( [number_of_extreme_demons, number_of_extreme_demons] , [0, max(extrapolation)] )
mpl.text(number_of_extreme_demons, final_estimate, f" {final_estimate}")
print(f"Final estimate for the number of people who have beat an extreme demon: {final_estimate}")
mpl.savefig("victors_extrapolation.png")
