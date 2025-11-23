import pickle
import pandas as pd

with open('content_based_components.pkl', 'rb') as f:
    components = pickle.load(f)

indices = components['indices']
books = pd.read_csv("books.csv")

print("=== CHECKING BOOKS IN MODEL ===")
print(f"Books in CSV: {len(books)}")
print(f"Books in model: {len(indices)}\n")

model_book_ids = [int(k) for k in indices.keys()]

print("First 20 model book_ids:")
print(sorted(model_book_ids)[:20])
print()

print("=== TOP 20 POPULAR BOOKS ===")
top_books = books.sort_values(by="ratings_count", ascending=False).head(20)

count = 0
for _, row in top_books.iterrows():
    bid_int = int(row['book_id'])
    status = "✓" if (bid_int in indices or str(bid_int) in indices) else "✗"
    if status == "✓":
        count += 1
    print(f"{status} {row['book_id']} | {row['ratings_count']} | {row['title']}")

print(f"\nPopular books found in model: {count}/20\n")

print("=== BOOKS FROM CSV THAT ARE IN MODEL ===")
books_in_model = books[books['book_id'].astype(str).isin(indices.keys())]
print(f"Found {len(books_in_model)} books\n")

if len(books_in_model) > 0:
    top = books_in_model.sort_values(by="ratings_count", ascending=False).head(20)
    for _, row in top.iterrows():
        print(f"✓ {row['book_id']} | {row['ratings_count']} | {row['title']}")
else:
    print("⚠ No CSV books match the model!")
