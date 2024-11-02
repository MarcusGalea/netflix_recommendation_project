import datetime as dt
from collections import defaultdict
import numpy as np

class User:
    def __init__(self, id):
        """
        Initialize a user with an id, a dictionary of ratings, a dictionary of dates, and a count of the 
        number of movies watched
        
        Attributes:
        ----------
            id: str
                user id
            ratings: dict
                dictionary of movie_id: rating given by user
            dates: dict
                dictionary of movie_id: date rating was given
            movies: dict
                dictionary of movie_id: movie object
            n_watched: int
                number of movies watched by user
            normalized: bool
                flag to indicate if ratings have been normalized
                
        Methods:
        --------
            __hash__()
                Return a hash value for the user object
            add_rating(movie, rating, date)
                Add a rating to the user's ratings and add the user to the movie's watched_by list
            normalize_ratings()
                Normalize the user's ratings by subtracting 
                the average rating and dividing by the standard deviation
            get_ratings()
                Return a list of ratings given by the user
        """
        
        self.id = id #user id
        self.ratings = defaultdict(float) #movie_id: rating given by user
        self.dates = defaultdict(dt.datetime) #movie_id: date rating was given
        self.movies = defaultdict(Movie) #movie_id: movie object
        self.n_watched = 0 #number of movies watched by user
        self.normalized = False #flag to indicate if ratings have been normalized
    
    
    
    def __hash__(self):
        """
        Return a hash value for the user object
        """
        #TODO: implement hash function
        pass
    
    def similarity(self, other, method='pearson'):
        """
        Compute the similarity between this user and another user
        
        Parameters:
        -----------
            other: User
                another user object
        
        Returns:
        --------
            float
                similarity between the two users
        """
        #get intersection of movies watched by both users
        watched_movies = set(self.movies.keys()).intersection(other.movies.keys())
        if len(watched_movies) == 0:
            return 0
        elif method == 'pearson':
            assert self.normalized and other.normalized, "Ratings should be normalized"
            ratings1 = np.array([self.ratings[movie_id] for movie_id in watched_movies])
            ratings2 = np.array([other.ratings[movie_id] for movie_id in watched_movies])
            denom = np.linalg.norm(ratings1)*np.linalg.norm(ratings2)
            denom = denom if denom != 0 else 1.0
            return np.dot(ratings1, ratings2)/denom
        elif method == 'jacard':
            #TODO implement jacard similarity
            pass
        elif method == 'cosine':
            #TODO implement cosine similarity
            pass
        else:
            #return error
            raise ValueError(f"Method {method} not implemented")
    
    
    def add_rating(self, movie, rating: int, date: str):
        """
        Add a rating to the user's ratings and add the user to the movie's watched_by list
        """
        self.ratings[movie.id] = rating #add rating to user's ratings
        self.dates[movie.id] = date #add date to user's 
        self.movies[movie.id] = movie #add movie to user's watched list
        
        movie.add_user(self) #add user to movie's user dictionary
        self.n_watched += 1
    
    def normalize_ratings(self):
        """
        Normalize the user's ratings by subtracting the average rating and dividing by the standard deviation
        """
        avg_rating = self.average_rating()
        sd_rating = self.sd_rating()
        for movie_id in self.ratings:
            self.ratings[movie_id] -= avg_rating
            self.ratings[movie_id] /= sd_rating
        self.normalized = True
    

    def get_ratings(self):
        """
        Return a dict of movie_id: rating given by the user
        """
        return self.ratings

    def average_rating(self):
        """
        return the average rating given by the user
        """
        return sum(self.ratings.values())/len(self.ratings)

    def sd_rating(self):
        """
        return the standard deviation of the user's ratings
        """
        avg_rating = self.average_rating()
        sd = np.sqrt(sum([(rating - avg_rating)**2 for rating in self.ratings.values()])/len(self.ratings))
        return sd if sd != 0 else 1
    
    def __str__(self):
        return f"User({self.id})"
    
    def __repr__(self):
        return f"User({self.id}) has rated {self.n_watched} movies"
    
    def __getitem__(self, movie_id: str):
        return self.ratings[movie_id]
    

class Movie:
    """
    Movie class to represent a movie object
    
    Attributes:
    -----------
        id: str
            movie id
        title: str
            movie title
        year: int
            movie release year
        users: dict
            dictionary of user_id: user object
        n_watched: int
            number of users who have watched the movie
    Methods:
    --------
        __hash__()
            Return a hash value for the movie object
        add_user(user)
            add a user who has watched the movie
        get_ratings()
            Return a list of ratings given to the movie by users
    """
    def __init__(self, id, title, year):
        self.id = id #movie id
        self.title = title #movie title 
        self.year = year #movie release year
        self.users = defaultdict(User) #list of users who have watched the movie
        self.genres = [] #list of genres
        self.n_watched = 0
        

    def __hash__(self):
        """
        Return a hash value for the movie object
        """
        #TODO: implement hash function
        pass
    
    def add_user(self, user: User):
        """
        add a user who has watched the movie
        """
        self.users[user.id] = user
        self.n_watched += 1
        
    def similarity(self, other, method='pearson'):
        """
        Compute the similarity between this movie and another movie
        
        Parameters:
        -----------
            other: Movie
                another movie object
        
        Returns:
        --------
            float
                similarity between the two movies
        """
        #get intersection of users who have watched both movies
        watched_users = set(self.users.keys()).intersection(other.users.keys())
        if len(watched_users) == 0:
            return 0
        elif method == 'pearson':
            ratings1 = np.array([self.users[user_id].ratings[self.id] for user_id in watched_users])
            ratings2 = np.array([other.users[user_id].ratings[other.id] for user_id in watched_users])
            denom = np.linalg.norm(ratings1)*np.linalg.norm(ratings2)
            denom = denom if denom != 0 else 1.0
            return np.dot(ratings1, ratings2)/denom
        elif method == 'jacard':
            #TODO implement jacard similarity
            pass
        elif method == 'cosine':
            #TODO implement cosine similarity
            pass
        else:
            #return error
            raise ValueError(f"Method {method} not implemented. You should normalize the ratings first")

    def get_ratings(self):
        """
        Return a dictionary of user_id: rating for the movie
        """
        return {user_id: user.ratings[self.id] for user_id, user in self.users.items()}
    
    def __str__(self):
        return f"{self.title}, {self.year}"
    
    def __repr__(self):
        return f"Movie({self.id}, {self.title}, {self.year}) seen by {self.n_watched} users"
    
    def __getitem__(self, user_id: str):
        return self.users[user_id]
    