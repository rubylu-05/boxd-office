import pandas as pd
import numpy as np
import plotly.graph_objects as go
from utils import GREEN

def plot_diary_chart(diary_df: pd.DataFrame):
    diary_df['date'] = pd.to_datetime(diary_df['date'], format='%d %b %Y').dt.normalize()

    diary_daily = diary_df.groupby('date').size().reset_index(name='films_watched')

    end_date = pd.to_datetime('today').normalize()
    start_date = end_date - pd.Timedelta(weeks=52)

    diary_daily = diary_daily[diary_daily['date'].between(start_date, end_date)]

    all_dates = pd.date_range(start=start_date, end=end_date, freq='D').normalize()

    diary_daily = pd.merge(
        pd.DataFrame({'date': all_dates}),
        diary_daily,
        on='date',
        how='left'
    ).fillna(0)

    diary_daily['films_watched'] = diary_daily['films_watched'].astype(int)
    
    # Add weekday and week columns
    diary_daily['weekday'] = diary_daily['date'].dt.weekday  # Monday=0
    diary_daily['week'] = (diary_daily['date'] - start_date).dt.days // 7

    # Calculate dynamic number of weeks
    num_days = (end_date - start_date).days + 1
    num_weeks = (num_days + 6) // 7  # Ceiling division to include partial week at the end

    # Heatmap data and hover date matrix
    heatmap_data = np.zeros((7, num_weeks))  # 7 weekdays × weeks
    hover_dates = np.empty((7, num_weeks), dtype='object')  # Changed dtype to 'object'

    for _, row in diary_daily.iterrows():
        weekday = row['weekday']
        week = row['week']
        if week < num_weeks:
            heatmap_data[weekday, week] = row['films_watched']
            hover_dates[weekday, week] = row['date']
    
    # Fill in missing hover dates
    for week in range(num_weeks):
        for weekday in range(7):
            if hover_dates[weekday, week] is None:  # Check for None (NaT equivalent in object dtype)
                hover_dates[weekday, week] = start_date + pd.Timedelta(weeks=week, days=weekday)

    # Month labels for x-axis
    month_labels = []
    month_positions = []
    current_month = None
    for week in range(num_weeks):
        middle_date = start_date + pd.Timedelta(weeks=week, days=3)
        month = middle_date.strftime('%b')
        if month != current_month:
            month_labels.append(month)
            month_positions.append(week + 0.5)
            current_month = month

    # Color scale
    github_colorscale = [
        [0.0, '#ebedf0'],
        [0.0001, '#9be9a8'],
        [0.25, '#40c463'],
        [0.75, '#30a14e'],
        [1.0, '#216e39']
    ]

    # Create the heatmap
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data,
        x=np.arange(num_weeks),
        y=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        colorscale=github_colorscale,
        hoverinfo='none',
        showscale=False,
        xgap=1,  # Reduced gap between squares
        ygap=1,  # Reduced gap between squares
        xaxis='x',
        yaxis='y'
    ))

    # Update layout
    fig.update_layout(
        title="Diary Activity",
        title_font=dict(size=26),  # Increased title size
        margin=dict(t=120, b=20),  # Increased top margin to push title further up
        height=190,  # Adjusted height to maintain aspect ratio
        xaxis=dict(
            showline=False,
            showgrid=False,
            zeroline=False,
            showticklabels=True,
            tickmode='array',
            tickvals=month_positions,
            ticktext=month_labels,
            side='top',
            tickfont=dict(size=10)
        ),
        yaxis=dict(
            showline=False,
            showgrid=False,
            zeroline=False,
            tickfont=dict(size=10),
            autorange='reversed'
        ),
        autosize=True,  # Ensure the layout adapts to content size
    )

    # Add hover info
    fig.update_traces(
        hovertemplate="<b>%{customdata|%b %d, %Y}</b><br>Films watched: %{z}<extra></extra>",
        customdata=hover_dates
    )

    return fig
