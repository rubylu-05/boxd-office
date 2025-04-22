import pandas as pd
import plotly.graph_objects as go
from theme import BLUE, GRAY

def plot_members_histogram(films_df: pd.DataFrame):
    # filter films that have num_watched data
    df = films_df.dropna(subset=['num_watched'])

    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=df['num_watched'],
        nbinsx=40,  # auto-binned into 40 bins
        marker=dict(
            color=BLUE,
        ),
        name='Popularity Distribution',
    ))

    fig.update_layout(
        title={
            'text': "Film Popularity Distribution",
            'font': {'size': 26, 'color': BLUE},
            'x': 0.0,
            'xanchor': 'left'
        },
        xaxis=dict(
            title='<b>Number of People Watched</b>',
            title_font=dict(size=16, color='white'),
            tickfont=dict(color='white'),
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
