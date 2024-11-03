import numpy as np
import mmh3
from collections import defaultdict
from src.structures import User, Movie
from tqdm import tqdm

def compute_minhashes(
                object: Movie | User, #movie or user to compute minhashes for
                n_hash = 100 #number of hashes
                ):

    bag = object.bag_ratings() #bag of ratings
    hashes = np.array([[mmh3.hash(id, seed) for id in bag] for seed in range(n_hash)]) #hashes for each seed
    minhashes = np.min(hashes, axis = 1) #minhashes for each seed
    return minhashes

def compute_signatures(
                objets: dict[str, Movie | User], #objects to compute signatures for
                n_hash = 100, #number of hashes
                with_tqdm = True #whether to show progress bar
                ):
    
    iterator = tqdm(objets.items()) if with_tqdm else objets.items() #iterator
    signatures = {id: compute_minhashes(obj, n_hash) for id, obj in iterator}
    return signatures

def bucket_hash(signatures, n_buckets = 100):
    bucket = 0
    for signature in signatures:
        bucket = bucket ^ signature #xor of all signatures
    return bucket % n_buckets #modulo n_buckets

def create_buckets(signatures: dict[str, np.ndarray], n_buckets = 100, bands = 10):
    r = len(signatures[list(signatures.keys())[0]]) // bands #number of rows in each band
    buckets = [defaultdict(list) for _ in range(bands)]
    for id, signature in signatures.items(): #for each object
        for band in range(bands): #for each band
            buckets[band][bucket_hash(signature[band*r:(band+1)*r], n_buckets)].append(id) #add to bucket
    return buckets

cartesian_product_exclude_greater = lambda A,B : set((a,b) for a in A for b in B if (b > a))

def get_candidates(buckets):
    #create a dictionary of the users' signatures
    candidates = set()
    for bucket in tqdm(buckets):
        for _, ids in tqdm(bucket.items()): 
            new_candidates = cartesian_product_exclude_greater(ids, ids)
            candidates.update(new_candidates)
    return candidates

def trim_candidates(users: dict[str, User | Movie], candidates: set, threshold = 0.5):
    n_removed = 0
    for id1,id2 in tqdm(candidates):
        sim = users[id1].similarity(users[id2], method = "jaccard")
        if sim < threshold:
            n_removed += 1
        else:
            users[id1].neighbors[id2] = sim
            users[id2].neighbors[id1] = sim
    return n_removed