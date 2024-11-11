import numpy as np
from gensim.models import KeyedVectors

print("Loading Word2Vec model")
model = KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary=True)
print("Loaded Word2Vec model")

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def get_word_vector_safe(word):
    if word in model:
        return model[word]
    else:
        raise ValueError(f"Word '{word}' not in vocabulary")

def get_best_match_idx(query, col_names):
    vectors = [get_word_vector_safe(c) for c in col_names]
    q = get_word_vector_safe(query)
    similarities = [cosine_similarity(v, q) for v in vectors]
    
    idx = np.argmax(similarities)
    return (idx, col_names[idx], similarities[idx])
