import pandas as pd
import plotly.graph_objects as go
from theme import ORANGE, GRAY

def plot_popular_themes(films_df: pd.DataFrame):
    exploded = films_df.explode('themes')
    exploded = exploded.dropna(subset=['themes'])

    theme_counts = exploded.groupby('themes').size().reset_index(name='total')
    liked_counts = exploded[exploded['liked']].groupby('themes').size().reset_index(name='liked')
    theme_data = pd.merge(theme_counts, liked_counts, on='themes', how='left').fillna(0)
    theme_data['liked'] = theme_data['liked'].astype(int)
    theme_data['unliked'] = theme_data['total'] - theme_data['liked']

    theme_data.rename(columns={'themes': 'theme'}, inplace=True)

    theme_examples = exploded.groupby('themes').apply(
        lambda x: x.nlargest(3, 'num_watched')['title'].tolist()
    )
    theme_favourites = exploded.dropna(subset=['rating']).groupby('themes').apply(
        lambda x: x.sort_values('rating', ascending=False).head(3)['title'].tolist()
    )

    theme_data = theme_data.merge(
        theme_examples.rename('examples'),
        left_on='theme',
        right_index=True
    ).merge(
        theme_favourites.rename('favourites'),
        left_on='theme',
        right_index=True,
        how='left'
    )

    theme_data = theme_data.nlargest(20, 'total')

    theme_data['hover_text'] = theme_data.apply(
        lambda row: (
            f"<span style='color:{ORANGE}'><b>Number of Films:</b></span> {row['total']}<br>" +
            f"<span style='color:{ORANGE}'><b>Liked:</b></span> {row['liked']} "
            f"({round(100 * row['liked'] / row['total'])}%)<br>" +
            f"<span style='color:{ORANGE}'><b>Examples:</b></span> {', '.join(row['examples'])}<br>" +
            (
                f"<span style='color:{ORANGE}'><b>Your Favourites:</b></span> {', '.join(row['favourites'])}"
                if isinstance(row['favourites'], list) and row['favourites'] else ""
            )
        ),
        axis=1
    )

    theme_data = theme_data.sort_values('total', ascending=True)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=theme_data['theme'],
        x=theme_data['unliked'],
        name='Not Liked',
        orientation='h',
        marker_color='white',
        customdata=theme_data[['hover_text']],
        hovertemplate="%{customdata[0]}<extra></extra>"
    ))

    fig.add_trace(go.Bar(
        y=theme_data['theme'],
        x=theme_data['liked'],
        name='Liked',
        orientation='h',
        marker_color=ORANGE,
        customdata=theme_data[['hover_text']],
        hovertemplate="%{customdata[0]}<extra></extra>"
    ))

    fig.update_layout(
        barmode='stack',
        title={
            'text': "Most Watched Themes",
            'font': {'size': 26, 'color': ORANGE},
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
            title='Theme',
            title_font=dict(size=16, weight='bold'),
        ),
        height=600,
        showlegend=True,
        margin=dict(t=80)
    )

    return fig
