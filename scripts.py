import scraper
import stats

def get_average_extremeness_for_user(browser, user, save_user=False, cap=None):
    reviews = scraper.get_user_reviews(user)
    print("Computing average extremeness of user's opinions...")

    cumulative = 0
    with open('data/movie-db.csv', 'r') as db_file:
        lines = db_file.readlines()
        db = {}
        for l in lines:
            l = l.split(',')
            movie = l[0]
            ratings = ','.join(l[1:])
            ratings = ratings.strip()[1:-1].split(',')
            ratings = [int(r) for r in ratings]
            db[movie] = ratings

    values = []

    if cap == None or len(reviews) < cap:
        step = 1
        total = len(reviews)
    else:
        step = max(math.floor(len(reviews) / cap), 1)
        total = cap
    
    movies_to_review = reviews[::step]
    movies_to_review = movies_to_review[:total]

    for movie in movies_to_review:
        if movie[0] not in db:
            mu, sigma, ratings =  scraper.get_movie_stats(browser, movie[0])
            db[movie[0]] = ratings
            

        ex = stats.extremeness(movie[1], db[movie[0]])
        mu, _ = stats.compute_stats(db[movie[0]])
        cumulative += ex
        values.append((ex, movie[0], movie[1], mu))

        if save_user:
            with open(f"data/users/{user}_extremeness.csv", 'a') as f:
                f.write(movie[0] + "," + str(ex) + "\n")

    average = cumulative / len(movies_to_review)

    if save_user:
        with open(f"data/users/{user}_extremeness.csv", 'a') as f:
            f.write("Average," + str(average) + "\n")
    
        
        with open("data/average_extremes.csv", 'a') as f:
            f.write(user + "," + str(average) + "\n")

    return average, values


def print_controversial(values):
    print("Most controversial:")
    print("[Movie], [User rating], [Average], [Extremeness]")
    most_controversial = sorted(values)
    for opinion in most_controversial[:10]:
        print(opinion[1][6:-1], ":", opinion[2], ",", round(opinion[3], 2), ",", round(opinion[0], 2) * 100, "%")
    print("=======================================")    


def print_is_contrarian(ratings, alpha):
    p_val, x2, crit_val = stats.is_contrarian(ratings, alpha)
    print("p-value is", p_val)
    if x2 > crit_val:
        print("Significant at ", alpha, " level. Rejecting null. Controversial opinions detected!")
    else:
        print("Insufficient evidence to reject null.")
    print("=======================================")

def print_extremeness(ex):
    print("Average extremeness:", ex)
    print("Average extremeness percentile:", stats.extremeness_percentile(ex))
    print("=======================================")

def user_analysis(user, alpha=0.05, movie_cap=None):
    browser = scraper.create_browser()
    average, values = get_average_extremeness_for_user(browser, user, cap=movie_cap)
    print_is_contrarian(values, alpha)
    print_controversial(values)
    print_extremeness(average)

    browser.quit()
    
