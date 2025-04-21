import pandas as pd
import plotly.express as px
from theme import BLUE, GRAY

def plot_popular_genres(films_df: pd.DataFrame) -> None:
    exploded_genres = films_df.explode('genres')
    
    genre_counts = exploded_genres['genres'].value_counts().reset_index()
    genre_counts.columns = ['genre', 'count']
    
    genre_examples = exploded_genres.groupby('genres').apply(
        lambda x: x.nlargest(3, 'num_watched')['title'].tolist()
    )
    
    genre_data = genre_counts.merge(
        genre_examples.rename('examples'), 
        left_on='genre', 
        right_index=True
    )
    
    genre_data['hover_text'] = genre_data.apply(
        lambda row: f"<span style='color:{BLUE}'><b>Genre:</b></span> {row['genre']}<br>" +
                    f"<span style='color:{BLUE}'><b>Number of Films:</b></span> {row['count']}<br>" +
                    f"<span style='color:{BLUE}'><b>Examples:</b></span> {', '.join(row['examples'])}",
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
        color_continuous_scale='Viridis',
        orientation='h'
    )
    
    fig.update_traces(
        hovertemplate="%{customdata[0]}<extra></extra>",
        marker_coloraxis=None
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
            title='Number of Films',
            title_font=dict(
                size=16,
                weight='bold'
            ),
            categoryorder='total ascending'
        ),
        height=600,
        showlegend=False,
        margin=dict(t=80)
    )
    
    return fig
