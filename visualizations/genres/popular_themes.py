import pandas as pd
import plotly.express as px
from theme import ORANGE, GRAY

def plot_popular_themes(films_df: pd.DataFrame):
    exploded_themes = films_df.explode('themes')

    theme_counts = exploded_themes['themes'].value_counts().reset_index()
    theme_counts.columns = ['theme', 'count']

    # top 20 themes
    theme_counts = theme_counts.head(20)

    # examples for top themes
    theme_examples = exploded_themes.groupby('themes').apply(
        lambda x: x.nlargest(3, 'num_watched')['title'].tolist()
    )

    theme_data = theme_counts.merge(
        theme_examples.rename('examples'), 
        left_on='theme', 
        right_index=True
    )

    theme_data['hover_text'] = theme_data.apply(
        lambda row: f"<span style='color:{ORANGE}'><b>Number of Films:</b></span> {row['count']}<br>" +
                    f"<span style='color:{ORANGE}'><b>Examples:</b></span> {', '.join(row['examples'])}",
        axis=1
    )

    # Create the figure with explicit color scale
    fig = px.bar(
        theme_data,
        y='theme',
        x='count',
        title='Most Watched Themes',
        custom_data=['hover_text'],
        labels={'count': 'Number of Films', 'theme': 'Theme'},
        color='count',
        color_continuous_scale=[(0, 'white'), (1, ORANGE)],
        orientation='h'
    )

    fig.update_traces(
        hovertemplate="%{customdata[0]}<extra></extra>"
    )

    fig.update_layout(
        title={
            'text': "Most Watched Themes",
            'font': {
                'size': 26,
                'color': ORANGE,
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
            title='Theme',
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
        cmin=theme_data['count'].min(),
        cmax=theme_data['count'].max()
    )

    return fig