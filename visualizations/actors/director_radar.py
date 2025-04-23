import pandas as pd
import plotly.graph_objects as go
from utils import ORANGE, GRAY

def plot_director_rating_radar(films_df: pd.DataFrame, top_n: int = 18):
    exploded = films_df.explode('directors')
    exploded = exploded.dropna(subset=['directors', 'rating', 'avg_rating'])

    director_counts = exploded['directors'].value_counts()
    top_directors = director_counts.head(top_n).index if len(director_counts) > top_n else director_counts.index

    filtered = exploded[exploded['directors'].isin(top_directors)]

    avg_ratings = (
        filtered.groupby('directors')['rating']
        .mean()
        .reindex(top_directors)
    )

    community_avg_ratings = (
        filtered.groupby('directors')['avg_rating']
        .mean()
        .reindex(top_directors)
    )

    film_counts = (
        filtered.groupby('directors')['rating']
        .count()
        .reindex(top_directors)
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
        hovertemplate="<b>Director:</b> %{customdata[0]}<br>" +
                      "<b>Average Rating:</b> %{customdata[1]:.2f}<br>" +
                      "<b>Number of Films:</b> %{customdata[2]}<extra></extra>",
        visible='legendonly'
    ))

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Your Ratings',
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
        showlegend=True,
        legend=dict(
            font=dict(color='white')
        ),
        height=600,
        margin=dict(t=80)
    )

    return fig
