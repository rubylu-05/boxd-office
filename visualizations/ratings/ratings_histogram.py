import pandas as pd
import plotly.graph_objects as go
from utils import BLUE, GRAY

def plot_ratings_histogram(films_df: pd.DataFrame, selected_genres=None):
    # filter films that have ratings
    df = films_df.dropna(subset=['rating'])

    df = df[(df['rating'] >= 0.5) & (df['rating'] <= 5.0)]

    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=df['rating'],
        xbins=dict(
            start=0.5,
            end=5.0,
            size=0.5
        ),
        marker=dict(
            color=BLUE,
        ),
        name='Rating Distribution',
    ))

    fig.update_layout(
        title={
            'text': "Rating Distribution",
            'font': {'size': 26},
            'x': 0.0,
            'xanchor': 'left'
        },
        xaxis=dict(
            title='<b>Rating</b>',
            title_font=dict(size=16, color='white'),
            tickfont=dict(color='white'),
            range=[0, 5],
            dtick=1,
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
