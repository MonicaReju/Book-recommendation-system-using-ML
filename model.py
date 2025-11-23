import pandas as pd
import pickle

# Load dataset
books = pd.read_csv("books.csv")

# Load pre-computed components from pickle
try:
    with open('content_based_components.pkl', 'rb') as f:
        components = pickle.load(f)
    
    cosine_sim = components['cosine_sim']
    indices = components['indices']  # book_id → matrix index
    print("✓ Loaded cosine_sim and indices from pickle successfully!")
    print(f"  Indices type: {type(indices)}")
    print(f"  Number of books in model: {len(indices)}")
except Exception as e:
    print(f"Error loading pickle: {e}")
    cosine_sim = None
    indices = None


def get_recommendations_for_user(user_ratings, top_n=20):
    """Get recommendations based on user’s rated books."""
    if cosine_sim is None or indices is None:
        print("Error: cosine_sim or indices not loaded")
        return []
    
    if not user_ratings:
        return []
    
    print(f"\n=== GENERATING RECOMMENDATIONS ===")
    print(f"User rated {len(user_ratings)} books")

    all_sim_scores = []
    found_books = []
    missing_books = []
    
    for book_id, rating in user_ratings:
        book_id_int = int(book_id)
        book_id_str = str(book_id)

        print(f"\nChecking book_id: {book_id} (rating: {rating})")
        
        # Try both int and string mapping
        if book_id_int in indices:
            idx = indices[book_id_int]
            print(f"  ✓ Found as int at index: {idx}")
            found_books.append(book_id_int)

        elif book_id_str in indices:
            idx = indices[book_id_str]
            print(f"  ✓ Found as str at index: {idx}")
            found_books.append(book_id_str)

        else:
            print(f"  ✗ Not found in model")
            missing_books.append(book_id)
            continue
        
        sim_scores = list(enumerate(cosine_sim[idx]))
        weighted_scores = [(i, score * (rating / 5.0)) for i, score in sim_scores]
        all_sim_scores.extend(weighted_scores)
    
    print(f"\n=== SUMMARY ===")
    print(f"Found {len(found_books)} books")
    print(f"Missing {len(missing_books)} books")

    if not all_sim_scores:
        return []
    
    from collections import defaultdict
    totals = defaultdict(float)
    counts = defaultdict(int)

    for idx, score in all_sim_scores:
        totals[idx] += score
        counts[idx] += 1

    avg_scores = [(idx, totals[idx] / counts[idx]) for idx in totals]
    avg_scores.sort(key=lambda x: x[1], reverse=True)

    rated_ids = {int(bid) for bid, _ in user_ratings}
    rated_ids.update({str(bid) for bid, _ in user_ratings})

    reverse_indices = {v: k for k, v in indices.items()}

    recommendations = []
    for matrix_idx, score in avg_scores:
        book_id = reverse_indices.get(matrix_idx)

        if not book_id or book_id in rated_ids:
            continue

        book_id_int = int(book_id)
        book = books[books['book_id'] == book_id_int]

        if not book.empty:
            recommendations.append(book.iloc[0])

        if len(recommendations) >= top_n:
            break

    print(f"\nGenerated {len(recommendations)} recommendations")

    result = []
    for book in recommendations:
        result.append({
            'book_id': int(book['book_id']),
            'title': book['title'],
            'authors': book['authors'],
            'average_rating': float(book['average_rating']),
            'ratings_count': int(book['ratings_count']),
            'image_url': book['image_url']
        })
    
    return result


def search_books(query, top_n=20):
    """Search books by title."""
    query_lower = query.lower()
    mask = books['title'].str.lower().str.contains(query_lower, na=False)
    results = books[mask].head(top_n)

    return results[['book_id', 'title', 'authors',
                    'average_rating', 'ratings_count',
                    'image_url']].to_dict(orient='records')
