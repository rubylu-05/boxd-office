import pandas as pd
import plotly.graph_objects as go
from theme import ORANGE, GRAY

def plot_director_rating_radar(films_df: pd.DataFrame, top_n: int = 18):
    # drop rows where 'director' or 'rating' is NaN
    films_df = films_df.dropna(subset=['director', 'rating'])

    avg_ratings = films_df.groupby('director')['rating'].mean()
    film_counts = films_df.groupby('director').size()
    director_counts = films_df['director'].value_counts()
    top_directors = director_counts.head(top_n).index if len(director_counts) > top_n else director_counts.index
    avg_ratings = avg_ratings[avg_ratings.index.isin(top_directors)]
    film_counts = film_counts[film_counts.index.isin(top_directors)]

    avg_ratings = avg_ratings.reindex(top_directors)
    film_counts = film_counts.reindex(top_directors)

    categories = avg_ratings.index.tolist()
    values = avg_ratings.tolist()
    counts = film_counts.tolist()

    categories.append(categories[0])
    values.append(values[0])
    counts.append(counts[0])

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Average Rating',
        line=dict(color=ORANGE),
        marker=dict(size=6),
        customdata=[[cat, val, cnt] for cat, val, cnt in zip(categories, values, counts)],
        hovertemplate="<span style='color:" + ORANGE + "'><b>Director:</b></span> %{customdata[0]}<br>" +
                      "<span style='color:" + ORANGE + "'><b>Average Rating:</b></span> %{customdata[1]:.2f}<br>" +
                      "<span style='color:" + ORANGE + "'><b>Number of Films:</b></span> %{customdata[2]}<extra></extra>"
    ))

    fig.update_layout(
        title={
            'text': "Average Ratings by Director",
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
        showlegend=False,
        height=600,
        margin=dict(t=80)
    )

    return fig
