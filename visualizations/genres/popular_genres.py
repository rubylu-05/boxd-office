import pandas as pd
import plotly.graph_objects as go
from theme import BLUE, GRAY
from utils import format_with_linebreaks

def plot_popular_genres(films_df: pd.DataFrame):
    exploded = films_df.explode('genres')
    exploded = exploded.dropna(subset=['genres'])

    genre_counts = exploded.groupby('genres').size().reset_index(name='total')
    liked_counts = exploded[exploded['liked']].groupby('genres').size().reset_index(name='liked')
    genre_data = pd.merge(genre_counts, liked_counts, on='genres', how='left').fillna(0)
    genre_data['liked'] = genre_data['liked'].astype(int)
    genre_data['unliked'] = genre_data['total'] - genre_data['liked']

    genre_data.rename(columns={'genres': 'genre'}, inplace=True)

    genre_examples = exploded.groupby('genres').apply(
        lambda x: x.nlargest(3, 'num_watched')['title'].tolist()
    )
    genre_favourites = exploded.dropna(subset=['rating']).groupby('genres').apply(
        lambda x: x.sort_values('rating', ascending=False).head(3)['title'].tolist()
    )

    genre_data = genre_data.merge(
        genre_examples.rename('examples'),
        left_on='genre',
        right_index=True
    ).merge(
        genre_favourites.rename('favourites'),
        left_on='genre',
        right_index=True,
        how='left'
    )

    genre_data['hover_text'] = genre_data.apply(
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

    genre_data = genre_data.sort_values('total', ascending=True)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=genre_data['genre'],
        x=genre_data['unliked'],
        name='Not Liked',
        orientation='h',
        marker_color='white',
        customdata=genre_data[['hover_text']],
        hovertemplate="%{customdata[0]}<extra></extra>"
    ))

    fig.add_trace(go.Bar(
        y=genre_data['genre'],
        x=genre_data['liked'],
        name='Liked',
        orientation='h',
        marker_color=BLUE,
        customdata=genre_data[['hover_text']],
        hovertemplate="%{customdata[0]}<extra></extra>"
    ))

    fig.update_layout(
        barmode='stack',
        title={
            'text': "Most Watched Genres",
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
            title='Genre',
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
