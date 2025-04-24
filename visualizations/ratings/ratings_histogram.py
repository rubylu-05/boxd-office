import pandas as pd
import plotly.graph_objects as go
from utils import BLUE, GRAY
import numpy as np

def plot_ratings_histogram(films_df: pd.DataFrame, selected_genres=None):
    df = films_df.dropna(subset=['rating'])
    df = df[(df['rating'] >= 0.5) & (df['rating'] <= 5.0)]

    bins = np.arange(0.5, 5.6, 0.5)
    counts, bin_edges = np.histogram(df['rating'], bins=bins)

    hover_texts = [
        f"<span style='color:{BLUE}'><b>Rating:</b></span> {(bin_edges[i+1] - 0.5):.1f}<br>"
        f"<span style='color:{BLUE}'><b>Number of Films:</b></span> {counts[i]}"
        for i in range(len(counts))
    ]

    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=df['rating'],
        xbins=dict(
            start=0.5,
            end=5.5,
            size=0.5
        ),
        marker=dict(color=BLUE),
        name='Rating Distribution',
        hovertext=hover_texts,
        hovertemplate="%{hovertext}<extra></extra>",
        autobinx=False
    ))

    fig.update_layout(
        title=dict(
            text="Rating Distribution",
            font=dict(size=26),
            x=0.0,
            xanchor='left'
        ),
        xaxis=dict(
            title='<b>Rating</b>',
            title_font=dict(size=16, color='white'),
            tickfont=dict(color='white'),
            range=[0, 5.5],
            tickvals=[1, 2, 3, 4, 5],
            ticktext=[str(i) for i in range(1, 6)],
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
