import pandas as pd
import plotly.graph_objects as go
from utils import BLUE, GRAY

def plot_genre_rating_radar(films_df: pd.DataFrame, top_n: int = 18):
    exploded = films_df.explode('genres')
    exploded = exploded.dropna(subset=['genres', 'rating', 'avg_rating'])

    genre_counts = exploded['genres'].value_counts()
    top_genres = genre_counts.head(top_n).index if len(genre_counts) > top_n else genre_counts.index

    filtered = exploded[exploded['genres'].isin(top_genres)]

    avg_ratings = (
        filtered.groupby('genres')['rating']
        .mean()
        .reindex(top_genres)
    )

    community_avg_ratings = (
        filtered.groupby('genres')['avg_rating']
        .mean()
        .reindex(top_genres)
    )

    film_counts = (
        filtered.groupby('genres')['rating']
        .count()
        .reindex(top_genres)
    )

    categories = avg_ratings.index.tolist()
    values = avg_ratings.tolist()
    community_values = community_avg_ratings.tolist()
    counts = film_counts.tolist()

    categories.append(categories[0])
    values.append(values[0])
    community_values.append(community_values[0])
    counts.append(counts[0])

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=community_values,
        theta=categories,
        fill='toself',
        name='Community Ratings',
        line=dict(color='white', width=2),
        marker=dict(size=6),
        customdata=[[cat, val, cnt] for cat, val, cnt in zip(categories, community_values, counts)],
        hovertemplate="<b>Genre:</b> %{customdata[0]}<br>" +
                      "<b>Average Rating:</b> %{customdata[1]:.2f}<br>" +
                      "<b>Number of Films:</b> %{customdata[2]}<extra></extra>",
        visible='legendonly'
    ))

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Your Ratings',
        line=dict(color=BLUE),
        marker=dict(size=6),
        customdata=[[cat, val, cnt] for cat, val, cnt in zip(categories, values, counts)],
        hovertemplate="<span style='color:" + BLUE + "'><b>Genre:</b></span> %{customdata[0]}<br>" +
                      "<span style='color:" + BLUE + "'><b>Average Rating:</b></span> %{customdata[1]:.2f}<br>" +
                      "<span style='color:" + BLUE + "'><b>Number of Films:</b></span> %{customdata[2]}<extra></extra>"
    ))

    fig.update_layout(
        title={
            'text': "Average Ratings by Genre",
            'font': {'size': 26},
            'x': 0.0,
            'xanchor': 'left'
        },
        polar=dict(
            bgcolor=GRAY,
            radialaxis=dict(
                visible=True,
                range=[0, 5],
                showticklabels=False,
                title_font=dict(size=16, color='white'),
                gridcolor='white',
                ticks='',
                showline=False,
            ),
            angularaxis=dict(
                tickfont=dict(size=13, color='white'),
                gridcolor='white'
            )
        ),
        hoverlabel=dict(
            bgcolor=GRAY,
            font_size=13,
            font_color='white',
            align='left'
        ),
        showlegend=True,
        legend=dict(
            font=dict(color='white')
        ),
        height=600,
        margin=dict(t=80, b=100, l=100, r=100)
    )

    return fig
