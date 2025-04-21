import pandas as pd
import plotly.express as px
from theme import BLUE, GRAY

def plot_popular_genres(films_df: pd.DataFrame):
    exploded_genres = films_df.explode('genres')

    genre_counts = exploded_genres['genres'].value_counts().reset_index()
    genre_counts.columns = ['genre', 'count']

    genre_examples = exploded_genres.groupby('genres').apply(
        lambda x: x.nlargest(3, 'num_watched')['title'].tolist()
    )

    genre_favourites = exploded_genres.dropna(subset=['rating']).groupby('genres').apply(
        lambda x: x.sort_values('rating', ascending=False).head(3)['title'].tolist()
    )

    genre_data = genre_counts.merge(
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
            f"<span style='color:{BLUE}'><b>Number of Films:</b></span> {row['count']}<br>" +
            f"<span style='color:{BLUE}'><b>Examples:</b></span> {', '.join(row['examples'])}<br>" +
            (
                f"<span style='color:{BLUE}'><b>Your Favourites:</b></span> {', '.join(row['favourites'])}"
                if isinstance(row['favourites'], list) and row['favourites'] else ""
            )
        ),
        axis=1
    )

    fig = px.bar(
        genre_data,
        y='genre',
        x='count',
        title='Most Watched Genres',
        custom_data=['hover_text'],
        labels={'count': 'Number of Films', 'genre': 'Genre'},
        color='count',
        color_continuous_scale=[(0, 'white'), (1, BLUE)],
        orientation='h'
    )

    fig.update_traces(
        hovertemplate="%{customdata[0]}<extra></extra>"
    )

    fig.update_layout(
        title={
            'text': "Most Watched Genres",
            'font': {
                'size': 26,
                'color': BLUE,
            },
            'x': 0.0,
            'xanchor': 'left',
        },
        hoverlabel=dict(
            bgcolor=GRAY,
            font_size=13,
            font_color='white',
            align='left',
        ),
        xaxis=dict(
            title='Number of Films',
            title_font=dict(
                size=16,
                weight='bold'
            )
        ),
        yaxis=dict(
            title='Genre',
            title_font=dict(
                size=16,
                weight='bold'
            ),
            categoryorder='total ascending'
        ),
        height=600,
        showlegend=False,
        margin=dict(t=80),
        coloraxis_showscale=False
    )

    fig.update_coloraxes(
        cmin=genre_data['count'].min(),
        cmax=genre_data['count'].max()
    )

    return fig
