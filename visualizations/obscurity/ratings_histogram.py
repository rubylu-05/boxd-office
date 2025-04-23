import pandas as pd
import plotly.graph_objects as go
from utils import BLUE, GRAY

def plot_avg_rating_distribution(films_df: pd.DataFrame):
    # filter films that have average rating data
    df = films_df.dropna(subset=['avg_rating'])

    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=df['avg_rating'],
        xbins=dict(
            start=0,
            end=5,
            size=0.2  # bin size
        ),
        marker=dict(
            color=BLUE,
        ),
        name='Average Rating Distribution',
    ))

    fig.update_layout(
        title={
            'text': "Average Rating Distribution",
            'font': {'size': 26},
            'x': 0.0,
            'xanchor': 'left'
        },
        xaxis=dict(
            title='<b>Average Rating</b>',
            title_font=dict(size=16, color='white'),
            tickfont=dict(color='white'),
            range=[0, 5],
            showgrid=True,
            gridcolor='dark gray'
        ),
        yaxis=dict(
            title='<b>Frequency</b>',
            title_font=dict(size=16, color='white'),
            tickfont=dict(color='white'),
            showgrid=True,
            gridcolor='dark gray'
        ),
        hoverlabel=dict(
            bgcolor=GRAY,
            font_size=13,
            font_color='white',
            align='left'
        ),
        showlegend=False,
        height=350,
        margin=dict(t=80, b=20),
        bargap=0.05
    )

    return fig
