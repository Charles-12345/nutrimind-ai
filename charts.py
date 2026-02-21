"""
charts.py
Plotly chart helpers for NutriMind AI
"""
import plotly.graph_objects as go
import plotly.express as px


def render_macro_chart(protein: int, carbs: int, fat: int):
    """Donut chart showing macro breakdown."""
    colors = ["#5cb85c", "#5bc0de", "#f0ad4e"]

    fig = go.Figure(go.Pie(
        labels=["Protein", "Carbs", "Fat"],
        values=[protein * 4, carbs * 4, fat * 9],   # convert to calories
        hole=0.6,
        marker=dict(colors=colors, line=dict(color='white', width=2)),
        textfont=dict(size=13, family="DM Sans"),
        hovertemplate="<b>%{label}</b><br>%{value} kcal<br>%{percent}<extra></extra>"
    ))

    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom", y=-0.2,
            xanchor="center", x=0.5,
            font=dict(family="DM Sans", size=12)
        ),
        margin=dict(t=10, b=30, l=0, r=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        annotations=[dict(
            text=f"<b>{protein*4+carbs*4+fat*9}</b><br>kcal",
            x=0.5, y=0.5, xref='paper', yref='paper',
            showarrow=False,
            font=dict(size=16, family="Syne", color="#1a2e1a")
        )]
    )
    return fig


def render_progress_chart(weight_log: list):
    """Line chart for weight progress over time."""
    if not weight_log:
        return go.Figure()

    dates   = [entry["date"]   for entry in weight_log]
    weights = [entry["weight"] for entry in weight_log]

    fig = go.Figure()

    # Fill area
    fig.add_trace(go.Scatter(
        x=dates, y=weights,
        fill='tozeroy',
        fillcolor='rgba(92,184,92,0.08)',
        line=dict(color='rgba(0,0,0,0)'),
        showlegend=False, hoverinfo='skip'
    ))

    # Main line
    fig.add_trace(go.Scatter(
        x=dates, y=weights,
        mode='lines+markers',
        name='Weight',
        line=dict(color='#2d5a27', width=2.5, shape='spline'),
        marker=dict(size=8, color='#5cb85c', line=dict(color='white', width=2)),
        hovertemplate="<b>%{x}</b><br>%{y} kg<extra></extra>"
    ))

    fig.update_layout(
        title=dict(text="⚖️ Weight Progress", font=dict(family="Syne", size=18)),
        xaxis=dict(showgrid=False, title="Date",
                   title_font=dict(family="DM Sans")),
        yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)',
                   title="Weight (kg)", title_font=dict(family="DM Sans")),
        margin=dict(t=50, b=30, l=50, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        hovermode='x unified'
    )
    return fig


def render_calorie_bar(log: list, goal: int):
    """Bar chart of calories per meal."""
    if not log:
        return go.Figure()

    meals    = [e["meal"]     for e in log]
    calories = [e["calories"] for e in log]
    colors   = ["#5cb85c" if c <= goal/3 else "#f0ad4e" if c <= goal*0.5 else "#d9534f"
                for c in calories]

    fig = go.Figure(go.Bar(
        x=meals, y=calories,
        marker_color=colors,
        text=calories, textposition='outside',
        hovertemplate="<b>%{x}</b><br>%{y} kcal<extra></extra>"
    ))

    fig.add_hline(y=goal, line_dash="dash", line_color="#d9534f",
                  annotation_text="Daily Goal", annotation_position="top right")

    fig.update_layout(
        title=dict(text="🔥 Calories by Meal", font=dict(family="Syne", size=16)),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
        margin=dict(t=50, b=30, l=50, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False
    )
    return fig
