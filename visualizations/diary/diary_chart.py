import pandas as pd
import numpy as np
import plotly.graph_objects as go
from utils import GRAY, GREEN

def plot_diary_chart(diary_df: pd.DataFrame):
    diary_df['date'] = pd.to_datetime(diary_df['date'], format='%d %b %Y').dt.normalize()

    # group by date: count and list of films
    diary_daily = diary_df.groupby('date').agg({
        'name': lambda x: ', '.join(x),
    }).rename(columns={'name': 'films_list'}).reset_index()

    diary_counts = diary_df.groupby('date').size().reset_index(name='films_watched')
    diary_daily = pd.merge(diary_daily, diary_counts, on='date')

    end_date = pd.to_datetime('today').normalize()
    start_date = end_date - pd.Timedelta(weeks=52)

    diary_daily = diary_daily[diary_daily['date'].between(start_date, end_date)]

    all_dates = pd.date_range(start=start_date, end=end_date, freq='D').normalize()

    diary_daily = pd.merge(
        pd.DataFrame({'date': all_dates}),
        diary_daily,
        on='date',
        how='left'
    ).fillna({'films_watched': 0, 'films_list': ''})

    diary_daily['films_watched'] = diary_daily['films_watched'].astype(int)

    weekday_offset = start_date.weekday()
    num_days = (end_date - start_date).days + 1
    num_weeks = (num_days + 6) // 7

    heatmap_data = np.zeros((7, num_weeks))
    hover_dates = np.empty((7, num_weeks), dtype='datetime64[ns]')
    valid_hover = np.full((7, num_weeks), False)
    films_lists = np.empty((7, num_weeks), dtype=object)

    for week in range(num_weeks):
        for weekday in range(7):
            current_date = start_date + pd.Timedelta(days=week * 7 + weekday - weekday_offset)
            if current_date > end_date:
                heatmap_data[weekday, week] = None
                hover_dates[weekday, week] = None
                continue
            match = diary_daily[diary_daily['date'] == current_date]
            if not match.empty:
                heatmap_data[weekday, week] = match.iloc[0]['films_watched']
                films_lists[weekday, week] = match.iloc[0]['films_list']
            hover_dates[weekday, week] = current_date
            valid_hover[weekday, week] = True

    month_labels = []
    month_positions = []

    current_month = start_date.strftime('%b')
    month_changes = []

    for week in range(num_weeks + 1):
        date = start_date + pd.Timedelta(weeks=week)
        month = date.strftime('%b')
        if month != current_month:
            month_changes.append((week, current_month))
            current_month = month

    if len(month_changes) == 0 or month_changes[-1][1] != current_month:
        month_changes.append((num_weeks, current_month))

    prev_week = 0
    for i in range(len(month_changes)):
        week, month = month_changes[i]
        month_width = week - prev_week
        if month_width >= 2:
            middle_position = prev_week + month_width / 2
            month_labels.append(month)
            month_positions.append(middle_position)
        prev_week = week

    max_films = np.nanmax(heatmap_data) if np.nanmax(heatmap_data) > 0 else 1
    if max_films == 1:
        colorscale = [
            [0, GRAY],
            [0.999, GRAY],
            [1, GREEN]
        ]
    else:
        colorscale = [[0, GRAY]]
        steps = 10
        for i in range(1, steps + 1):
            value = i / steps
            opacity = min(0.2 + (value * 0.8), 1.0)
            green_rgba = f'rgba({int(GREEN[1:3], 16)}, {int(GREEN[3:5], 16)}, {int(GREEN[5:7], 16)}, {opacity})'
            colorscale.append([value, green_rgba])

    hover_text = np.empty((7, num_weeks), dtype=object)
    for i in range(7):
        for j in range(num_weeks):
            if valid_hover[i, j]:
                date_str = pd.to_datetime(str(hover_dates[i, j])).strftime('%b %d, %Y')
                count = int(heatmap_data[i, j])
                film_names = films_lists[i, j] or ""
                hover = (
                    f"<span style='color:{GREEN}'><b>Date:</b></span> {date_str}<br>"
                    f"<span style='color:{GREEN}'><b>Number of Films:</b></span> {count}"
                )
                if count > 0:
                    hover += f"<br><span style='color:{GREEN}'><b>Films Watched:</b></span> {film_names}"
                hover_text[i, j] = hover
            else:
                hover_text[i, j] = None

    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data,
        x=np.arange(num_weeks),
        y=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        colorscale=colorscale,
        hoverinfo='text',
        hovertext=hover_text,
        showscale=False,
        xgap=1,
        ygap=1,
        xaxis='x',
        yaxis='y',
        zmin=0,
        zmax=max_films
    ))

    fig.update_layout(
        margin=dict(t=10, b=50),
        height=175,
        xaxis=dict(
            showline=False,
            showgrid=False,
            zeroline=False,
            showticklabels=True,
            tickmode='array',
            tickvals=month_positions,
            ticktext=month_labels,
            side='top',
            ticks="",
            tickangle=0,
        ),
        yaxis=dict(
            showline=False,
            showgrid=False,
            zeroline=False,
            showticklabels=True,
            ticks="",
            autorange='reversed'
        ),
        autosize=True,
        hoverlabel=dict(
            bgcolor=GRAY,
            font_size=13,
            font_color='white',
            align='left'
        )
    )

    return fig
