import math
from scipy.stats import norm, chi2

'''
Mean and variance for a set of rating frequencies
'''
def compute_stats(ratings):
    N = sum(ratings)
    if N == 0:
        return 0, 0
    average = sum([0.5 * (i + 1) * r for i, r in enumerate(ratings)]) / N
    variance = sum( r * ((0.5 * (i + 1) - average) ** 2) for i, r in enumerate(ratings)) / N

    return average, variance


'''
Extremeness value of a rating is a value between 0 - 1 which reflects
what percentage of users rated at least as far from the mean as the given score.
'''
def extremeness(score, ratings):
    if sum(ratings) == 0:
        # This is a hack, but for some movies the letterboxd page just doesn't display 
        # the histogram. So then the ratings are all set to zeros. 
        # Given the low frequency of this behaviour, we can just return 1.0 as 
        # the extrememness without too much problem.
        return 1.0
    average, _ = compute_stats(ratings)
    ex = 0
    for i, r in enumerate(ratings):
        if (i + 1) == (score * 2):
            ex += (r // 2)
        elif abs((0.5 * (i + 1)) - average) > abs(score - average):
            ex += r
    if ex == 0:
        print("Extrememness value is 0!", score, ratings)
    return ex / sum(ratings)


def extremeness_percentile(value):
    return norm.cdf(value, 0.52, 0.095)


def is_contrarian(ratings, alpha):
    x2 = -2 * sum(math.log(p[0]) for p in ratings)
    crit_val = chi2.ppf(1 - alpha, 2 * len(ratings))
    p_val = 1 - chi2.cdf(x2, 2 * len(ratings))
    return p_val, x2, crit_val