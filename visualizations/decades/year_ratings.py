import pandas as pd
import plotly.graph_objects as go
from theme import ORANGE, GRAY
from utils import format_with_linebreaks

def plot_yearly_average_ratings(films_df: pd.DataFrame, group_by_decade=False):
    # drop rows with missing year or rating
    valid = films_df.dropna(subset=['year', 'rating', 'avg_rating'])

    if group_by_decade:
        valid['decade'] = (valid['year'] // 10) * 10
        your_grouped = valid.groupby('decade')
    else:
        your_grouped = valid.groupby('year')

    your_avg = your_grouped['rating'].mean()
    your_total = your_grouped.size()
    your_liked = valid[valid['liked']].groupby('year' if not group_by_decade else 'decade').size()
    your_examples = your_grouped.apply(lambda x: x.nlargest(3, 'num_watched')['title'].tolist())

    overall_avg = your_grouped['avg_rating'].mean()

    data = pd.DataFrame({
        'your_avg': your_avg,
        'overall_avg': overall_avg,
        'total': your_total,
        'liked': your_liked
    }).fillna(0).astype({'total': 'int', 'liked': 'int'})

    data['examples'] = your_examples

    data['hover_text'] = data.apply(
        lambda row: (
            f"<span style='color:{ORANGE}'><b>Year:</b></span> {row.name}<br>" +
            f"<span style='color:{ORANGE}'><b>Average Rating:</b></span> {row['your_avg']:.2f}<br>" +
            f"<span style='color:{ORANGE}'><b>Liked:</b></span> {row['liked']} ({round(100 * row['liked'] / row['total'])}%)<br>" +
            f"<span style='color:{ORANGE}'><b>Number of Films:</b></span> {row['total']}<br>" +
            (
                f"<span style='color:{ORANGE}'><b>Examples:</b></span> {format_with_linebreaks(row['examples'])}"
                if isinstance(row['examples'], list) and row['examples'] else ""
            )
        ),
        axis=1
    )

    data['hover_text_overall'] = data.apply(
        lambda row: (
            f"<span><b>Year:</b></span> {row.name}<br>" +
            f"<span><b>Average Rating:</b></span> {row['overall_avg']:.2f}<br>" +
            f"<span><b>Number of Films:</b></span> {row['total']}"
        ),
        axis=1
    )

    data = data.sort_index()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['overall_avg'],
        mode='lines+markers',
        name='Community Ratings',
        line=dict(color='white', width=2),
        marker=dict(size=4),
        customdata=data[['hover_text_overall']],
        hovertemplate="%{customdata[0]}<extra></extra>"
    ))

    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['your_avg'],
        mode='lines+markers',
        name='Your Ratings',
        line=dict(color=ORANGE, width=2),
        marker=dict(size=4),
        customdata=data[['hover_text']],
        hovertemplate="%{customdata[0]}<extra></extra>"
    ))

    fig.update_layout(
        title={
            'text': "Average Ratings by Year" if not group_by_decade else "Average Ratings by Decade",
            'font': {'size': 26},
            'x': 0.0,
            'xanchor': 'left'
        },
        xaxis=dict(
            title='Year' if not group_by_decade else 'Decade',
            title_font=dict(size=16, weight='bold'),
            tickmode='linear',
            dtick=5 if not group_by_decade else 1
        ),
        yaxis=dict(
            title='Average Rating',
            title_font=dict(size=16, weight='bold'),
            range=[0, 5.2]
        ),
        hoverlabel=dict(
            bgcolor=GRAY,
            font_size=13,
            font_color='white',
            align='left'
        ),
        height=500,
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