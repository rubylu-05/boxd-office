import pandas as pd
import plotly.graph_objects as go
from theme import BLUE, GRAY
from utils import format_with_linebreaks

def plot_popular_languages(films_df: pd.DataFrame):
    filtered = films_df.dropna(subset=['language'])

    language_counts = filtered.groupby('language').size().reset_index(name='total')
    liked_counts = filtered[filtered['liked']].groupby('language').size().reset_index(name='liked')
    language_data = pd.merge(language_counts, liked_counts, on='language', how='left').fillna(0)
    language_data['liked'] = language_data['liked'].astype(int)
    language_data['unliked'] = language_data['total'] - language_data['liked']

    language_examples = filtered.groupby('language').apply(
        lambda x: x.nlargest(3, 'num_watched')['title'].tolist()
    )
    language_favourites = filtered.dropna(subset=['rating']).groupby('language').apply(
        lambda x: x.sort_values('rating', ascending=False).head(3)['title'].tolist()
    )

    language_data = language_data.merge(
        language_examples.rename('examples'),
        left_on='language',
        right_index=True
    ).merge(
        language_favourites.rename('favourites'),
        left_on='language',
        right_index=True,
        how='left'
    )

    language_data['hover_text'] = language_data.apply(
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

    language_data = language_data.sort_values('total', ascending=True)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=language_data['language'],
        x=language_data['unliked'],
        name='Not Liked',
        orientation='h',
        marker_color='white',
        customdata=language_data[['hover_text']],
        hovertemplate="%{customdata[0]}<extra></extra>"
    ))

    fig.add_trace(go.Bar(
        y=language_data['language'],
        x=language_data['liked'],
        name='Liked',
        orientation='h',
        marker_color=BLUE,
        customdata=language_data[['hover_text']],
        hovertemplate="%{customdata[0]}<extra></extra>"
    ))

    fig.update_layout(
        barmode='stack',
        title={
            'text': "Most Watched Languages",
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
            title='Language',
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
