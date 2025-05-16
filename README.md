# Film Tools

Tools to analyse Letterboxd profiles. Alongside functions to scraper Letterboxd data, such as movie ratings 
distributions and user ratings, there are a variety of statistical tools.
For a given rating, it is possible to compute what proportion of people rated a movie at least as far from the mean rating
as the user, using `stats.extremeness()`. This proportion is the _extremeness_ value. For a given user, the average
extremeness across all their ratings can be computed.

An empirical distribution for the average extremeness value across a sample of users was computed, and fitted to a Normal(0.52, 0.095)
distribution, allowing for a measure of what proportion of users a given user is more contrarian than.
This is the function `stats.extremeness_percentile()`.

Finally, a hypothesis test is performed by `stats.is_contrarian()` to check whether a given user is contrarian in their opinions.
Each movie rating is treated as an independent test, with the extremeness for the movie treated as its p-value. 
These are combined into a meta-analysis using [Fisher's method](https://en.wikipedia.org/wiki/Fisher%27s_method), to check whether
their is sufficient evidence to reject the null hypothesis that a user's opinions are largely in line with the wider population.

Summary functions are given in `scripts.py`.

Example usage:
```
import scripts

scripts.user_analysis('USER HERE')
```

Example output:
```
p-value is 0.9999796715699255
Insufficient evidence to reject null.
=======================================
Most controversial:
[Movie], [User rating], [Average], [Extremeness]
ghost-world : 1.0 , 3.6 , 1.0 %
the-rocky-horror-picture-show : 2.0 , 4.06 , 3.0 %
past-lives : 3.0 , 4.17 , 8.0 %
ponyo : 3.0 , 4.15 , 8.0 %
raiders-of-the-lost-ark : 3.0 , 4.13 , 8.0 %
nosferatu-2024 : 2.5 , 3.77 , 8.0 %
arrival-2016 : 3.0 , 4.09 , 10.0 %
being-john-malkovich : 5.0 , 3.99 , 14.000000000000002 %
the-boy-and-the-heron : 5.0 , 3.93 , 15.0 %
look-back-2024 : 3.5 , 4.26 , 15.0 %
=======================================
Average extremeness: 0.5553607057348022
Average extremeness percentile: 0.6451347106153533
=======================================
```