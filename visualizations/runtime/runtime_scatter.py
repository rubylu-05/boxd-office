import pandas as pd
import plotly.graph_objects as go
from theme import BLUE, GRAY

def plot_runtime_scatter(films_df: pd.DataFrame, selected_genres=None):
    # drop films without runtime or rating
    df = films_df.dropna(subset=['runtime', 'rating'])

    # iqr filtering to remove runtime outliers
    q1 = df['runtime'].quantile(0.25)
    q3 = df['runtime'].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    df = df[(df['runtime'] >= lower_bound) & (df['runtime'] <= upper_bound)]
    df = df.sort_values(by='rating', ascending=False)

    df['hover_text'] = df.apply(
        lambda row: (
            f"<span style='color:{BLUE}'><b>Film:</b></span> {row['title']} ({row['year'] or 'N/A'})<br>"
            f"<span style='color:{BLUE}'><b>Runtime:</b></span> {row['runtime']} min<br>"
            f"<span style='color:{BLUE}'><b>Your Rating:</b></span> {row['rating']}<br>"
        ),
        axis=1
    )

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['runtime'],
        y=df['rating'],
        mode='markers',
        marker=dict(
            size=8,
            color=BLUE,
            opacity=0.9,
            line=dict(width=1, color='white')
        ),
        text=df['hover_text'],
        hovertemplate="%{text}<extra></extra>",
        name='Films'
    ))

    fig.update_layout(
        title={
            'text': "Runtime vs. Rating",
            'font': {'size': 26, 'color': BLUE},
            'x': 0.0,
            'xanchor': 'left'
        },
        xaxis=dict(
            title='<b>Runtime (minutes)</b>',
            title_font=dict(size=16, color='white'),
            tickfont=dict(color='white'),
            showgrid=True,
            gridcolor='dark gray'
        ),
        yaxis=dict(
            title='<b>Your Rating</b>',
            title_font=dict(size=16, color='white'),
            tickfont=dict(color='white'),
            range=[0, 5.2],
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
        height=600,
        margin=dict(t=80),
    )

    return fig
