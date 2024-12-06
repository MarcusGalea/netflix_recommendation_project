import numpy as np
import mmh3
from collections import defaultdict
from src.structures import User, Movie
from tqdm import tqdm

def compute_minhashes(
                object: Movie | User, #movie or user to compute minhashes for
                n_hash = 100, #number of hashes
                ):
    """Computes minhashes for a movie or user object

    Args:
        object (Movie | User): movie or user object to compute minhashes for

    Returns:
        np.ndarray: minhashes for the object
    """
    
    
    bag = object.bag_ratings() #bag representation of ratings
    hashes = np.array([[mmh3.hash(id, seed) for id in bag] for seed in range(n_hash)]) #hashes for each seed
    minhashes = np.min(hashes, axis = 1) #minhashes for each seed
    return minhashes

def compute_signatures(
                objets: dict[str, Movie | User], #objects to compute signatures for
                n_hash = 100, #number of hashes
                with_tqdm = True #whether to show progress bar
                ):
    """Computes signatures for a dictionary of objects

    Args:
        objets (dict[str, Movie  |  User]): dictionary of objects to compute signatures for

    Returns:
        dict[str, np.ndarray]: dictionary of signatures
        """
    
    iterator = tqdm(objets.items()) if with_tqdm else objets.items() #iterator
    signatures = {id: compute_minhashes(obj, n_hash) for id, obj in iterator}
    return signatures

def bucket_hash(signatures: dict[str, np.ndarray], n_buckets = 100):
    """Hashes a list of signatures to a bucket

    Args:
        signatures (list): list of signatures
        n_buckets (int, optional): Defaults to 100.

    Returns:
        int: bucket id
    """
    bucket = 0
    for signature in signatures:
        bucket = bucket ^ signature #xor of all signatures
    return bucket % n_buckets #modulo n_buckets

def create_buckets(signatures: dict[str, np.ndarray], n_buckets = 100, bands = 10):
    """Creates buckets for a dictionary of signatures

    Args:
        signatures (dict[str, np.ndarray]): dictionary of signatures
        n_buckets (int, optional): _description_. Defaults to 100.
        bands (int, optional): _description_. Defaults to 10.

    Returns:
        list: list for each band containing a dictionary of buckets. Each bucket is a hash table with the bucket number as key and a list of object ids as value
    """
    r = len(signatures[list(signatures.keys())[0]]) // bands #number of rows in each band
    buckets = [defaultdict(list) for _ in range(bands)]
    for id, signature in signatures.items(): #for each object (movie or user)
        for band in range(bands): #for each band
            bucket_id = bucket_hash(signature[band*r:(band+1)*r], n_buckets) #hash the band to a bucket
            buckets[band][bucket_id].append(id) #add id to bucket
    return buckets

cartesian_product_exclude_greater = lambda A,B : set((a,b) for a in A for b in B if (b > a))

def get_candidates(buckets):
    """Get candidate pairs from a list of buckets

    Args:
        buckets (list): list for each band containing a dictionary of buckets. Each bucket is a hash table with the bucket number as key and a list of object ids as value

    Returns:
        set: set of candidate pairs
    """
    #create a dictionary of the users' signatures
    candidates = set()
    for bucket in tqdm(buckets):
        for _, ids in tqdm(bucket.items()): 
            new_candidates = cartesian_product_exclude_greater(ids, ids)
            candidates.update(new_candidates)
    return candidates

def trim_candidates(users: dict[str, User | Movie], candidates: set, threshold = 0.5):
    """Trim candidates based on a similarity threshold

    Args:
        users (dict[str, User  |  Movie]): dictionary of users
        candidates (set): set of candidate pairs
        threshold (float, optional): threshold Defaults to 0.5.

    Returns:
        int: number of removed candidates
    """
    n_removed = 0
    for id1,id2 in tqdm(candidates):
        sim = users[id1].similarity(users[id2], method = "jaccard")
        if sim < threshold:
            n_removed += 1
        else:
            users[id1].neighbors[id2] = sim
            users[id2].neighbors[id1] = sim
    return n_removed