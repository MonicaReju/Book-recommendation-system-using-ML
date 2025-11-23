import pickle
import pandas as pd

print("=== LOADING FILES ===")

with open('content_based_components.pkl', 'rb') as f:
    components = pickle.load(f)

print("✓ Pickle loaded")
print(f"Keys: {components.keys()}\n")

books = pd.read_csv("books.csv")
print("✓ CSV loaded")
print(f"Columns: {list(books.columns)}")
print(f"Total books: {len(books)}\n")

indices = components['indices']
print(f"Type of indices: {type(indices)}")
print(f"Number of indices: {len(indices)}\n")

print("=== SAMPLE CSV DATA ===")
print(books.head(3)[['id', 'book_id', 'title', 'authors']].to_string())
print()

print("=== FIRST 10 ITEMS IN INDICES ===")
if isinstance(indices, dict):
    for key, idx in list(indices.items())[:10]:
        print(f"Key: {key} -> Index: {idx}")
print()

print("=== CHECKING FIRST 5 BOOK TITLES ===")
for i in range(5):
    title = books.iloc[i]['title']
    in_pickle = (title in indices) if not books.empty else False
    mark = "✓" if in_pickle else "✗"
    print(f"{mark} '{title}'")
print()

print("=== TRYING MATCHES ===")
matches = 0
for i in range(20):
    title = books.iloc[i]['title']
    if title in indices:
        matches += 1

print(f"Matches {matches}/20\n")

print("=== CHECKING THE HUNGER GAMES ===")
hg = books[books['title'].str.contains('Hunger Games', case=False, na=False)]
for _, row in hg.iterrows():
    title = row['title']
    exists = title in indices
    mark = "✓" if exists else "✗"
    print(f"{mark} {row['book_id']} | {title}")
