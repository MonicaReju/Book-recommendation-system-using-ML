from flask import Flask, render_template, request, redirect, url_for
import model
import pandas as pd

app = Flask(__name__)

# Load books dataset
books = pd.read_csv("books.csv")


# --------------------------
# HOME → SHOW TOP 60 BOOKS
# --------------------------
@app.route('/')
def home():
    # ALWAYS new user → no history
    user_ratings_dict = {}
    rated_count = 0  

    # Show top 60 popular books
    top_books = books.sort_values(by='ratings_count', ascending=False).head(60)
    top_books = top_books[['book_id','title','authors','average_rating',
                           'ratings_count','image_url']].to_dict(orient='records')

    return render_template(
        'home.html',
        books=top_books,
        search_results=None,
        rated_count=rated_count,
        user_ratings=user_ratings_dict
    )


# --------------------------
# SEARCH BOOKS
# --------------------------
@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    search_results = model.search_books(query)

    user_ratings_dict = {}
    rated_count = 0

    # Also load top books again for fallback
    top_books = books.sort_values(by='ratings_count', ascending=False).head(60)
    top_books = top_books[['book_id','title','authors','average_rating',
                           'ratings_count','image_url']].to_dict(orient='records')

    return render_template(
        'home.html',
        books=top_books,
        search_results=search_results,
        rated_count=rated_count,
        user_ratings=user_ratings_dict
    )


# --------------------------
# RATE BOOK (TEMPORARY MEMORY)
# --------------------------
temporary_user_ratings = []   # ← NEW USER EVERY REFRESH


@app.route('/rate', methods=['POST'])
def rate():
    global temporary_user_ratings

    book_id = request.form['book_id']
    rating = float(request.form['rating'])

    # Remove old rating if exists
    temporary_user_ratings = [
        (b, r) for (b, r) in temporary_user_ratings if str(b) != str(book_id)
    ]

    # Add new rating
    temporary_user_ratings.append((book_id, rating))

    return redirect(url_for('home'))


# --------------------------
# RECOMMEND BOOKS USING MODEL
# --------------------------
@app.route('/recommend', methods=['POST'])
def recommend():
    global temporary_user_ratings

    if len(temporary_user_ratings) == 0:
        return render_template(
            'recommend.html',
            books=[],
            message="Please rate at least 1 book to get recommendations!"
        )

    if len(temporary_user_ratings) < 3:
        return render_template(
            'recommend.html',
            books=[],
            message=f"You rated {len(temporary_user_ratings)} book(s). Rate at least 3 books for better recommendations!"
        )

    # Call your existing model.py logic
    recommendations = model.get_recommendations_for_user(
        temporary_user_ratings,
        top_n=60
    )

    if not recommendations:
        return render_template(
            'recommend.html',
            books=[],
            message="We couldn't generate recommendations. Try rating different books!"
        )

    return render_template(
        'recommend.html',
        books=recommendations,
        message=None,
        rated_count=len(temporary_user_ratings)
    )


if __name__ == "__main__":
    app.run(debug=True)
