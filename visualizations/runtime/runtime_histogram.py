import pandas as pd
import plotly.graph_objects as go
from utils import BLUE, GRAY

def plot_runtime_histogram(films_df: pd.DataFrame):
    # filter films that have runtimes
    df = films_df.dropna(subset=['runtime'])

    df = df[(df['runtime'] >= 20) & (df['runtime'] <= 300)]

    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=df['runtime'],
        xbins=dict(
            start=20,
            end=300,
            size=10  # 10-minute bins
        ),
        marker=dict(
            color=BLUE,
        ),
        name='Runtime Distribution',
    ))

    fig.update_layout(
        title={
            'text': "Runtime Distribution",
            'font': {'size': 26},
            'x': 0.0,
            'xanchor': 'left'
        },
        xaxis=dict(
            title='<b>Runtime (minutes)</b>',
            title_font=dict(size=16, color='white'),
            tickfont=dict(color='white'),
            range=[0, 310],
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
