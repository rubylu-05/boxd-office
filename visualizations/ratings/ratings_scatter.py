import pandas as pd
import plotly.graph_objects as go
from theme import BLUE, GRAY

def plot_ratings_scatter(films_df: pd.DataFrame):
    # drop films without both ratings
    df = films_df.dropna(subset=['rating', 'avg_rating'])

    df = df.sort_values(by='rating', ascending=False)

    df['hover_text'] = df.apply(
        lambda row: (
            f"<span style='color:{BLUE}'><b>{row['title']}</b></span><br>"
            f"<span style='color:{BLUE}'><b>Your Rating:</b></span> {row['rating']}<br>"
            f"<span style='color:{BLUE}'><b>Avg Rating:</b></span> {row['avg_rating']}<br>"
            f"<span style='color:{BLUE}'><b>Year:</b></span> {row['year'] or 'N/A'}"
        ),
        axis=1
    )

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['avg_rating'],
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

    fig.add_shape(
        type="line",
        x0=0, y0=0,
        x1=5, y1=5,
        line=dict(color=BLUE, dash='dash'),
        xref='x', yref='y'
    )

    fig.update_layout(
        title={
            'text': "Your Ratings vs. Average Ratings",
            'font': {'size': 26, 'color': BLUE},
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
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    return fig
