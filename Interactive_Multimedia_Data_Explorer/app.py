import io
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

st.set_page_config(page_title="Interactive Multimedia Data Explorer", page_icon="🧭", layout="wide")

st.markdown("""
<style>
.main {background: #f7f9fc;}
.block-container {padding-top: 2rem; padding-bottom: 2rem;}
.hero {padding: 1.4rem 1.6rem; border-radius: 18px; background: linear-gradient(120deg,#12243a,#286b78); color: white; margin-bottom: 1rem;}
.hero h1 {color: white; margin-bottom: .25rem;}
.small-muted {color: #667085;}
</style>
<div class="hero">
<h1>🧭 Interactive Multimedia Data Explorer</h1>
Explore datasets, discover patterns with interactive charts, and edit images in one simple dashboard.
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("Navigation")
    section = st.radio("Choose a workspace", ["📊 Data Explorer", "🖼️ Image Studio", "ℹ️ About Project"])
    st.divider()
    st.caption("Built with Streamlit, Pandas, Plotly and Pillow.")

def sample_dataframe():
    return pd.DataFrame({
        "City": ["Pune", "Mumbai", "Nagpur", "Nashik", "Pune", "Mumbai", "Aurangabad", "Nagpur", "Nashik", "Pune", "Mumbai", "Aurangabad"],
        "Category": ["Air Quality", "Transport", "Air Quality", "Water", "Transport", "Water", "Air Quality", "Transport", "Water", "Air Quality", "Transport", "Water"],
        "Month": ["Jan", "Jan", "Feb", "Feb", "Mar", "Mar", "Apr", "Apr", "May", "May", "Jun", "Jun"],
        "Value": [72, 85, 61, 68, 91, 74, 55, 88, 70, 64, 93, 66],
        "Score": [7.2, 8.5, 6.1, 6.8, 9.1, 7.4, 5.5, 8.8, 7.0, 6.4, 9.3, 6.6]
    })

if section == "📊 Data Explorer":
    st.subheader("Explore your dataset")
    st.write("Upload a CSV file or start with the built-in sample dataset.")
    uploaded = st.file_uploader("Upload CSV", type=["csv"], help="Your file is processed in this app session.")
    try:
        if uploaded is not None:
            df = pd.read_csv(uploaded)
            source_name = uploaded.name
        else:
            df = sample_dataframe()
            source_name = "Built-in sample dataset"
    except Exception as exc:
        st.error(f"Could not read this CSV: {exc}")
        st.stop()

    if df.empty:
        st.warning("The dataset is empty.")
        st.stop()

    st.caption(f"Data source: **{source_name}** · {len(df):,} rows · {len(df.columns)} columns")
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = df.select_dtypes(exclude="number").columns.tolist()

    c1, c2, c3 = st.columns(3)
    c1.metric("Rows", f"{len(df):,}")
    c2.metric("Columns", len(df.columns))
    c3.metric("Missing cells", f"{int(df.isna().sum().sum()):,}")

    with st.expander("Filter data", expanded=True):
        filtered = df.copy()
        f1, f2 = st.columns(2)
        if categorical_cols:
            cat_col = f1.selectbox("Filter by category column", ["No filter"] + categorical_cols)
            if cat_col != "No filter":
                choices = sorted(filtered[cat_col].dropna().astype(str).unique().tolist())
                selected = f2.multiselect("Choose values", choices, default=choices)
                filtered = filtered[filtered[cat_col].astype(str).isin(selected)]
        if numeric_cols:
            num_filter = st.selectbox("Optional numeric range filter", ["No filter"] + numeric_cols)
            if num_filter != "No filter":
                series = pd.to_numeric(filtered[num_filter], errors="coerce").dropna()
                if not series.empty:
                    lo, hi = float(series.min()), float(series.max())
                    if lo == hi:
                        filtered = filtered[pd.to_numeric(filtered[num_filter], errors="coerce") == lo]
                    else:
                        low, high = st.slider("Range", min_value=lo, max_value=hi, value=(lo, hi))
                        vals = pd.to_numeric(filtered[num_filter], errors="coerce")
                        filtered = filtered[vals.between(low, high)]

    left, right = st.columns([1.3, 1])
    with left:
        st.markdown("#### Dataset preview")
        st.dataframe(filtered, use_container_width=True, height=280)
        st.download_button("⬇️ Download filtered CSV", filtered.to_csv(index=False).encode("utf-8"), "filtered_dataset.csv", "text/csv")
    with right:
        st.markdown("#### Quick summary")
        st.dataframe(filtered.describe(include="all").transpose().fillna("—"), use_container_width=True, height=280)

    st.markdown("---")
    st.subheader("Interactive visualization")
    if not numeric_cols:
        st.info("This dataset has no numeric columns to plot. Upload a CSV containing at least one numeric column.")
    else:
        chart_type = st.selectbox("Chart type", ["Bar chart", "Line chart", "Scatter plot", "Histogram", "Box plot", "Pie chart"])
        x_default = categorical_cols[0] if categorical_cols else numeric_cols[0]
        x_options = list(filtered.columns)
        x_col = st.selectbox("X axis / category", x_options, index=x_options.index(x_default))
        y_col = st.selectbox("Numeric column", numeric_cols)
        color_options = ["None"] + categorical_cols
        color_col = st.selectbox("Color grouping (optional)", color_options)
        color_arg = None if color_col == "None" or color_col == x_col else color_col
        plot_df = filtered.copy()

        try:
            if chart_type == "Bar chart":
                fig = px.bar(plot_df, x=x_col, y=y_col, color=color_arg, title=f"{y_col} by {x_col}", template="plotly_white")
            elif chart_type == "Line chart":
                fig = px.line(plot_df, x=x_col, y=y_col, color=color_arg, markers=True, title=f"{y_col} across {x_col}", template="plotly_white")
            elif chart_type == "Scatter plot":
                scatter_x = x_col if x_col in numeric_cols else y_col
                scatter_y = st.selectbox("Scatter Y axis", numeric_cols, index=min(1, len(numeric_cols)-1))
                fig = px.scatter(plot_df, x=scatter_x, y=scatter_y, color=color_arg, title=f"{scatter_y} vs {scatter_x}", template="plotly_white")
            elif chart_type == "Histogram":
                fig = px.histogram(plot_df, x=y_col, color=color_arg, title=f"Distribution of {y_col}", template="plotly_white")
            elif chart_type == "Box plot":
                fig = px.box(plot_df, x=x_col if x_col in categorical_cols else None, y=y_col, color=color_arg, title=f"Distribution of {y_col}", template="plotly_white")
            else:
                if x_col in categorical_cols:
                    pie_df = plot_df.groupby(x_col, dropna=False)[y_col].sum().reset_index()
                    fig = px.pie(pie_df, names=x_col, values=y_col, title=f"{y_col} share by {x_col}", template="plotly_white")
                else:
                    st.warning("For a pie chart, choose a categorical column for X axis.")
                    fig = None
            if fig is not None:
                fig.update_layout(margin=dict(l=10, r=10, t=55, b=10), legend_title_text="Group")
                st.plotly_chart(fig, use_container_width=True)
        except Exception as exc:
            st.error(f"Could not create this chart from the selected columns: {exc}")

    with st.expander("Dataset information"):
        st.write("**Column data types**")
        st.dataframe(pd.DataFrame({"Column": df.columns, "Data type": [str(t) for t in df.dtypes], "Missing values": [int(df[c].isna().sum()) for c in df.columns]}), use_container_width=True)

elif section == "🖼️ Image Studio":
    st.subheader("Image Studio")
    st.write("Upload an image, preview it, apply a simple filter, and download the result.")
    file = st.file_uploader("Upload image", type=["png", "jpg", "jpeg", "webp"])
    if file:
        try:
            original = Image.open(file).convert("RGB")
            a, b = st.columns(2)
            with a:
                st.markdown("#### Original image")
                st.image(original, use_container_width=True)
                st.caption(f"Size: {original.width} × {original.height}px")
            with st.sidebar:
                st.subheader("Image controls")
                operation = st.selectbox("Effect", ["Original", "Grayscale", "Blur", "Sharpen", "Edge enhance", "Contrast"])
                strength = st.slider("Effect strength", 0.5, 3.0, 1.3, 0.1)
                max_width = st.slider("Resize width", 200, 1600, min(900, max(200, original.width)), 50)
            edited = original.copy()
            if operation == "Grayscale":
                edited = ImageOps.grayscale(edited).convert("RGB")
            elif operation == "Blur":
                edited = edited.filter(ImageFilter.GaussianBlur(radius=strength))
            elif operation == "Sharpen":
                edited = ImageEnhance.Sharpness(edited).enhance(strength)
            elif operation == "Edge enhance":
                edited = edited.filter(ImageFilter.EDGE_ENHANCE)
            elif operation == "Contrast":
                edited = ImageEnhance.Contrast(edited).enhance(strength)
            if edited.width > max_width:
                new_height = int(edited.height * max_width / edited.width)
                edited = edited.resize((max_width, new_height))
            with b:
                st.markdown("#### Edited image")
                st.image(edited, use_container_width=True)
                st.caption(f"Size: {edited.width} × {edited.height}px")
            buffer = io.BytesIO()
            edited.save(buffer, format="PNG")
            st.download_button("⬇️ Download edited image", buffer.getvalue(), "edited_image.png", "image/png")
        except Exception as exc:
            st.error(f"Could not process this image: {exc}")
    else:
        st.info("Upload a JPG or PNG image to try the image editing tools.")

else:
    st.subheader("About the project")
    st.markdown("""
**Project title:** Interactive Multimedia Data Explorer

**Aim:** To build a simple interactive application that helps users explore tabular data and multimedia images.

**Libraries used (from the lab manual):**
- **Streamlit:** dashboard, upload controls, filters and widgets (Experiment 4)
- **Pandas:** tabular data loading and analysis
- **Plotly:** interactive visualizations (Experiment 2)
- **Pillow:** image preview, resizing and filters (Experiment 7)

**Main features**
1. Upload and filter CSV data.
2. View rows, summary statistics and missing values.
3. Create bar, line, scatter, histogram, box and pie charts.
4. Upload, preview, resize, edit and download images.

**Note:** The app uses a built-in sample dataset if no CSV is uploaded. It does not claim to predict or classify data; it is an exploration and visualization tool.
""")

st.markdown("---")
st.caption("Interactive Multimedia Data Explorer · Python mini project")
