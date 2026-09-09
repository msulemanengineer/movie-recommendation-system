import streamlit as st
import httpx
import html
import textwrap

# ============================================================
# HTML HELPER
# ============================================================
# IMPORTANT — two separate Markdown quirks were breaking this app's
# HTML rendering:
#
# 1) Streamlit's markdown parser treats any line indented with 4+
#    spaces as a Markdown *code block*. Because this file builds
#    HTML inside nested functions/if-blocks, the raw triple-quoted
#    strings had lots of leading whitespace -> fixed with dedent.
#
# 2) CommonMark's raw-HTML-block rule ends an HTML block as soon as
#    it hits a BLANK LINE. This file's HTML strings use blank lines
#    between tags purely for readability, which was closing the
#    HTML block early. Everything after that blank line then got
#    re-parsed as a *new* block — and since it was still indented,
#    it became an indented code block again, even after dedenting.
#
# render_html() fixes both: dedent, then drop blank lines, before
# handing the string to st.markdown. Every HTML-producing call in
# this file goes through render_html() instead of calling
# st.markdown directly.

def render_html(content):
    content = textwrap.dedent(content)
    # Drop blank/whitespace-only lines so Markdown doesn't treat
    # them as the end of the HTML block.
    content = "\n".join(
        line for line in content.split("\n")
        if line.strip() != ""
    )
    st.markdown(
        content,
        unsafe_allow_html=True
    )

# ============================================================
# CONFIG
# ============================================================

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="CineMatch",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "selected_movie": None,
    "selected_details": None,
    "search_results": [],
    "search_query": "",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# GLOBAL CSS
# ============================================================

render_html(
    """
    <style>

    /* ======================================================
       RESET / GLOBAL
    ====================================================== */

    .stApp {
        background: #f6f4ef;
        color: #171717;
    }

    .main .block-container {
        max-width: 1380px;
        padding-top: 1.5rem;
        padding-bottom: 5rem;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        background: transparent !important;
    }

    * {
        font-family: Inter, -apple-system, BlinkMacSystemFont,
                     "Segoe UI", sans-serif;
    }

    /* ======================================================
       NAVBAR
    ====================================================== */

    .nav {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.4rem 0 1.5rem;
        margin-bottom: 1rem;
    }

    .logo {
        font-size: 1.45rem;
        font-weight: 850;
        letter-spacing: -1.2px;
        color: #151515;
    }

    .logo-mark {
        display: inline-flex;
        width: 30px;
        height: 30px;
        align-items: center;
        justify-content: center;
        border-radius: 9px;
        background: #181818;
        color: white;
        margin-right: 8px;
        font-size: 0.9rem;
    }

    .nav-copy {
        color: #77736c;
        font-size: 0.78rem;
        letter-spacing: 0.2px;
    }

    /* ======================================================
       HERO
    ====================================================== */

    .hero {
        position: relative;
        overflow: hidden;
        min-height: 410px;
        border-radius: 30px;
        padding: 3.7rem;
        margin: 0.5rem 0 2.5rem;
        background:
            radial-gradient(
                circle at 80% 15%,
                rgba(236, 178, 119, 0.38),
                transparent 28%
            ),
            radial-gradient(
                circle at 100% 100%,
                rgba(145, 120, 190, 0.22),
                transparent 35%
            ),
            #ebe5da;
        border: 1px solid #ded8ce;
    }

    .hero::after {
        content: "";
        position: absolute;
        width: 330px;
        height: 330px;
        right: -100px;
        bottom: -150px;
        border-radius: 50%;
        background: rgba(255,255,255,0.4);
    }

    .hero-kicker {
        position: relative;
        z-index: 2;
        color: #75695d;
        text-transform: uppercase;
        font-size: 0.7rem;
        font-weight: 800;
        letter-spacing: 2.5px;
        margin-bottom: 1rem;
    }

    .hero-title {
        position: relative;
        z-index: 2;
        max-width: 700px;
        font-family: Georgia, "Times New Roman", serif;
        font-size: clamp(3rem, 6vw, 5.5rem);
        line-height: 0.92;
        letter-spacing: -4px;
        color: #171717;
        margin: 0;
    }

    .hero-title em {
        color: #8a5b42;
        font-weight: 400;
    }

    .hero-description {
        position: relative;
        z-index: 2;
        max-width: 560px;
        margin-top: 1.5rem;
        color: #68625b;
        line-height: 1.7;
        font-size: 0.98rem;
    }

    .hero-badge {
        position: absolute;
        z-index: 2;
        right: 5%;
        top: 18%;
        width: 130px;
        height: 130px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        background: #181818;
        color: #f7f3ec;
        font-size: 0.72rem;
        font-weight: 750;
        line-height: 1.35;
        transform: rotate(9deg);
        box-shadow: 0 18px 40px rgba(0,0,0,0.12);
    }

    /* ======================================================
       SEARCH
    ====================================================== */

    .search-label {
        font-size: 0.73rem;
        text-transform: uppercase;
        letter-spacing: 1.8px;
        font-weight: 800;
        color: #777169;
        margin-bottom: 0.5rem;
    }

    div[data-testid="stTextInput"] input {
        background: #fffdf9 !important;
        color: #171717 !important;
        border: 1px solid #d8d2c8 !important;
        border-radius: 15px !important;
        height: 52px !important;
        font-size: 0.95rem !important;
        padding-left: 1rem !important;
    }

    div[data-testid="stTextInput"] input:focus {
        border-color: #8a5b42 !important;
        box-shadow: 0 0 0 1px #8a5b42 !important;
    }

    div.stButton > button {
        border-radius: 13px;
        min-height: 45px;
        border: 1px solid #d5cec4;
        background: #fffdf9;
        color: #242424;
        font-weight: 650;
        transition: all 0.18s ease;
    }

    div.stButton > button:hover {
        border-color: #8a5b42;
        color: #8a5b42;
        background: #fffaf4;
    }

    /* ======================================================
       SECTION HEADINGS
    ====================================================== */

    .section {
        margin-top: 2.8rem;
        margin-bottom: 1.2rem;
    }

    .section-eyebrow {
        color: #9a6b4e;
        text-transform: uppercase;
        font-size: 0.68rem;
        letter-spacing: 2px;
        font-weight: 850;
        margin-bottom: 0.25rem;
    }

    .section-title {
        font-family: Georgia, "Times New Roman", serif;
        font-size: 2rem;
        letter-spacing: -1.2px;
        color: #181818;
        margin: 0;
    }

    .section-description {
        color: #858078;
        font-size: 0.82rem;
        margin-top: 0.3rem;
    }

    /* ======================================================
       CATEGORY PILLS
    ====================================================== */

    div[data-testid="stRadio"] > div {
        gap: 0.45rem;
    }

    div[data-testid="stRadio"] label {
        background: #ebe7df;
        border: 1px solid #ddd7ce;
        border-radius: 999px;
        padding: 0.45rem 0.9rem;
        color: #69645d;
        transition: 0.15s;
    }

    div[data-testid="stRadio"] label:hover {
        border-color: #bba895;
        color: #4b4038;
    }

    div[data-testid="stRadio"] label:has(input:checked) {
        background: #181818;
        border-color: #181818;
        color: white;
    }

    /* ======================================================
       MOVIE CARDS
    ====================================================== */

    .movie-card {
        background: transparent;
        margin-bottom: 0.4rem;
    }

    .poster-frame {
        position: relative;
        overflow: hidden;
        border-radius: 16px;
        background: #e8e3db;
        aspect-ratio: 2 / 3;
        box-shadow: 0 7px 20px rgba(39, 31, 23, 0.07);
    }

    .poster-frame img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
    }

    .poster-placeholder {
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #9a9389;
        font-size: 0.75rem;
    }

    .movie-title {
        margin-top: 0.65rem;
        font-size: 0.88rem;
        font-weight: 720;
        line-height: 1.25;
        color: #242424;
        min-height: 2.2rem;
    }

    .movie-meta {
        margin-top: 0.2rem;
        color: #89837a;
        font-size: 0.72rem;
    }

    .star {
        color: #9a6b4e;
        font-weight: 750;
    }

    /* ======================================================
       DETAILS HERO
    ====================================================== */

    .details-wrap {
        background: #ebe6dd;
        border: 1px solid #ddd6cb;
        border-radius: 28px;
        overflow: hidden;
        margin-bottom: 2rem;
    }

    .details-backdrop {
        position: relative;
        min-height: 390px;
        background: #d9d2c7;
        overflow: hidden;
    }

    .details-backdrop img {
        width: 100%;
        height: 390px;
        object-fit: cover;
        display: block;
        opacity: 0.72;
    }

    .backdrop-overlay {
        position: absolute;
        inset: 0;
        background:
            linear-gradient(
                to right,
                rgba(26,23,20,0.82),
                rgba(26,23,20,0.22),
                rgba(26,23,20,0.1)
            ),
            linear-gradient(
                to top,
                rgba(26,23,20,0.75),
                transparent 55%
            );
    }

    .details-content {
        position: absolute;
        left: 3rem;
        bottom: 2.5rem;
        max-width: 700px;
        color: white;
    }

    .details-title {
        font-family: Georgia, "Times New Roman", serif;
        font-size: 3.2rem;
        line-height: 0.98;
        letter-spacing: -2px;
        margin-bottom: 0.7rem;
    }

    .details-meta {
        font-size: 0.8rem;
        color: #e1ddd7;
        margin-bottom: 0.9rem;
    }

    .details-body {
        padding: 2rem 2.5rem 2.5rem;
    }

    .genre {
        display: inline-block;
        background: #ded7cd;
        color: #625a52;
        padding: 0.38rem 0.7rem;
        border-radius: 999px;
        font-size: 0.7rem;
        margin: 0 0.35rem 0.35rem 0;
    }

    .overview {
        max-width: 800px;
        color: #666159;
        line-height: 1.8;
        font-size: 0.92rem;
        margin-top: 1.2rem;
    }

    /* ======================================================
       RECOMMENDATION SCORE
       ====================================================== */

    .similarity {
        display: inline-block;
        margin-top: 0.2rem;
        padding: 0.22rem 0.45rem;
        border-radius: 6px;
        background: #e9dfd5;
        color: #865c45;
        font-size: 0.65rem;
        font-weight: 750;
    }

    /* ======================================================
       DIVIDER
       ====================================================== */

    .soft-divider {
        height: 1px;
        background: #ded8cf;
        margin: 2.5rem 0;
    }

    /* ======================================================
       EMPTY / ERROR
       ====================================================== */

    .empty {
        padding: 3rem;
        text-align: center;
        border: 1px dashed #d4cec5;
        border-radius: 18px;
        color: #888177;
        background: #faf8f4;
    }

    /* ======================================================
       RESPONSIVE
       ====================================================== */

    @media (max-width: 900px) {

        .hero {
            padding: 2.5rem 2rem;
        }

        .hero-badge {
            display: none;
        }

        .details-content {
            left: 1.5rem;
            right: 1.5rem;
        }

        .details-title {
            font-size: 2.3rem;
        }
    }

    </style>
    """
)


# ============================================================
# API
# ============================================================

def api_get(endpoint, params=None):

    try:

        response = httpx.get(
            f"{API_URL}{endpoint}",
            params=params,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    except Exception as e:

        st.error(f"Unable to connect to recommendation API: {e}")

        return None


def get_home(category):

    return api_get(
        "/home",
        {
            "category": category,
            "limit": 20,
        },
    ) or []


def search_movies(query):

    return api_get(
        "/tmdb/search",
        {
            "query": query,
            "page": 1,
        },
    ) or {}


def get_details(movie_id):

    return api_get(
        f"/movie/id/{movie_id}"
    )


def get_bundle(title):

    return api_get(
        "/movie/search",
        {
            "query": title,
            "tfidf_top_n": 10,
            "genre_limit": 10,
        },
    )


# ============================================================
# NORMALIZE TMDB SEARCH RESULT
# ============================================================

# def normalize_movie(movie):

#     poster_path = movie.get("poster_path")

#     return {
#         **movie,
#         "tmdb_id": movie.get("id"),
#         "title": movie.get("title") or movie.get("name") or "",
#         "poster_url": (
#             f"https://image.tmdb.org/t/p/w500{poster_path}"
#             if poster_path
#             else None
#         ),
#         "release_date": movie.get("release_date"),
#         "vote_average": movie.get("vote_average"),
#     }

def normalize_movie(movie):

    poster_path = movie.get("poster_path")

    # Preserve an already-created poster URL
    poster_url = movie.get("poster_url")

    # If poster_url doesn't exist, build it from poster_path
    if not poster_url and poster_path:
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"

    return {
        **movie,

        "tmdb_id": (
            movie.get("tmdb_id")
            or movie.get("id")
        ),

        "title": (
            movie.get("title")
            or movie.get("name")
            or ""
        ),

        "poster_url": poster_url,

        "release_date": (
            movie.get("release_date")
            or movie.get("first_air_date")
            or ""
        ),

        "vote_average": movie.get("vote_average"),
    }


# ============================================================
# MOVIE CARD
# ============================================================

def render_movie_card(movie, key):

    movie = normalize_movie(movie)

    title = html.escape(
        movie.get("title") or "Untitled"
    )

    poster = movie.get("poster_url")

    year = str(
        movie.get("release_date") or ""
    )[:4]

    rating = movie.get("vote_average")

    if poster:

        render_html(
            f"""
            <div class="movie-card">

                <div class="poster-frame">

                    <img
                        src="{poster}"
                        alt="{title}"
                    />

                </div>

                <div class="movie-title">
                    {title}
                </div>

                <div class="movie-meta">
                    {year if year else "—"}
                    &nbsp;&nbsp;·&nbsp;&nbsp;
                    <span class="star">
                        ★ {rating:.1f}
                    </span>
                </div>

            </div>
            """
        )

    else:

        render_html(
            f"""
            <div class="movie-card">

                <div class="poster-frame">

                    <div class="poster-placeholder">
                        No poster available
                    </div>

                </div>

                <div class="movie-title">
                    {title}
                </div>

                <div class="movie-meta">
                    {year if year else "—"}
                </div>

            </div>
            """
        )

    if st.button(
        "View movie",
        key=key,
        use_container_width=True,
    ):

        movie_id = movie.get("tmdb_id")

        details = get_details(movie_id)

        if details:

            st.session_state.selected_movie = movie
            st.session_state.selected_details = details

            st.rerun()


# ============================================================
# MOVIE GRID
# ============================================================

def render_grid(movies, prefix="movie"):

    if not movies:

        render_html(
            """
            <div class="empty">
                No movies found here.
            </div>
            """
        )

        return

    # 5 larger cards
    for start in range(0, len(movies), 5):

        row = movies[start:start + 5]

        cols = st.columns(
            5,
            gap="medium",
        )

        for i, movie in enumerate(row):

            with cols[i]:

                render_movie_card(
                    movie,
                    f"{prefix}_{start}_{i}",
                )


# ============================================================
# NAVIGATION
# ============================================================

render_html(
    """
    <div class="nav">

        <div>
            <div class="logo">
                <span class="logo-mark">▶</span>
                CineMatch
            </div>

            <div class="nav-copy">
                A smarter way to find your next favorite film.
            </div>
        </div>

        <div class="nav-copy">
            Movie Discovery · Recommendations · AI
        </div>

    </div>
    """
)


# ============================================================
# MOVIE DETAILS PAGE
# ============================================================

if st.session_state.selected_movie:

    movie = st.session_state.selected_movie
    details = st.session_state.selected_details

    if st.button("← Back to discovery"):

        st.session_state.selected_movie = None
        st.session_state.selected_details = None

        st.rerun()

    if details:

        title = html.escape(
            details.get("title") or movie.get("title") or ""
        )

        overview = html.escape(
            details.get("overview")
            or "No overview available."
        )

        poster = details.get("poster_url")
        backdrop = details.get("backdrop_url")

        release = details.get("release_date") or ""

        rating = movie.get("vote_average")

        genres = details.get("genres", [])

        # --------------------------------------------
        # DETAILS HERO
        # --------------------------------------------

        if backdrop:

            backdrop_html = f"""
                <img
                    src="{backdrop}"
                    alt="{title}"
                />

                <div class="backdrop-overlay"></div>
            """

        else:

            backdrop_html = """
                <div
                    style="
                        height:390px;
                        background:
                        linear-gradient(
                            135deg,
                            #4b4038,
                            #1e1b19
                        );
                    "
                ></div>
            """

        genre_html = ""

        for genre in genres:

            genre_html += (
                f'<span class="genre">'
                f'{html.escape(str(genre.get("name", "")))}'
                f'</span>'
            )

        rating_text = (
            f"★ {rating:.1f}"
            if isinstance(rating, (int, float))
            else "No rating"
        )

        render_html(
            f"""
            <div class="details-wrap">

                <div class="details-backdrop">

                    {backdrop_html}

                    <div class="details-content">

                        <div class="details-title">
                            {title}
                        </div>

                        <div class="details-meta">
                            {release[:4] if release else "—"}
                            &nbsp;&nbsp;·&nbsp;&nbsp;
                            <span>
                                {rating_text}
                            </span>
                        </div>

                        <div>
                            {genre_html}
                        </div>

                    </div>

                </div>

                <div class="details-body">

                    <div class="section-eyebrow">
                        About the film
                    </div>

                    <div class="overview">
                        {overview}
                    </div>

                </div>

            </div>
            """
        )

        # --------------------------------------------
        # RECOMMENDATIONS
        # --------------------------------------------

        render_html(
            """
            <div class="section">

                <div class="section-eyebrow">
                    Machine learning
                </div>

                <div class="section-title">
                    Films that feel similar
                </div>

                <div class="section-description">
                    Recommendations generated from the movie's
                    textual features using TF-IDF similarity.
                </div>

            </div>
            """
        )

        bundle = get_bundle(
            details.get("title")
        )

        if bundle:

            tfidf_items = bundle.get(
                "tfidf_recommendations",
                [],
            )

            tfidf_movies = []

            for item in tfidf_items:

                tmdb = item.get("tmdb")

                if tmdb:

                    tmdb["similarity_score"] = item.get(
                        "score",
                        0,
                    )

                    tfidf_movies.append(tmdb)

            render_grid(
                tfidf_movies,
                "similar",
            )

            # ----------------------------------------
            # GENRE SECTION
            # ----------------------------------------

            render_html(
                '<div class="soft-divider"></div>'
            )

            render_html(
                """
                <div class="section">

                    <div class="section-eyebrow">
                        Same universe
                    </div>

                    <div class="section-title">
                        More from this genre
                    </div>

                    <div class="section-description">
                        Popular films sharing this movie's
                        primary genre.
                    </div>

                </div>
                """
            )

            genre_movies = bundle.get(
                "genre_recommendations",
                [],
            )

            render_grid(
                genre_movies,
                "genre",
            )

    st.stop()


# ============================================================
# HERO
# ============================================================

render_html(
    """
    <section class="hero">

        <div class="hero-kicker">
            Cinema, curated differently
        </div>

        <h1 class="hero-title">
            Find something<br>
            <em>worth watching.</em>
        </h1>

        <p class="hero-description">
            Explore popular films, discover hidden gems,
            and let machine learning find movies that match
            your taste.
        </p>

        <div class="hero-badge">
            DISCOVER<br>
            SOMETHING<br>
            NEW
        </div>

    </section>
    """
)


# ============================================================
# SEARCH
# ============================================================

render_html(
    '<div class="search-label">Search the collection</div>'
)

search_col, button_col = st.columns(
    [5, 1],
    gap="small",
)

with search_col:

    query = st.text_input(
        "Search movies",
        placeholder="Try “Interstellar”, “Batman”, “Inception”...",
        label_visibility="collapsed",
        key="main_search",
    )

with button_col:

    search_clicked = st.button(
        "Search →",
        use_container_width=True,
    )


# ============================================================
# SEARCH RESULTS
# ============================================================

if search_clicked and query.strip():

    result = search_movies(
        query.strip()
    )

    results = result.get(
        "results",
        [],
    )

    st.session_state.search_results = [
        normalize_movie(movie)
        for movie in results
    ]

    st.session_state.search_query = query.strip()


if st.session_state.search_results:

    render_html(
        f"""
        <div class="section">

            <div class="section-eyebrow">
                Search
            </div>

            <div class="section-title">
                Results for “{
                    html.escape(
                        st.session_state.search_query
                    )
                }”
            </div>

        </div>
        """
    )

    render_grid(
        st.session_state.search_results[:15],
        "search",
    )

    render_html(
        '<div class="soft-divider"></div>'
    )


# ============================================================
# DISCOVER
# ============================================================

render_html(
    """
    <div class="section">

        <div class="section-eyebrow">
            Explore
        </div>

        <div class="section-title">
            What are you in the mood for?
        </div>

        <div class="section-description">
            Browse different corners of the movie world.
        </div>

    </div>
    """
)


categories = {
    "🔥 Trending": "trending",
    "✦ Popular": "popular",
    "★ Top Rated": "top_rated",
    "◉ Now Playing": "now_playing",
    "↗ Upcoming": "upcoming",
}


selected_label = st.radio(
    "Category",
    list(categories.keys()),
    horizontal=True,
    label_visibility="collapsed",
)

selected_category = categories[
    selected_label
]


# ============================================================
# CATEGORY MOVIES
# ============================================================

movies = get_home(
    selected_category
)

render_html(
    f"""
    <div class="section">

        <div class="section-eyebrow">
            {selected_label}
        </div>

        <div class="section-title">
            {selected_label.replace("🔥 ", "")
                          .replace("✦ ", "")
                          .replace("★ ", "")
                          .replace("◉ ", "")
                          .replace("↗ ", "")}
        </div>

    </div>
    """
)

render_grid(
    movies,
    f"home_{selected_category}",
)


# ============================================================
# FOOTER
# ============================================================

render_html("""
    <div class="soft-divider"></div>

    <div style="
        display:flex;
        justify-content:space-between;
        color:#99938a;
        font-size:0.72rem;
        padding-bottom:1rem;
    ">

        <span>
            CineMatch
        </span>

        <span>
            Powered by TMDB · Built with Python & Machine Learning
        </span>

    </div>
    """
)