import pandas as pd
import plotly.graph_objects as go
from theme import ORANGE, GRAY

def plot_ratings_pie(films_df: pd.DataFrame):
    liked_count = films_df['liked'].sum()
    not_liked_count = len(films_df) - liked_count

    labels = ['Liked', 'Not Liked']
    values = [liked_count, not_liked_count]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=[ORANGE, GRAY]),
        textinfo='label',
        pull=[0.1, 0],
        hoverinfo='value+percent'
    )])

    fig.update_layout(
        title='Liked Films',
        title_font={'size': 26, 'color': ORANGE},
        showlegend=False,
        height=400,
        margin=dict(t=80)
    )

    return fig
