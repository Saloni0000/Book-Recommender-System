from flask import Flask, render_template, request
import pickle
import numpy as np
import pandas as pd
import os

def merge_files():
    """Merge the split pickle files into one."""
    parts = ["books_part1.pkl", "books_part2.pkl", "books_part3.pkl"]
    
    # Ensure all parts exist
    for part in parts:
        if not os.path.exists(part):
            raise FileNotFoundError(f"Missing file: {part}")

    # Read and merge the parts
    merged_data = b""
    for part in parts:
        with open(part, "rb") as f:
            merged_data += f.read()
    
    # Save the merged file
    with open("books.pkl", "wb") as f:
        f.write(merged_data)

    return "books.pkl"

# Merge files before loading
books_file = merge_files()

# Load the merged pickle file
with open(books_file, "rb") as f:
    books = pd.read_pickle(f)

# Load other required pickle files
popular_df = pd.read_pickle(open('popular.pkl', 'rb'))
pt = pd.read_pickle(open('pt.pkl', 'rb'))
similarity_scores = pd.read_pickle(open('similarity_scores.pkl', 'rb'))

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html',
                           book_name=list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values)
                           )

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books', methods=['POST'])
def recommend():
    user_input = request.form.get('user_input')
    
    try:
        index = np.where(pt.index == user_input)[0][0]
        similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]
    except IndexError:
        return render_template('recommend.html', data=[], error="Book not found. Please try another title.")
    
    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
        data.append(item)
    
    return render_template('recommend.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
