import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path


def format_count_short(n: float) -> str:
    abs_n = abs(n)
    if abs_n >= 1_000_000_000:
        return f"{n/1_000_000_000:.0f}B"
    if abs_n >= 1_000_000:
        return f"{n/1_000_000:.0f}M"
    if abs_n >= 1_000:
        return f"{n/1_000:.0f}K"
    return f"{n:.0f}"


def compute_funnel(funnel_counts: dict) -> pd.DataFrame:
    stages = list(funnel_counts.keys())
    counts = np.array(list(funnel_counts.values()), dtype=float)
    conv_from_prev = np.r_[1.0, counts[1:] / counts[:-1]]
    conv_from_start = counts / counts[0] if counts[0] else np.zeros_like(counts)
    df = pd.DataFrame(
        {
            "stage": stages,
            "count": counts,
            "conv_from_prev": conv_from_prev,
            "conv_from_start": conv_from_start,
            "drop_from_prev": 1 - conv_from_prev,
        }
    )
    return df


def counts_figure(df_funnel: pd.DataFrame, chart_type: str = "Bar"):
    if chart_type == "Funnel":
        # Plotly funnel chart
        fig = px.funnel(
            df_funnel,
            y="stage",
            x="count",
            title="Safari City — Early Player Funnel (Counts)",
            color_discrete_sequence=["#5ac8fa"],
        )
        fig.update_traces(
            text=df_funnel["count"].apply(format_count_short),
            textposition="outside",
            cliponaxis=False,
        )
        fig.update_layout(margin=dict(l=140, r=20, t=60, b=40))
        return fig

    if chart_type == "Lollipop":
        # Lollipop: line from 0 to value + circle + label
        fig = px.scatter(
            df_funnel,
            x="count",
            y="stage",
            title="Safari City — Early Player Funnel (Counts)",
        )
        # Add stems
        for _, row in df_funnel.iterrows():
            fig.add_shape(
                type="line",
                x0=0,
                y0=row["stage"],
                x1=float(row["count"]),
                y1=row["stage"],
                line=dict(color="#5ac8fa", width=6),
            )
        fig.update_traces(marker=dict(size=12, color="#0ea5e9"))
        # Add text labels outside
        fig.update_traces(
            text=df_funnel["count"].apply(format_count_short),
            textposition="top right",
        )
        fig.update_layout(
            xaxis_title="Players",
            yaxis_title="Stage",
            xaxis=dict(tickformat="~s"),
            margin=dict(l=140, r=20, t=60, b=40),
            showlegend=False,
        )
        return fig

    # Default: Bar
    fig = px.bar(
        df_funnel,
        x="count",
        y="stage",
        orientation="h",
        title="Safari City — Early Player Funnel (Counts)",
        color_discrete_sequence=["#5ac8fa"],
    )
    fig.update_traces(
        text=df_funnel["count"].apply(format_count_short),
        textposition="outside",
        cliponaxis=False,
    )
    fig.update_layout(
        xaxis_title="Players",
        yaxis_title="Stage",
        xaxis=dict(tickformat="~s"),
        margin=dict(l=140, r=20, t=60, b=40),
    )
    return fig


def conversion_figure(df_funnel: pd.DataFrame, chart_type: str = "Bar"):
    df_conv = df_funnel.iloc[1:].copy()
    df_conv["conv_pct"] = (df_conv["conv_from_prev"] * 100).round(1)

    if chart_type == "Funnel Area":
        fig = px.funnel_area(
            df_conv,
            values="conv_pct",
            names="stage",
            title="Conversion From Previous Stage (%) — Funnel Area",
            color_discrete_sequence=px.colors.sequential.Greens,
        )
        fig.update_traces(text=df_conv["conv_pct"].astype(str) + "%")
        fig.update_layout(margin=dict(l=60, r=60, t=60, b=40))
        return fig

    if chart_type == "Slope":
        # Slope graph: show % vs index with labels
        df_slope = df_conv.copy()
        df_slope["idx"] = np.arange(1, len(df_slope) + 1)
        fig = px.line(
            df_slope,
            x="idx",
            y="conv_pct",
            markers=True,
            title="Conversion From Previous Stage (%) — Slope",
        )
        fig.update_traces(text=df_slope["conv_pct"].astype(str) + "%")
        fig.update_layout(
            xaxis=dict(
                tickmode="array",
                tickvals=df_slope["idx"],
                ticktext=df_slope["stage"],
            ),
            yaxis_title="%",
            margin=dict(l=60, r=20, t=60, b=120),
            showlegend=False,
        )
        return fig

    # Default: Bar
    fig = px.bar(
        df_conv,
        x="conv_pct",
        y="stage",
        orientation="h",
        title="Conversion From Previous Stage (%)",
        color_discrete_sequence=["#34c759"],
    )
    fig.update_traces(
        text=df_conv["conv_pct"].astype(str) + "%",
        textposition="outside",
        cliponaxis=False,
    )
    max_pct = float(df_conv["conv_pct"].max()) if not df_conv.empty else 100.0
    fig.update_layout(
        xaxis_title="%",
        yaxis_title="Stage",
        xaxis=dict(range=[0, max(100.0, max_pct + 5)]),
        margin=dict(l=140, r=20, t=60, b=40),
    )
    return fig


def dropoff_waterfall_figure(df_funnel: pd.DataFrame) -> "px.Figure":
    # Compute absolute drop from previous stage
    df = df_funnel.copy()
    if len(df) < 2:
        return px.bar(title="Drop-offs Waterfall (needs ≥2 stages)")
    df["prev_count"] = df["count"].shift(1)
    df["drop_abs"] = df["prev_count"] - df["count"]
    # First stage has no drop; set to 0 for clarity
    df.loc[df.index[0], "drop_abs"] = 0.0
    fig = px.waterfall(
        df,
        x="stage",
        y="drop_abs",
        title="Drop-offs by Stage (Absolute)",
        measure=["relative"] * len(df),
        text=df["drop_abs"].fillna(0).apply(lambda x: f"{int(x):,}"),
        color="drop_abs",
        color_continuous_scale=px.colors.sequential.OrRd,
    )
    fig.update_layout(yaxis_title="Players lost from previous stage", showlegend=False, margin=dict(l=60, r=20, t=60, b=60))
    return fig


def cumulative_conversion_figure(df_funnel: pd.DataFrame) -> "px.Figure":
    if df_funnel.empty:
        return px.line(title="Cumulative Conversion (no data)")
    df = df_funnel.copy()
    df["cum_conv_pct"] = (df["conv_from_start"] * 100).round(1)
    df["idx"] = np.arange(1, len(df) + 1)
    fig = px.line(
        df,
        x="idx",
        y="cum_conv_pct",
        markers=True,
        title="Cumulative Conversion from Start (%)",
    )
    fig.update_traces(text=df["cum_conv_pct"].astype(str) + "%")
    fig.update_layout(
        xaxis=dict(tickmode="array", tickvals=df["idx"], ticktext=df["stage"]),
        yaxis_title="%",
        margin=dict(l=60, r=20, t=60, b=120),
        showlegend=False,
    )
    return fig


def drop_distribution_donut_figure(df_funnel: pd.DataFrame) -> "px.Figure":
    if len(df_funnel) < 2:
        return px.pie(title="Drop Distribution (needs ≥2 stages)")
    df = df_funnel.iloc[1:].copy()
    df["drop_abs"] = (df["drop_from_prev"] * df_funnel["count"].shift(1).iloc[1:].values).astype(float)
    df["drop_abs"] = df["drop_abs"].fillna(0.0)
    if df["drop_abs"].sum() <= 0:
        return px.pie(title="Drop Distribution (no drops)")
    fig = px.pie(
        df,
        values="drop_abs",
        names="stage",
        title="Share of Total Drop by Stage",
        hole=0.5,
        color_discrete_sequence=px.colors.sequential.RdPu,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(margin=dict(l=60, r=20, t=60, b=40))
    return fig


def main():
    st.set_page_config(page_title="Safari City Funnel", layout="wide")
    st.title("Safari City — Early Funnel Dashboard")

    # Defaults (can be edited in the sidebar)
    default_counts = {
        "Install → Open": 10000,
        "Play Tap (Title)": 9200,
        "Tutorial Complete": 8500,
        "L1 Win (First Key)": 8000,
        "Spend First Key (Payoff)": 7600,
        "Reach L3 (Loop Mastery)": 6800,
        "Milestone 1 Reached": 5200,
        "Episode 1 Complete (D0)": 4200,
    }

    st.sidebar.header("Funnel Inputs")
    mode = st.sidebar.radio("Input method", ["Manual", "Upload CSV"], index=0)

    raw_events = {"first_open": None, "level_end": None, "in_app_purchase": None, "app_remove": None, "session_start": None}

    if mode == "Upload CSV":
        st.sidebar.caption("Upload either: (1) stage,count CSV; or (2) Firebase overview CSV")
        uploaded = st.sidebar.file_uploader("Upload CSV", type=["csv"]) 

        def parse_stage_count_csv(df: pd.DataFrame) -> dict:
            cols = {c.strip().lower(): c for c in df.columns}
            if "stage" in cols and "count" in cols:
                stage_col = cols["stage"]
                count_col = cols["count"]
                df2 = df[[stage_col, count_col]].dropna()
                return {str(r[stage_col]): float(r[count_col]) for _, r in df2.iterrows()}
            raise KeyError("stage,count columns not found")

        def parse_firebase_overview_csv(raw_text: str) -> tuple[dict, dict]:
            # Extract the block starting at 'Event name,Event count'
            lines = [ln.strip() for ln in raw_text.splitlines()]
            counts = {}
            in_block = False
            for ln in lines:
                if not in_block and ln.lower().startswith("event name, event count".replace(" ","")):
                    in_block = True
                    continue
                if in_block:
                    if not ln or ln.startswith("#"):
                        break
                    parts = [p.strip() for p in ln.split(",")]
                    if len(parts) >= 2 and parts[0] and parts[1]:
                        name = parts[0].strip().lower()
                        try:
                            val = float(parts[1])
                        except Exception:
                            continue
                        counts[name] = counts.get(name, 0.0) + val
            if not counts:
                # try generic two-column at first non-comment row
                try:
                    df_tmp = pd.read_csv(pd.compat.StringIO(raw_text), comment="#", header=0)
                    return parse_stage_count_csv(df_tmp), {}
                except Exception:
                    return {}, {}
            # Map to a simple 4-stage funnel
            installs = counts.get("first_open", 0.0)
            level_end = counts.get("level_end", 0.0)
            iap = counts.get("in_app_purchase", 0.0)
            uninstall = counts.get("app_remove", 0.0)
            session_start = counts.get("session_start", 0.0)
            if installs or level_end or iap or uninstall:
                return {
                    "Installs": installs,
                    "Level Completed": level_end,
                    "In-App Purchase": iap,
                    "Uninstall": uninstall,
                }, {
                    "first_open": installs,
                    "level_end": level_end,
                    "in_app_purchase": iap,
                    "app_remove": uninstall,
                    "session_start": session_start,
                }
            return {}, {}

        if uploaded is not None:
            try:
                # First try simple stage,count
                df_up = pd.read_csv(uploaded)
                counts_map = parse_stage_count_csv(df_up)
            except Exception:
                try:
                    # Fallback: treat as Firebase overview style with multiple tables
                    uploaded.seek(0)
                    text = uploaded.read().decode("utf-8", errors="ignore")
                    counts_map, raw_events_map = parse_firebase_overview_csv(text)
                    if raw_events_map:
                        raw_events.update(raw_events_map)
                    if not counts_map:
                        raise ValueError("Unsupported CSV format – expected 'stage,count' or Firebase overview with 'Event name,Event count'.")
                except Exception as e:
                    st.sidebar.error(f"Could not read CSV: {e}")
                    counts_map = default_counts
        else:
            counts_map = default_counts
    else:
        counts_map = {}
        for stage, val in default_counts.items():
            counts_map[stage] = st.sidebar.number_input(stage, min_value=0.0, value=float(val), step=100.0)

    # Optional KPI inputs when not provided via CSV
    st.sidebar.header("KPI Events (optional)")
    raw_events["first_open"] = st.sidebar.number_input("first_open (installs)", min_value=0.0, value=float(raw_events["first_open"] or 0.0), step=100.0)
    raw_events["level_end"] = st.sidebar.number_input("level_end (completions)", min_value=0.0, value=float(raw_events["level_end"] or 0.0), step=100.0)
    raw_events["in_app_purchase"] = st.sidebar.number_input("in_app_purchase", min_value=0.0, value=float(raw_events["in_app_purchase"] or 0.0), step=10.0)
    raw_events["app_remove"] = st.sidebar.number_input("app_remove (uninstall)", min_value=0.0, value=float(raw_events["app_remove"] or 0.0), step=10.0)
    raw_events["session_start"] = st.sidebar.number_input("session_start", min_value=0.0, value=float(raw_events["session_start"] or 0.0), step=100.0)

    df_funnel = compute_funnel(counts_map)

    st.sidebar.header("Visualization")
    counts_type = st.sidebar.selectbox("Counts chart", ["Bar", "Funnel", "Lollipop"], index=0)
    conv_type = st.sidebar.selectbox("Conversion chart", ["Bar", "Funnel Area", "Slope"], index=0)

    col1, col2 = st.columns(2)
    with col1:
        fig_counts = counts_figure(df_funnel, counts_type)
        st.plotly_chart(fig_counts, use_container_width=True, theme="streamlit")
    with col2:
        fig_conv = conversion_figure(df_funnel, conv_type)
        st.plotly_chart(fig_conv, use_container_width=True, theme="streamlit")

    st.markdown("---")
    st.subheader("Key Insights")
    if len(df_funnel) > 1:
        insights = df_funnel.iloc[1:].sort_values("drop_from_prev", ascending=False).head(3)
        for _, row in insights.iterrows():
            st.write(f"- Largest drop at '{row['stage']}': {row['drop_from_prev']*100:.1f}% from previous stage")
    else:
        st.write("Add more stages to see insights.")

    st.markdown("---")
    st.subheader("Business Questions")
    st.caption("How many install? What % complete a level? purchase? uninstall? sessions per player?")

    installs = float(raw_events["first_open"] or 0.0)
    level_end = float(raw_events["level_end"] or 0.0)
    iap = float(raw_events["in_app_purchase"] or 0.0)
    uninstall = float(raw_events["app_remove"] or 0.0)
    session_start = float(raw_events["session_start"] or 0.0)

    lvl_completion = (level_end / installs * 100.0) if installs else 0.0
    purchase_rate = (iap / installs * 100.0) if installs else 0.0
    uninstall_rate = (uninstall / installs * 100.0) if installs else 0.0
    avg_sessions_pp = (session_start / installs) if installs else 0.0

    kpi_cols = st.columns(4)
    with kpi_cols[0]:
        st.write("Level completion %")
        st.plotly_chart(go.Figure(go.Indicator(
            mode="gauge+number",
            value=round(lvl_completion, 1),
            number={"suffix": "%"},
            gauge={"axis": {"range": [0, 100]}, "bar": {"color": "#34c759"}},
            title={"text": "Completion"},
        )), use_container_width=True)
    with kpi_cols[1]:
        st.write("Purchase %")
        st.plotly_chart(go.Figure(go.Indicator(
            mode="gauge+number",
            value=round(purchase_rate, 2),
            number={"suffix": "%"},
            gauge={"axis": {"range": [0, 5]}, "bar": {"color": "#5856d6"}},
            title={"text": "Purchase"},
        )), use_container_width=True)
    with kpi_cols[2]:
        st.write("Uninstall %")
        st.plotly_chart(go.Figure(go.Indicator(
            mode="gauge+number",
            value=round(uninstall_rate, 1),
            number={"suffix": "%"},
            gauge={"axis": {"range": [0, 40]}, "bar": {"color": "#ff3b30"}},
            title={"text": "Uninstall"},
        )), use_container_width=True)
    with kpi_cols[3]:
        st.write("Avg sessions / player")
        st.plotly_chart(go.Figure(go.Indicator(
            mode="number",
            value=round(avg_sessions_pp, 2),
            title={"text": "Sessions/Player"},
        )), use_container_width=True)

    # Event counts bar answering "How many install?"
    if any(v > 0 for v in [installs, level_end, iap, uninstall, session_start]):
        df_events = pd.DataFrame({
            "event": ["first_open", "level_end", "in_app_purchase", "app_remove", "session_start"],
            "count": [installs, level_end, iap, uninstall, session_start],
        })
        fig_events = px.bar(df_events, x="event", y="count", title="Firebase Event Counts", color="event")
        fig_events.update_layout(showlegend=False, yaxis_title="Count", xaxis_title="Event")
        st.plotly_chart(fig_events, use_container_width=True, theme="streamlit")

    st.markdown("---")
    st.subheader("More Visuals")
    col3, col4 = st.columns(2)
    with col3:
        st.caption("Drop-offs Waterfall")
        fig_drop = dropoff_waterfall_figure(df_funnel)
        st.plotly_chart(fig_drop, use_container_width=True, theme="streamlit")
    with col4:
        st.caption("Cumulative Conversion Line")
        fig_cum = cumulative_conversion_figure(df_funnel)
        st.plotly_chart(fig_cum, use_container_width=True, theme="streamlit")

    col5, _ = st.columns([2,1])
    with col5:
        st.caption("Drop Distribution Donut")
        fig_donut = drop_distribution_donut_figure(df_funnel)
        st.plotly_chart(fig_donut, use_container_width=True, theme="streamlit")


if __name__ == "__main__":
    main()


