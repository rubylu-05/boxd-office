import pandas as pd
import plotly.graph_objects as go
from theme import ORANGE, GRAY
from utils import format_with_linebreaks

def plot_popular_directors(films_df: pd.DataFrame):

    exploded = films_df.explode('directors')
    exploded = exploded.dropna(subset=['directors'])

    director_counts = exploded.groupby('directors').size().reset_index(name='total')
    liked_counts = exploded[exploded['liked']].groupby('directors').size().reset_index(name='liked')
    director_data = pd.merge(director_counts, liked_counts, on='directors', how='left').fillna(0)
    director_data['liked'] = director_data['liked'].astype(int)
    director_data['unliked'] = director_data['total'] - director_data['liked']

    director_data.rename(columns={'directors': 'director'}, inplace=True)

    director_examples = exploded.groupby('directors').apply(
        lambda x: x.nlargest(3, 'num_watched')['title'].tolist()
    )

    director_data = director_data.merge(
        director_examples.rename('examples'),
        left_on='director',
        right_index=True
    )

    director_data['hover_text'] = director_data.apply(
        lambda row: (
            f"<span style='color:{ORANGE}'><b>Number of Films:</b></span> {row['total']}<br>" +
            f"<span style='color:{ORANGE}'><b>Liked:</b></span> {row['liked']} "
            f"({round(100 * row['liked'] / row['total'])}%)<br>" +
            f"<span style='color:{ORANGE}'><b>Examples:</b></span> {format_with_linebreaks(row['examples'])}"
        ),
        axis=1
    )

    director_data = director_data.sort_values('total', ascending=True).tail(20)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=director_data['director'],
        x=director_data['unliked'],
        name='Not Liked',
        orientation='h',
        marker_color='white',
        customdata=director_data[['hover_text']],
        hovertemplate="%{customdata[0]}<extra></extra>"
    ))

    fig.add_trace(go.Bar(
        y=director_data['director'],
        x=director_data['liked'],
        name='Liked',
        orientation='h',
        marker_color=ORANGE,
        customdata=director_data[['hover_text']],
        hovertemplate="%{customdata[0]}<extra></extra>"
    ))

    fig.update_layout(
        barmode='stack',
        title={
            'text': "Most Watched Directors",
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
            title='Directors',
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
