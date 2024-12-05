import fasttext.util
import numpy as np


fasttext.util.download_model('en', if_exists='ignore')

print("Loading FastText model")
ft = fasttext.load_model('cc.en.300.bin')
print("Loaded FastText model")


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def get_word_vector_safe(word):
    res = ft.get_word_vector(word)
    if np.linalg.norm(res) == 0:
        raise ValueError(f"Word '{word}' not in vocabulary")
    return res

def get_best_match_idx(query, col_names, forbidden_idxs=[]):
    vectors = [get_word_vector_safe(c) for c in col_names]
    q = get_word_vector_safe(query)
    similarities = [cosine_similarity(v, q) + (0 if idx not in forbidden_idxs else -10) for idx, v in enumerate(vectors)]
    
    idx = np.argmax(similarities)
    return (idx, col_names[idx], similarities[idx])


if __name__ == "__main__":
    cols = ["danceability","energy","key","loudness","mode","speechiness","acousticness","instrumentalness","liveness","valence","tempo","duration_ms","time_signature","liked"]
    
    _, match, _ = get_best_match_idx("time", cols)
    print(match)

    _, match, _ = get_best_match_idx("acoustics", cols)
    print(match)