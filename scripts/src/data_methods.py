#read data from datapath
import numpy as np
import os
from collections import defaultdict
from src.structures import User, Movie
from tqdm import tqdm
import pandas as pd


def read_movies(datapath):
        """
        Read data from the netflix dataset
        Args:
            datapath: path to the folder containing the dataset
        Returns:
            movies: dictionary of movies
        """
        movies = defaultdict(Movie)
        with open(os.path.join(datapath, 'movie_titles.csv'), 'r', encoding='latin1') as f:
            for line in f:
                movieid, year= line.strip().split(',')[:2]
                title = ','.join(line.strip().split(',')[2:])
                movies[movieid] = Movie(movieid, title, year)
        return movies

def read_viewers(
            datapath, 
            movies, 
            datafiles = ['combined_data_1.txt'], 
            with_tqdm = False, 
            n_lines = np.inf,
            reviews_pr_movie = np.inf
            ):
    """
    Read data from the netflix dataset
    Args:
        datapath: path to the folder containing the dataset
        movies: dictionary of movies
        datafiles: list of datafiles to read
    Returns:
        users: dictionary of users
    """
    users = defaultdict(User)
    for datafile in datafiles:
        with open(os.path.join(datapath, datafile), 'r') as f:
            lines = f.readlines()
            n = min(n_lines, len(lines))
            iterator = tqdm(range(n)) if with_tqdm else range(n)
            for i in iterator:
                line = lines[i].strip()
                if i > n:
                    break
                #check if theres a comma in the line
                if not ',' in line:
                    movieid = line.split(':')[0]
                else:
                    j = 0
                    if j < reviews_pr_movie:
                        userid, rating, date= line.split(',')
                        #check if user already exists
                        if userid not in users:
                            users[userid] = User(userid)
                        #add rating to user
                        users[userid].add_rating(movies[movieid], int(rating), date)
                        j += 1
    #remove movies with no ratings
    excluded_movies = [movieid for movieid, movie in movies.items() if movie.n_watched == 0]
    for movieid in excluded_movies:
        del movies[movieid]
    return users

#### Dataframe methods ####
def dict_to_df(users):
    data = []
    for user in users.values():
        for movie_id, rating in user.ratings.items():
            data.append({'user_id': user.id, 'movie_id': movie_id, 'rating': rating})
    return pd.DataFrame(data)

def read_df(datapath, datafiles = ['combined_data_1.txt'], n_lines = np.inf):
    data = []
    for datafile in datafiles:
        with open(os.path.join(datapath, datafile), 'r') as f:
            lines = f.readlines()
            n = min(n_lines, len(lines))
            for i in range(n):
                line = lines[i].strip()
                if i > n:
                    break
                #check if theres a comma in the line
                if not ',' in line:
                    movieid = line.split(':')[0]
                else:
                    userid, rating, date= line.split(',')
                    data.append({'user_id': userid, 'movie_id': movieid, 'rating': rating, 'date': date})
    return pd.DataFrame(data)