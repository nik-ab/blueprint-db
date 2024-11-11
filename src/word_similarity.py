import fasttext.util
import numpy as np

fasttext.util.download_model('en', if_exists='ignore')
ft = fasttext.load_model('cc.en.300.bin')
print("Loaded FastText model")


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def get_word_vector_safe(word):
    res = ft.get_word_vector(word)
    if np.linalg.norm(res) == 0:
        raise ValueError(f"Word '{word}' not in vocabulary")
    return res

def get_best_match_idx(query, col_names):
    vectors = [get_word_vector_safe(c) for c in col_names]
    q = get_word_vector_safe(query)
    similarities = [cosine_similarity(v, q) for v in vectors]
    
    idx = np.argmax(similarities)
    return (idx, col_names[idx], similarities[idx])


if __name__ == "__main__":
    cols = ["name", "idx", "age", "city", "country"]
    _, match, _ = get_best_match_idx("time", cols)
    print(match)