from math import comb
import numpy as np
from collections import defaultdict
from src.structures import User, Movie
from tqdm import tqdm


def prediction(user: User, movie: Movie):
    #get the neighbors
    weighted_sum = 0
    total_weight = 0
    for neighbor_id, similarity in user.neighbors.items():
        neighbor = users[neighbor_id]
        if movie.id in neighbor.ratings:
            weighted_sum += similarity * (neighbor.ratings[movie.id]-neighbor.average_rating())
            total_weight += similarity
    if total_weight == 0:
        return -1
    return weighted_sum/ total_weight + user.average_rating()


def prediction_error(user: User, movies, method = 'MAE'):
    error = 0.0
    n = 0
    for movie_id,rating in user.ratings.items():
        movie = movies[movie_id]
        pred = prediction(user, movie)
        if pred == -1:
            continue
        if method == 'MAE':
            error += abs(rating - pred)
        elif method == 'RMSE':
            error += (rating - pred)**2
        n += 1
    if n == 0:
        return -1
    if method == 'MAE':
        return error/n
    elif method == 'RMSE':
        return np.sqrt(error/n)

def prediction_error_all(users: dict[str, User], method = 'MAE'):
    RMSE_dict = defaultdict(float)
    for user in tqdm(users.values()):
        RMSE_dict[user.id] = prediction_error(user, method = method)
    return RMSE_dict


def get_true_pairs(movies: dict, #dict of Movie objects indexed by movie_id
                   sim_matrix, #similarity matrix between movies
                   t, #threshold for similarity
                   ):
    """
    Get true pairs of movies with similarity above threshold t
    Args:
        movies (dict): dictionary of Movie objects indexed by movie_id
        sim_matrix (np.array): similarity matrix between movies
        t (float): threshold for similarity
    Returns:
        list of tuples: list of true pairs of movies
    """
    pairs = sim_matrix > t
    idx_map = {i: movie_id for i, movie_id in enumerate(movies)}
    #get indices of pairs
    movie_id1, movie_id2 = np.where(pairs)
    pairs = list(zip(movie_id1, movie_id2))
    true_pairs = [(idx_map[i], idx_map[j]) for i, j in pairs if i != j and i < j]
    return true_pairs

#create confusion matrix for candidates and true pairs
def confusion_matrix(candidate_pairs, true_pairs, n_movies):
    """Compute confusion matrix for candidate pairs and true pairs

    Args:
        candidate_pairs (list): list of candidate pairs (tuple of ids)
        true_pairs (list): list of true pairs (tuple of ids)
        n_movies (int): number of movies

    Returns:
        np.array: confusion matrix
    """
    
    n_pairs = comb(n_movies, 2) # number of possible pairs
    n_candidates = len(candidate_pairs) # number of candidate pairs
    
    #initialize confusion matrix
    confusion_matrix = np.zeros((2, 2), dtype = int)
    for i, j in candidate_pairs:
        if (i, j) in true_pairs: #true positive
            confusion_matrix[0, 0] += 1
        else: #false positive
            confusion_matrix[0, 1] += 1
    for i, j in true_pairs: 
        if (i, j) not in candidate_pairs: #false negative
            confusion_matrix[1, 0] += 1
    confusion_matrix[1, 1] = n_pairs - n_candidates - confusion_matrix[1, 0] #true negative
    return confusion_matrix

def sensitivity_specificity(CM):
    """
    Compute sensitivity and specificity from confusion matrix
    
    Args:
    CM: np.array, confusion matrix
    
    Returns:
    sensitivity: float, sensitivity
    specificity: float, specificity
    """
    TP, FP, FN, TN = CM.flatten()
    sensitivity = TP/(TP + FN)
    specificity = TN/(TN + FP)
    return sensitivity, specificity