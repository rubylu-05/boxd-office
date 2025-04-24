import pandas as pd
import plotly.graph_objects as go
from utils import ORANGE, GRAY

def plot_liked_pie(films_df: pd.DataFrame):
    liked_count = films_df['liked'].sum()
    not_liked_count = len(films_df) - liked_count
    total = len(films_df)

    labels = ['Liked', 'Not Liked']
    values = [liked_count, not_liked_count]
    percentages = [round(liked_count / total * 100), round(not_liked_count / total * 100)]
    custom_text = [
        f"<span style='color:{ORANGE}'><b>Liked:</b></span> {liked_count} ({percentages[0]}%)",
        f"<span style='color:{ORANGE}'><b>Not Liked:</b></span> {not_liked_count} ({percentages[1]}%)"
    ]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=[ORANGE, GRAY]),
        textinfo='label',
        pull=[0.1, 0],
        hoverinfo='skip',
        customdata=custom_text,
        hovertemplate="%{customdata}<extra></extra>"
    )])

    fig.update_layout(
        title='Liked Films',
        title_font={'size': 26},
        showlegend=False,
        height=400,
        margin=dict(t=80),
        hoverlabel=dict(
            bgcolor=GRAY,
            font_size=13,
            font_color='white',
            align='left'
        )
    )

    return fig
