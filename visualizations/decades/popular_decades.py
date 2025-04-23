import pandas as pd
import plotly.graph_objects as go
from utils import format_with_linebreaks, BLUE, GRAY

def plot_popular_decades(films_df: pd.DataFrame):
    films_df = films_df.dropna(subset=['year'])
    films_df['decade'] = (films_df['year'] // 10 * 10).astype(int).astype(str) + "s"

    decade_counts = films_df.groupby('decade').size().reset_index(name='total')
    liked_counts = films_df[films_df['liked']].groupby('decade').size().reset_index(name='liked')
    decade_data = pd.merge(decade_counts, liked_counts, on='decade', how='left').fillna(0)
    decade_data['liked'] = decade_data['liked'].astype(int)
    decade_data['unliked'] = decade_data['total'] - decade_data['liked']

    decade_examples = films_df.groupby('decade').apply(
        lambda x: x.nlargest(3, 'num_watched')['title'].tolist()
    )
    decade_favourites = films_df.dropna(subset=['rating']).groupby('decade').apply(
        lambda x: x.sort_values('rating', ascending=False).head(3)['title'].tolist()
    )

    decade_data = decade_data.merge(
        decade_examples.rename('examples'),
        left_on='decade',
        right_index=True
    ).merge(
        decade_favourites.rename('favourites'),
        left_on='decade',
        right_index=True,
        how='left'
    )

    decade_data['hover_text'] = decade_data.apply(
        lambda row: (
            f"<span style='color:{BLUE}'><b>Number of Films:</b></span> {row['total']}<br>" +
            f"<span style='color:{BLUE}'><b>Liked:</b></span> {row['liked']} "
            f"({round(100 * row['liked'] / row['total'])}%)<br>" +
            f"<span style='color:{BLUE}'><b>Examples:</b></span> {format_with_linebreaks(row['examples'])}<br>" +
            (
                f"<span style='color:{BLUE}'><b>Your Favourites:</b></span> {format_with_linebreaks(row['favourites'])}"
                if isinstance(row['favourites'], list) and row['favourites'] else ""
            )
        ),
        axis=1
    )

    # sort by decade chronologically
    decade_data['decade_numeric'] = decade_data['decade'].str[:-1].astype(int)
    decade_data = decade_data.sort_values('decade_numeric')

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=decade_data['decade'],
        x=decade_data['unliked'],
        name='Not Liked',
        orientation='h',
        marker_color='white',
        customdata=decade_data[['hover_text']],
        hovertemplate="%{customdata[0]}<extra></extra>"
    ))

    fig.add_trace(go.Bar(
        y=decade_data['decade'],
        x=decade_data['liked'],
        name='Liked',
        orientation='h',
        marker_color=BLUE,
        customdata=decade_data[['hover_text']],
        hovertemplate="%{customdata[0]}<extra></extra>"
    ))

    fig.update_layout(
        barmode='stack',
        title={
            'text': "Most Watched Decades",
            'font': {'size': 26},
            'x': 0.0,
            'xanchor': 'left'
        },
        hoverlabel=dict(
            bgcolor=GRAY,
            font_size=13,
            font_color='white',
            align='left'
        ),
        xaxis=dict(
            title='Number of Films',
            title_font=dict(size=16, weight='bold'),
        ),
        yaxis=dict(
            title='Decade',
            title_font=dict(size=16, weight='bold'),
        ),
        height=600,
        showlegend=True,
        margin=dict(t=80)
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor='dark gray',
        gridwidth=0.5
    )

    return fig
