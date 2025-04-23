import pandas as pd
import plotly.graph_objects as go
from theme import BLUE, GRAY
from utils import format_with_linebreaks

def plot_popular_studios(films_df: pd.DataFrame):
    exploded = films_df.explode('studios')
    exploded = exploded.dropna(subset=['studios'])

    studio_counts = exploded.groupby('studios').size().reset_index(name='total')
    liked_counts = exploded[exploded['liked']].groupby('studios').size().reset_index(name='liked')
    studio_data = pd.merge(studio_counts, liked_counts, on='studios', how='left').fillna(0)
    studio_data['liked'] = studio_data['liked'].astype(int)
    studio_data['unliked'] = studio_data['total'] - studio_data['liked']

    studio_data.rename(columns={'studios': 'studio'}, inplace=True)

    studio_examples = exploded.groupby('studios').apply(
        lambda x: x.nlargest(3, 'num_watched')['title'].tolist()
    )
    studio_favourites = exploded.dropna(subset=['rating']).groupby('studios').apply(
        lambda x: x.sort_values('rating', ascending=False).head(3)['title'].tolist()
    )

    studio_data = studio_data.merge(
        studio_examples.rename('examples'),
        left_on='studio',
        right_index=True
    ).merge(
        studio_favourites.rename('favourites'),
        left_on='studio',
        right_index=True,
        how='left'
    )

    studio_data['hover_text'] = studio_data.apply(
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

    studio_data = studio_data.sort_values('total', ascending=True).tail(20)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=studio_data['studio'],
        x=studio_data['unliked'],
        name='Not Liked',
        orientation='h',
        marker_color='white',
        customdata=studio_data[['hover_text']],
        hovertemplate="%{customdata[0]}<extra></extra>"
    ))

    fig.add_trace(go.Bar(
        y=studio_data['studio'],
        x=studio_data['liked'],
        name='Liked',
        orientation='h',
        marker_color=BLUE,
        customdata=studio_data[['hover_text']],
        hovertemplate="%{customdata[0]}<extra></extra>"
    ))

    fig.update_layout(
        barmode='stack',
        title={
            'text': "Most Watched Studios",
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
            dtick=2
        ),
        yaxis=dict(
            title='Studio',
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
