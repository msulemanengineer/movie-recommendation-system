# 🎬 Movie Recommendation System

A **content-based movie recommendation system** built using **Machine Learning and Natural Language Processing (NLP)**. The system recommends movies similar to a user's selected movie by analyzing movie metadata and calculating similarity between movies.

The project includes a **FastAPI backend** for serving recommendations and a **Streamlit frontend** for interacting with the recommendation system.

## 🚀 Features

* 🎥 Content-based movie recommendations
* 🔎 Search and select movies
* 🧠 NLP-based text preprocessing
* 📊 Text vectorization using **TF-IDF**
* 📐 Movie similarity using **Cosine Similarity**
* ⚡ FastAPI REST API
* 🖥️ Interactive Streamlit UI
* 💾 Precomputed recommendation data using Pickle
* 🧹 Data cleaning and preprocessing pipeline
* 🐍 Built entirely with Python

## 🧠 How It Works

The recommendation system follows a content-based filtering approach.

### 1. Data Collection

Movie information is collected and prepared for processing. Relevant movie attributes such as:

* Movie title
* Genres
* Keywords
* Cast
* Crew
* Overview

are combined to create a textual representation of each movie.

### 2. Data Preprocessing

The movie metadata is cleaned and transformed into a format suitable for NLP processing.

The preprocessing includes:

* Handling missing values
* Combining relevant features
* Converting text to lowercase
* Removing unnecessary information
* Preparing movie tags/features

### 3. Text Vectorization

The processed movie information is converted into numerical vectors using **TF-IDF (Term Frequency-Inverse Document Frequency)**.

This allows the system to represent each movie based on the words and features associated with it.

### 4. Cosine Similarity

The similarity between movies is calculated using **cosine similarity**.

Movies with similar feature vectors receive higher similarity scores.

Conceptually:

```text
Movie → Text Features → TF-IDF Vectorization
                         ↓
                  Similarity Matrix
                         ↓
                  Similar Movies
```

### 5. Recommendation

When a user selects a movie:

1. The system identifies the selected movie.
2. It retrieves its corresponding feature vector.
3. Similarity scores are calculated against other movies.
4. Movies are sorted according to similarity.
5. The most similar movies are returned as recommendations.

## 🏗️ Project Architecture

```text
                    ┌─────────────────────┐
                    │    Streamlit UI     │
                    │     Frontend        │
                    └──────────┬──────────┘
                               │
                               │ HTTP Request
                               ▼
                    ┌─────────────────────┐
                    │     FastAPI         │
                    │      Backend        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Recommendation      │
                    │      Engine         │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │ TF-IDF + Cosine     │
                    │    Similarity       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Precomputed Movie   │
                    │       Data          │
                    └─────────────────────┘
```

## 🛠️ Technologies Used

| Technology   | Purpose                               |
| ------------ | ------------------------------------- |
| Python       | Core programming language             |
| Pandas       | Data manipulation and preprocessing   |
| NumPy        | Numerical operations                  |
| Scikit-learn | TF-IDF and cosine similarity          |
| FastAPI      | Backend REST API                      |
| Uvicorn      | ASGI server                           |
| Streamlit    | Frontend/UI                           |
| Pickle       | Storing processed recommendation data |


## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/msulemanengineer/movie-recommendation-system.git

cd movie-recommendation-system
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

On macOS/Linux:

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## ▶️ Running the Project

The project consists of two parts:

* FastAPI backend
* Streamlit frontend

### Start FastAPI

```bash
uvicorn main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

FastAPI documentation can be accessed at:

```text
http://127.0.0.1:8000/docs
```

### Start Streamlit

Open another terminal and run:

```bash
streamlit run app.py
```

The Streamlit application will then open in your browser.

## 🔌 API

The FastAPI backend exposes endpoints for interacting with the recommendation engine.

Example request:

```text
GET /recommend/{movie_name}
```

Example:

```text
GET /recommend/Inception
```

Example response:

```json
{
  "movie": "Inception",
  "recommendations": [
    "Interstellar",
    "The Prestige",
    "The Dark Knight",
    "Shutter Island",
    "Memento"
  ]
}
```

> Update the endpoint and response example according to your actual FastAPI implementation.

## 📊 Recommendation Approach

This project uses **content-based filtering** rather than collaborative filtering.

Instead of relying on ratings from other users, the system recommends movies based on their content and metadata.

For example:

```text
Inception
   ↓
Genres + Keywords + Cast + Overview
   ↓
Text Processing
   ↓
TF-IDF Vector
   ↓
Cosine Similarity
   ↓
Most Similar Movies
```

This approach is useful when recommendations need to be generated based on the characteristics of the item itself.

## 📚 What I Learned

Through this project, I gained practical experience with:

* Data cleaning and preprocessing
* Natural Language Processing
* Feature engineering
* TF-IDF vectorization
* Cosine similarity
* Content-based recommendation systems
* Building REST APIs with FastAPI
* Connecting a frontend with a backend API
* Working with serialized ML data
* Building interactive ML applications with Streamlit
* Structuring an end-to-end machine learning project

## 🎯 Future Improvements

Some potential improvements include:

* [ ] Add movie posters and images
* [ ] Improve search functionality
* [ ] Add movie details and descriptions
* [ ] Add genre-based filtering
* [ ] Add user ratings
* [ ] Implement collaborative filtering
* [ ] Combine content-based and collaborative filtering
* [ ] Add user authentication
* [ ] Deploy the FastAPI backend
* [ ] Deploy the Streamlit frontend
* [ ] Improve recommendation ranking
* [ ] Add recommendation evaluation metrics


## 👨‍💻 Author

**Muhammad Suleman**

Full-Stack Developer | Machine Learning Enthusiast

* GitHub: [@msulemanengineer](https://github.com/msulemanengineer)
<!-- * Portfolio: [sulemans.netlify.app](https://sulemans.netlify.app/) -->

## ⭐ Support

If you found this project useful or interesting, consider giving the repository a ⭐ on GitHub.

---

**Built with Python, NLP, FastAPI and Streamlit.**
