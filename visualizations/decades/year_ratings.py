import pandas as pd
import plotly.graph_objects as go
from theme import ORANGE, GRAY

def plot_yearly_average_ratings(films_df: pd.DataFrame):
    # drop rows with missing year or rating
    valid_ratings = films_df.dropna(subset=['year', 'rating'])

    # group by year
    grouped = valid_ratings.groupby('year')
    avg_ratings = grouped['rating'].mean()
    total_counts = grouped.size()
    liked_counts = films_df[films_df['liked']].groupby('year').size()
    examples = grouped.apply(lambda x: x.nlargest(3, 'num_watched')['title'].tolist())

    data = pd.DataFrame({
        'average_rating': avg_ratings,
        'total': total_counts,
        'liked': liked_counts
    }).fillna(0).astype({'total': 'int', 'liked': 'int'})

    data['examples'] = examples

    data['hover_text'] = data.apply(
        lambda row: (
            f"<span style='color:{ORANGE}'><b>Year:</b></span> {row.name}<br>" +
            f"<span style='color:{ORANGE}'><b>Average Rating:</b></span> {row['average_rating']:.2f}<br>" +
            f"<span style='color:{ORANGE}'><b>Liked:</b></span> {row['liked']} ({round(100 * row['liked'] / row['total'])}%)<br>" +
            (
                f"<span style='color:{ORANGE}'><b>Examples:</b></span> {', '.join(row['examples'])}"
                if isinstance(row['examples'], list) and row['examples'] else ""
            )
        ),
        axis=1
    )

    data = data.sort_index()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['average_rating'],
        mode='lines+markers',
        name='Average Rating',
        line=dict(color=ORANGE, width=3),
        marker=dict(size=6),
        customdata=data[['hover_text']],
        hovertemplate="%{customdata[0]}<extra></extra>"
    ))

    fig.update_layout(
        title={
            'text': "Average Movie Rating by Year",
            'font': {'size': 26, 'color': ORANGE},
            'x': 0.0,
            'xanchor': 'left'
        },
        xaxis=dict(
            title='Year',
            title_font=dict(size=16, weight='bold'),
            tickmode='linear',
            dtick=5
        ),
        yaxis=dict(
            title='Average Rating',
            title_font=dict(size=16, weight='bold'),
            range=[0, 5]
        ),
        hoverlabel=dict(
            bgcolor=GRAY,
            font_size=13,
            font_color='white',
            align='left'
        ),
        height=500,
        showlegend=False,
        margin=dict(t=80)
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor='dark gray',
        gridwidth=0.5
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor='dark gray',
        gridwidth=0.5
    )

    return fig
