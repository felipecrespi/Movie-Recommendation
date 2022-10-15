from graph.graph import Graph


def get_recommendation_value(paths: list[tuple[int, int]]) -> float:
    """Return the recommendation value between two movies given their paths.
    The recommendation value is defined as follows:

    (num of paths) * (average review score per path) * (average path length)
    """
    if paths == []:
        return 0.0

    avg_review_score = sum(path[1] for path in paths) / len(paths)
    avg_length = sum(path[0] for path in paths) / len(paths)

    return len(paths) * avg_review_score * avg_length


def one_movie_recommendation(movie: str, graph: Graph) -> list[tuple[float, str]]:
    """Return a sorted list of tuples with recommended movies and their individual
    recommendation value based solely on one movie."""
    movies = []
    for m in graph.get_all_vertices('movie'):
        if m != movie:
            rec_value = get_recommendation_value(graph.get_all_paths(movie, m))
            if rec_value > 0:
                movies.append((rec_value, m))
    movies.sort(reverse=True)
    return movies


def recommend_movies(movies: list[str], graph: Graph) -> list[str]:
    """Return a list of recommended movies based the movies given
    using their average recommendation value.

    Average recommendation value is the average of individual
    recommendation value the movie received.
    """
    recommended_movies = {}
    # this dictionary maps a movie to a list containing the recommendation
    # indexes for every time it was recommended. E.g {'The Matrix': [3.7, 5.6]}
    for movie in movies:
        for rec in one_movie_recommendation(movie, graph):
            if rec[1] in recommended_movies:
                recommended_movies[rec[1]].append(rec[0])
            else:
                recommended_movies[rec[1]] = [rec[0]]

    # get the average recommendation value for each movie and sort the list.
    recommendation = [(sum(recommended_movies[movie]) / len(recommended_movies[movie]),
                       movie) for movie in recommended_movies]
    recommendation.sort(reverse=True)

    return [movie[1] for movie in recommendation]  # don't return the rec value, only the name


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['graph', 'load_graph'],
        'max-line-length': 100,
        'disable': ['R1705', 'C0200']
    })

    import python_ta.contracts
    python_ta.contracts.check_all_contracts()

    import doctest

    doctest.testmod()
