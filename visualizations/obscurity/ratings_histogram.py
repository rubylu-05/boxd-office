import pandas as pd
import plotly.graph_objects as go
from utils import format_with_linebreaks, BLUE, GRAY

def plot_avg_rating_distribution(films_df: pd.DataFrame):
    df = films_df.dropna(subset=['avg_rating']).copy()

    counts, bin_edges = pd.cut(df['avg_rating'], bins=25, retbins=True)
    bin_ranges = [
        f"{bin_edges[i]:.1f} - {bin_edges[i+1]:.1f}"
        for i in range(len(bin_edges)-1)
    ]

    df['bin'] = pd.cut(df['avg_rating'], bins=bin_edges)
    bin_examples = df.groupby('bin', observed=False).apply(
        lambda x: x.nlargest(3, 'num_watched')['title'].tolist()
    )
    bin_examples = bin_examples.reindex(df['bin'].cat.categories)

    bin_counts = df['bin'].value_counts().sort_index()

    hover_texts = []
    for i in range(len(bin_ranges)):
        examples = bin_examples.iloc[i] if i < len(bin_examples) else []
        count = bin_counts.iloc[i] if i < len(bin_counts) else 0

        hover_text = (
            f"<span style='color:{BLUE}'><b>Average Rating:</b></span> {bin_ranges[i]}<br>"
            f"<span style='color:{BLUE}'><b>Number of Films:</b></span> {count}<br>"
            f"<span style='color:{BLUE}'><b>Examples:</b></span> {format_with_linebreaks(examples)}"
        )
        hover_texts.append(hover_text)

    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=df['avg_rating'],
        xbins=dict(
            start=bin_edges[0],
            end=bin_edges[-1],
            size=(bin_edges[-1] - bin_edges[0])/25
        ),
        marker=dict(
            color=BLUE,
        ),
        name='Average Rating Distribution',
        customdata=hover_texts,
        hovertemplate="%{customdata}<extra></extra>"
    ))

    fig.update_layout(
        title={
            'text': "Average Rating Distribution",
            'font': {'size': 26},
            'x': 0.0,
            'xanchor': 'left'
        },
        xaxis=dict(
            title='<b>Average Rating</b>',
            title_font=dict(size=16, color='white'),
            tickfont=dict(color='white'),
            range=[0, 5],
            showgrid=True,
            gridcolor='dark gray'
        ),
        yaxis=dict(
            title='<b>Frequency</b>',
            title_font=dict(size=16, color='white'),
            tickfont=dict(color='white'),
            showgrid=True,
            gridcolor='dark gray'
        ),
        hoverlabel=dict(
            bgcolor=GRAY,
            font_size=13,
            font_color='white',
            align='left'
        ),
        showlegend=False,
        height=350,
        margin=dict(t=80, b=20),
        bargap=0.05
    )

    return fig
