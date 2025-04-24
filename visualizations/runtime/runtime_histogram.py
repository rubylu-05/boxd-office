import pandas as pd
import plotly.graph_objects as go
from utils import format_with_linebreaks, BLUE, GRAY

def plot_runtime_histogram(films_df: pd.DataFrame):
    df = films_df.dropna(subset=['runtime'])

    df = df[(df['runtime'] >= 20) & (df['runtime'] <= 300)]

    bin_edges = list(range(20, 301, 10))
    bin_ranges = [
        f"{bin_edges[i]} - {bin_edges[i+1]}"
        for i in range(len(bin_edges)-1)
    ]

    df['bin'] = pd.cut(df['runtime'], bins=bin_edges, right=False)
    
    bin_counts = df['bin'].value_counts().sort_index()
    
    bin_examples = df.groupby('bin').apply(
        lambda x: x.nlargest(3, 'num_watched')['title'].tolist()
    )
    bin_examples = bin_examples.reindex(df['bin'].cat.categories, fill_value=[])

    hover_texts = []
    for i, bin_range in enumerate(bin_ranges):
        count = bin_counts.get(df['bin'].cat.categories[i], 0)
        
        examples = bin_examples.get(df['bin'].cat.categories[i], [])
        
        hover_text = (
            f"<span style='color:{BLUE}'><b>Runtime:</b></span> {bin_range}<br>"
            f"<span style='color:{BLUE}'><b>Number of Films:</b></span> {count}<br>"
            f"<span style='color:{BLUE}'><b>Examples:</b></span> {format_with_linebreaks(examples)}"
        )
        hover_texts.append(hover_text)

    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=df['runtime'],
        xbins=dict(
            start=20,
            end=300,
            size=10
        ),
        marker=dict(
            color=BLUE,
        ),
        name='Runtime Distribution',
        customdata=hover_texts,
        hovertemplate="%{customdata}<extra></extra>"
    ))

    fig.update_layout(
        title={
            'text': "Runtime Distribution",
            'font': {'size': 26},
            'x': 0.0,
            'xanchor': 'left'
        },
        xaxis=dict(
            title='<b>Runtime (minutes)</b>',
            title_font=dict(size=16, color='white'),
            tickfont=dict(color='white'),
            range=[0, 310],
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