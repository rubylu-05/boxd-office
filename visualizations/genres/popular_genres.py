import pandas as pd
import plotly.express as px

def plot_popular_genres(films_df: pd.DataFrame) -> None:
    exploded_genres = films_df.explode('genres')
    
    genre_counts = exploded_genres['genres'].value_counts().reset_index()
    genre_counts.columns = ['genre', 'count']
    
    # top 3 most watched films for each genre (by num_watched)
    genre_examples = exploded_genres.groupby('genres').apply(
        lambda x: x.nlargest(3, 'num_watched')['title'].tolist()
    )
    
    genre_data = genre_counts.merge(
        genre_examples.rename('examples'), 
        left_on='genre', 
        right_index=True
    )
    
    genre_data['hover_text'] = genre_data.apply(
        lambda row: f"<b>Genre:</b> {row['genre']}<br>" +
                    f"<b>Number of Films:</b> {row['count']}<br>" +
                    f"<b>Examples:</b> {', '.join(row['examples'])}",
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
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
        ),
        yaxis={'categoryorder': 'total ascending'},
        height=600,
        showlegend=False
    )
    
    return fig