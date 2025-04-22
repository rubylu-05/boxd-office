import pandas as pd
import plotly.graph_objects as go
from theme import BLUE, GRAY
from utils import format_with_linebreaks

def plot_popular_actors(films_df: pd.DataFrame):
    # keep only the first 12 actors from each cast list
    films_df = films_df.copy()
    films_df['cast'] = films_df['cast'].apply(lambda x: x[:12] if isinstance(x, list) else x)

    exploded = films_df.explode('cast')
    exploded = exploded.dropna(subset=['cast'])

    actor_counts = exploded.groupby('cast').size().reset_index(name='total')
    liked_counts = exploded[exploded['liked']].groupby('cast').size().reset_index(name='liked')
    actor_data = pd.merge(actor_counts, liked_counts, on='cast', how='left').fillna(0)
    actor_data['liked'] = actor_data['liked'].astype(int)
    actor_data['unliked'] = actor_data['total'] - actor_data['liked']

    actor_data.rename(columns={'cast': 'actor'}, inplace=True)

    actor_examples = exploded.groupby('cast').apply(
        lambda x: x.nlargest(3, 'num_watched')['title'].tolist()
    )

    actor_data = actor_data.merge(
        actor_examples.rename('examples'),
        left_on='actor',
        right_index=True
    )

    actor_data['hover_text'] = actor_data.apply(
        lambda row: (
            f"<span style='color:{BLUE}'><b>Number of Films:</b></span> {row['total']}<br>" +
            f"<span style='color:{BLUE}'><b>Liked:</b></span> {row['liked']} "
            f"({round(100 * row['liked'] / row['total'])}%)<br>" +
            f"<span style='color:{BLUE}'><b>Examples:</b></span> {format_with_linebreaks(row['examples'])}"
        ),
        axis=1
    )

    actor_data = actor_data.sort_values('total', ascending=True).tail(20)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=actor_data['actor'],
        x=actor_data['unliked'],
        name='Not Liked',
        orientation='h',
        marker_color='white',
        customdata=actor_data[['hover_text']],
        hovertemplate="%{customdata[0]}<extra></extra>"
    ))

    fig.add_trace(go.Bar(
        y=actor_data['actor'],
        x=actor_data['liked'],
        name='Liked',
        orientation='h',
        marker_color=BLUE,
        customdata=actor_data[['hover_text']],
        hovertemplate="%{customdata[0]}<extra></extra>"
    ))

    fig.update_layout(
        barmode='stack',
        title={
            'text': "Most Watched Actors",
            'font': {'size': 26, 'color': BLUE},
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
            title='Actor',
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
