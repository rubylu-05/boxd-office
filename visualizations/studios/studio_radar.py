import pandas as pd
import plotly.graph_objects as go
from utils import BLUE, GRAY

def plot_studio_rating_radar(films_df: pd.DataFrame, top_n: int = 18):
    exploded = films_df.explode('studios')
    exploded = exploded.dropna(subset=['studios', 'rating'])

    studio_counts = exploded['studios'].value_counts()
    top_studios = studio_counts.head(top_n).index if len(studio_counts) > top_n else studio_counts.index

    filtered = exploded[exploded['studios'].isin(top_studios)]

    avg_ratings = (
        filtered.groupby('studios')['rating']
        .mean()
        .reindex(top_studios)
    )

    film_counts = (
        filtered.groupby('studios')['rating']
        .count()
        .reindex(top_studios)
    )

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
        line=dict(color=BLUE),
        marker=dict(size=6),
        customdata=[[cat, val, cnt] for cat, val, cnt in zip(categories, values, counts)],
        hovertemplate="<span style='color:" + BLUE + "'><b>Studio:</b></span> %{customdata[0]}<br>" +
                      "<span style='color:" + BLUE + "'><b>Average Rating:</b></span> %{customdata[1]:.2f}<br>" +
                      "<span style='color:" + BLUE + "'><b>Number of Films:</b></span> %{customdata[2]}<extra></extra>"

    ))

    fig.update_layout(
        title={
            'text': "Average Ratings by Studio",
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
