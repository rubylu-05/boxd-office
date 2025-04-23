import pandas as pd
import plotly.express as px
import numpy as np
from utils import format_with_linebreaks, ORANGE, GRAY

def plot_popular_countries_map(films_df: pd.DataFrame):
    exploded = films_df.explode('countries')
    exploded = exploded.dropna(subset=['countries'])

    country_counts = exploded['countries'].value_counts().reset_index()
    country_counts.columns = ['country', 'count']
    country_counts['log_count'] = np.log1p(country_counts['count'])

    country_examples = (
        exploded.groupby('countries')
        .apply(lambda x: x.nlargest(3, 'num_watched')['title'].tolist())
        .rename('examples')
        .reset_index()
    )

    country_counts = country_counts.merge(country_examples, left_on='country', right_on='countries', how='left')
    country_counts['examples'] = country_counts['examples'].fillna('').apply(format_with_linebreaks)

    country_counts['hover_text'] = country_counts.apply(
        lambda row: (
            f"<span style='color:{ORANGE}'><b>Country:</b></span> {row['country']}<br>" +
            f"<span style='color:{ORANGE}'><b>Number of Films:</b></span> {row['count']}<br>" +
            (
                f"<span style='color:{ORANGE}'><b>Examples:</b></span> {row['examples']}"
                if row['examples'] else ""
            )
        ),
        axis=1
    )

    fig = px.choropleth(
        country_counts,
        locations='country',
        locationmode='country names',
        color='log_count',
        color_continuous_scale=[[0, 'white'], [1, ORANGE]],
        range_color=[country_counts['log_count'].min(), country_counts['log_count'].max()],
        height=480  # Reduced height
    )

    fig.update_traces(
        customdata=country_counts[['hover_text']],
        hovertemplate="%{customdata[0]}<extra></extra>"
    )

    fig.update_layout(
        title={
            'text': "Filming & Production Around the World",
            'font': {'size': 26},
            'x': 0.0,
            'xanchor': 'left',
            'yanchor': 'top',
            'y': 0.9
        },
        geo=dict(
            showframe=False,
            showcoastlines=True,
            coastlinecolor='dark gray',
            projection_type='natural earth',
            landcolor='rgba(0,0,0,0)',
            bgcolor='rgba(0,0,0,0)',
            lataxis_range=[-60, 90],
            projection_scale=1,
            center={"lat": 15, "lon": 0}
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=80, b=10),
        coloraxis_showscale=False,
        hoverlabel=dict(
            bgcolor=GRAY,
            font_size=13,
            font_color='white',
            align='left'
        )
    )

    return fig
