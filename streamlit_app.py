import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
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

        def parse_firebase_overview_csv(raw_text: str) -> dict:
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
                    return parse_stage_count_csv(df_tmp)
                except Exception:
                    return {}
            # Map to a simple 4-stage funnel
            installs = counts.get("first_open", 0.0)
            level_end = counts.get("level_end", 0.0)
            iap = counts.get("in_app_purchase", 0.0)
            uninstall = counts.get("app_remove", 0.0)
            if installs or level_end or iap or uninstall:
                return {
                    "Installs": installs,
                    "Level Completed": level_end,
                    "In-App Purchase": iap,
                    "Uninstall": uninstall,
                }
            return {}

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
                    counts_map = parse_firebase_overview_csv(text)
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


if __name__ == "__main__":
    main()


