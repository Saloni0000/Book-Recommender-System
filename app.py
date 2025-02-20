import streamlit as st
import pickle
import numpy as np
import pandas as pd
import os

# ------------------------------
# 🔹 Function to Merge Pickle Files
# ------------------------------
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

# ------------------------------
# 🔹 Load Data
# ------------------------------
@st.cache_resource
def load_data():
    books = pd.read_pickle(books_file)
    popular_df = pd.read_pickle("popular.pkl")
    pt = pd.read_pickle("pt.pkl")
    similarity_scores = pd.read_pickle("similarity_scores.pkl")
    return books, popular_df, pt, similarity_scores

books, popular_df, pt, similarity_scores = load_data()

# Debugging: Show columns of popular_df
#st.write("📌 Available columns in `popular_df`:", list(popular_df.columns))

# ------------------------------
# 🔹 Streamlit UI
# ------------------------------
st.title("📚 Book Recommendation System")

# 🔸 **Popular Books Section**
st.subheader("🔥 Most Popular Books")

# ✅ Check if required columns exist before displaying
required_columns = ['Book-Title', 'Book-Author', 'avg_rating', 'num_ratings']
if 'Image-URL-M' in popular_df.columns:
    required_columns.append('Image-URL-M')

if all(col in popular_df.columns for col in required_columns):
    for i in range(len(popular_df)):
        col1, col2 = st.columns([1, 3])
        with col1:
            if 'Image-URL-M' in popular_df.columns:
                st.image(popular_df['Image-URL-M'].iloc[i], width=100)
        with col2:
            st.write(f"**{popular_df['Book-Title'].iloc[i]}** by {popular_df['Book-Author'].iloc[i]}")
            st.write(f"⭐ {round(popular_df['avg_rating'].iloc[i], 1)} ({popular_df['num_ratings'].iloc[i]} votes)")
            st.markdown("---")
else:
    st.error("⚠️ Required columns are missing from `popular_df`. Please check the dataset.")

# 🔸 **Book Recommendation Input**
st.subheader("📖 Get Book Recommendations")
user_input = st.text_input("Enter a book title:")

if st.button("Recommend"):
    if user_input:
        try:
            index = np.where(pt.index == user_input)[0][0]
            similar_items = sorted(
                list(enumerate(similarity_scores[index])),
                key=lambda x: x[1],
                reverse=True
            )[1:5]  # Get top 4 similar books

            st.subheader("🔹 Recommended Books")
            for i in similar_items:
                temp_df = books[books['Book-Title'] == pt.index[i[0]]]

                # ✅ Check if required columns exist
                if 'Image-URL-M' in temp_df.columns:
                    st.image(temp_df['Image-URL-M'].values[0], width=100)
                st.write(f"**{temp_df['Book-Title'].values[0]}** by {temp_df['Book-Author'].values[0]}")
                st.markdown("---")

        except IndexError:
            st.error("⚠️ Book not found. Try another title.")
