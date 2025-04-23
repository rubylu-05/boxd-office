import pandas as pd
import plotly.graph_objects as go
from utils import format_with_linebreaks, BLUE, GRAY

def plot_rating_timeline(films_df: pd.DataFrame):
    # drop rows without rating or date
    valid = films_df.dropna(subset=['date', 'rating'])

    # sort by date
    valid = valid.sort_values('date')

    valid['hover_text'] = valid.apply(
        lambda row: (
            f"<span style='color:{BLUE}'><b>Date:</b></span> {row['date'].strftime('%b %d, %Y')}<br>" +
            f"<span style='color:{BLUE}'><b>Film:</b></span> {row['name']}<br>" +
            f"<span style='color:{BLUE}'><b>Rating:</b></span> {row['rating']:.1f}"
        ),
        axis=1
    )

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=valid['date'],
        y=valid['rating'],
        mode='lines+markers',
        name='Your Ratings',
        line=dict(color=BLUE, width=2),
        marker=dict(size=4),
        customdata=valid[['hover_text']],
        hovertemplate="%{customdata[0]}<extra></extra>"
    ))

    fig.update_layout(
        title={
            'text': "Ratings Over Time",
            'font': {'size': 26},
            'x': 0.0,
            'xanchor': 'left'
        },
        xaxis=dict(
            title='Date Watched',
            title_font=dict(size=16, weight='bold'),
        ),
        yaxis=dict(
            title='Rating',
            title_font=dict(size=16, weight='bold'),
            range=[0, 5.2]
        ),
        hoverlabel=dict(
            bgcolor=GRAY,
            font_size=13,
            font_color='white',
            align='left'
        ),
        height=500,
        margin=dict(t=80)
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor='dark gray',
        gridwidth=0.5
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor='dark gray',
        gridwidth=0.5
    )

    return fig
