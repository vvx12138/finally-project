import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# -------------------- Load Data --------------------
df = pd.read_csv("Spotify_Youtube.csv")
st.set_page_config(layout="wide")
sns.set_theme()
st.title("Spotify × YouTube Music Analysis Dashboard (2023)")

# -------------------- Fixed Data Overview --------------------
st.dataframe(df)

# -------------------- Sidebar --------------------
analysis_mode = st.sidebar.radio(
    "Select Analysis Section:",
    ["YouTube Overview", "Spotify Overview", "Cross-Platform Analysis"]
)

# Universal Spotify feature selector
spotify_features = ['Energy', 'Danceability', 'Acousticness', 'Valence', 'Loudness']
selected_feature = st.sidebar.selectbox(
    "Select Spotify Feature for Top vs Bottom Analysis:",
    spotify_features
)

# -------------------- Filter for YouTube --------------------
if analysis_mode == "YouTube Overview":
    st.sidebar.header("Filters")
    view_min = int(df['Views'].min())
    view_max = int(df['Views'].max())
    view_filter = st.sidebar.slider(
        "Filter by YouTube Views:",
        view_min, view_max, (view_min, view_max)
    )
    video_type = st.sidebar.selectbox(
        "Video Type:",
        ["All", "Official Only", "Unofficial Only"]
    )

    filtered_df = df[
        (df['Views'] >= view_filter[0]) & (df['Views'] <= view_filter[1])
    ].copy()

    if video_type == "Official Only":
        filtered_df = filtered_df[filtered_df['official_video'] == True]
    elif video_type == "Unofficial Only":
        filtered_df = filtered_df[filtered_df['official_video'] == False]
else:
    filtered_df = df.copy()

#  YOUTUBE OVERVIEW
if analysis_mode == "YouTube Overview":
    st.header("YouTube Overview")

    # --- 1. Top 10 Channels by Views ---
    st.subheader("Top 10 Channels by Total Views")
    top_channels = filtered_df.groupby('Channel')['Views'].sum().sort_values(ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(x=top_channels.values, y=top_channels.index, palette="viridis", ax=ax)
    ax.set_xlabel("Total Views")
    ax.set_ylabel("Channel")
    ax.set_title("Top 10 Channels by Views")
    st.pyplot(fig)
    

    # --- 2. Official vs Unofficial Comparison ---
    st.subheader("Official vs Unofficial: Average Views, Likes, and Comments")
    avg_metrics = filtered_df.groupby('official_video')[['Views', 'Likes', 'Comments']].mean().reset_index()
    avg_metrics['official_video'] = avg_metrics['official_video'].map({True: 'Official', False: 'Unofficial'})
    fig, ax = plt.subplots(figsize=(7, 4))
    avg_metrics.plot(x='official_video', kind='bar', ax=ax, rot=0, color=['skyblue', 'lightcoral', 'lightgreen'])
    ax.set_ylabel("Average Count")
    ax.set_title("Average Engagement by Video Type")
    st.pyplot(fig)
    st.markdown("**Observation:** Officially released videos tend to achieve higher views and likes, showing the importance of official branding and channel authority.")

    # --- 3. Top vs Bottom Performing Songs (Feature-selectable) ---
    st.subheader("Top vs Bottom Performing Songs (YouTube Views)")
    top_threshold = df['Views'].quantile(0.9)
    bottom_threshold = df['Views'].quantile(0.1)
    df['YT_Performance'] = df['Views'].apply(
        lambda x: 'Top 10%' if x >= top_threshold else ('Bottom 10%' if x <= bottom_threshold else 'Mid')
    )
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.boxplot(
        data=df[df['YT_Performance'].isin(['Top 10%', 'Bottom 10%'])],
        x='YT_Performance', y=selected_feature,
        palette='pastel', ax=ax
    )
    ax.set_title(f"{selected_feature} Distribution: Top vs Bottom YouTube Songs")
    st.pyplot(fig)
    st.markdown(f"**Observation:** Top-viewed songs show distinct patterns in *{selected_feature}*, suggesting it contributes to audience engagement on YouTube.")


    # --- 4. Audience Engagement Rate by Channel ---
    st.subheader("Audience Engagement Rate by Channel")
    df['Engagement_Rate'] = (df['Likes'] + df['Comments']) / df['Views']
    engagement = df.groupby('Channel')['Engagement_Rate'].mean().sort_values(ascending=False).head(10)

    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(x=engagement.values, y=engagement.index, palette="coolwarm", ax=ax)
    ax.set_xlabel("Average Engagement Rate (Likes + Comments per View)")
    ax.set_ylabel("Channel")
    ax.set_title("Top 10 Channels by Engagement Rate")
    st.pyplot(fig)
    st.markdown(
        "**Observation:** Channels with high engagement rates tend to maintain strong audience loyalty, "
        "even when their total view counts are lower, showing that smaller fan communities can have strong influence potential."
    )

    # --- 5. Engagement Rate vs Spotify Features ---
    st.subheader("Engagement Rate vs Spotify Features")

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.scatterplot(data=df, x=selected_feature, y='Engagement_Rate', alpha=0.6, color='teal')
    sns.regplot(data=df, x=selected_feature, y='Engagement_Rate', scatter=False, color='red', ax=ax)
    ax.set_title(f"Engagement Rate vs {selected_feature}")
    ax.set_xlabel(selected_feature)
    ax.set_ylabel("Engagement Rate (Likes + Comments per View)")
    st.pyplot(fig)
    st.markdown(
        f"**Observation:** Songs with higher *{selected_feature}* tend to show distinctive engagement patterns, "
        "suggesting that musical characteristics influence how audiences interact beyond just viewing."
    )



#SPOTIFY OVERVIEW
elif analysis_mode == "Spotify Overview":
    st.header("Spotify Overview")

    # --- 1. Feature Distributions ---
    st.subheader("Distribution of Spotify Audio Features")
    features = ['Energy', 'Danceability', 'Acousticness', 'Valence', 'Loudness']
    fig, axes = plt.subplots(1, len(features), figsize=(18, 4))
    for i, feature in enumerate(features):
        sns.histplot(df[feature], bins=20, ax=axes[i], color='skyblue')
        axes[i].set_title(feature)
    st.pyplot(fig)
    st.markdown("**Observation:** Most tracks show medium to high energy and danceability, aligning with mainstream music production trends.")

    # --- 2. Top vs Bottom Performing Songs (Spotify Streams) ---
    if 'Stream' in df.columns:
        st.subheader("Top vs Bottom Performing Songs (Spotify Streams)")
        top_s = df['Stream'].quantile(0.9)
        bottom_s = df['Stream'].quantile(0.1)
        df['SP_Performance'] = df['Stream'].apply(
            lambda x: 'Top 10%' if x >= top_s else ('Bottom 10%' if x <= bottom_s else 'Mid')
        )

        fig, ax = plt.subplots(figsize=(8, 5))
        sns.boxplot(
            data=df[df['SP_Performance'].isin(['Top 10%', 'Bottom 10%'])],
            x='SP_Performance', y=selected_feature,
            palette='muted', ax=ax
        )
        ax.set_title(f"{selected_feature} Distribution: Top vs Bottom Spotify Songs")
        st.pyplot(fig)
        st.markdown(f"**Observation:** Top-streamed songs on Spotify show unique *{selected_feature}* profiles, reflecting listener preferences.")
    else:
        st.warning(" 'Stream' column not found; Spotify performance analysis skipped.")


# CROSS-PLATFORM ANALYSIS

elif analysis_mode == "Cross-Platform Analysis":
    st.header("Cross-Platform Analysis: Spotify vs YouTube")


    # --- 1. Streams vs Views ---
    st.subheader("Spotify Streams vs YouTube Views")
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.scatterplot(data=df, x='Stream', y='Views', alpha=0.6)
    sns.regplot(data=df, x='Stream', y='Views', scatter=False, color='red', ax=ax)
    ax.set_title("Relationship between Spotify Streams and YouTube Views")
    ax.set_xlabel("Spotify Streams")
    ax.set_ylabel("YouTube Views")
    st.pyplot(fig)
    st.markdown("**Observation:** Songs with high Spotify streams generally achieve higher YouTube views, suggesting cross-platform popularity alignment.")


    # --- 2. Feature Influence Comparison ---
    st.subheader("Feature Influence Comparison: Streams vs Views")

    features = ['Energy', 'Danceability', 'Acousticness', 'Valence', 'Loudness']
    feature_corr = []

    for feature in features:
        corr_stream = df[feature].corr(df['Stream'])
        corr_views = df[feature].corr(df['Views'])
        feature_corr.append([feature, corr_stream, corr_views])

    feature_df = pd.DataFrame(feature_corr, columns=['Feature', 'Spotify_Streams', 'YouTube_Views'])

    fig, ax = plt.subplots(figsize=(8, 5))
    feature_df_melted = feature_df.melt(id_vars='Feature', var_name='Platform', value_name='Correlation')
    sns.barplot(data=feature_df_melted, x='Feature', y='Correlation', hue='Platform', palette='Set2', ax=ax)
    ax.set_title("Feature Correlation Comparison: Spotify vs YouTube")
    ax.set_ylabel("Correlation Coefficient")
    ax.set_xlabel("Spotify Feature")
    st.pyplot(fig)

    st.markdown("""
    **Observation:**  
    Energy and Danceability consistently show the strongest positive relationship with both Spotify streams and YouTube views.  
    However, Acousticness tends to correlate negatively, suggesting that lively, electronic-driven songs perform better across platforms.  
    """)


    # --- 3. Cross-Platform Divergence (Top vs Bottom Differences) ---
    st.subheader("Cross-Platform Divergence: Which Songs Perform Differently?")
    df['Stream_Rank'] = df['Stream'].rank(pct=True)
    df['View_Rank'] = df['Views'].rank(pct=True)
    df['Performance_Gap'] = abs(df['Stream_Rank'] - df['View_Rank'])
    top_gap = df.nlargest(10, 'Performance_Gap')[['Artist', 'Track', 'Stream_Rank', 'View_Rank', 'Performance_Gap']]

    st.dataframe(top_gap.style.highlight_max(subset=['Performance_Gap'], color='lightcoral'))
    st.markdown("**Observation:** Some songs perform far better on one platform than the other, showing differing audience behaviors between streaming and video consumption.")
    

