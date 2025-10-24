import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
st.set_page_config(layout="wide")

sns.set_theme()
st.title('YouTube Top 100 Songs (2025) Data Analysis')

df = pd.read_csv('youtube-top-100-songs-2025.csv')

# ------------------ Sidebar Filters ------------------
st.sidebar.header("Filters")

# view_count
min_views = int(df['view_count'].min())
max_views = int(df['view_count'].max())
view_filter = st.sidebar.slider('Select view count range:',
                                min_views, max_views, (min_views, max_views))

# categories
categories = df['categories'].dropna().unique().tolist()
selected_categories = st.sidebar.multiselect('Select categories:', categories, categories)

# channel
channel_size = st.sidebar.multiselect(
    'Select channel size (by the amount of fans)：',
    ['Small (<1M)', 'Medium (1M-10M)', 'Large (>10M)'],
    default=['Small (<1M)', 'Medium (1M-10M)', 'Large (>10M)']
)


# ------------------ Additional Interaction: Relationship Explorer ------------------
st.sidebar.markdown("---")
st.sidebar.header("Explore Relationships")

analysis_option = st.sidebar.radio(
    "Select a relationship to explore:",
    ["View Count vs Duration",
     "View Count by Channel Size",
     "View Count by Category"]
)



# ------------------ filter the data ------------------
filtered_df = df.copy()

# filter view-count
filtered_df = filtered_df[
    (filtered_df['view_count'] >= view_filter[0]) &
    (filtered_df['view_count'] <= view_filter[1])
]

# filter_categories
filtered_df = filtered_df[filtered_df['categories'].isin(selected_categories)]

# def scale
def get_scale(fans):
    if fans < 1_000_000:
        return 'Small (<1M)'
    elif fans < 10_000_000:
        return 'Medium (1M-10M)'
    else:
        return 'Large (>10M)'

df['scale'] = df['channel_follower_count'].apply(get_scale)
filtered_df['scale'] = filtered_df['channel_follower_count'].apply(get_scale)

# channal filter
if channel_size:  
    filtered_df = filtered_df[filtered_df['scale'].isin(channel_size)]

# ------------------page :left+right------------------
left_col, right_col = st.columns([2, 1])

# ------------------ left ------------------
with left_col:
    st.subheader("Filtered Data Preview")
    st.write(filtered_df.head())
    st.markdown(f"**Total filtered songs:** {len(filtered_df)}")

    # 1. most mentioned singers
    st.subheader("Most Mentioned Singers (Filtered)")
    artist_counts = filtered_df['channel'].value_counts()
    st.bar_chart(artist_counts)

    # 2. The trend of average views for different categories of videos over duration length
    st.subheader("The Trend of Average Views for Different Categories Over Duration")
    trend_data = filtered_df.groupby(['categories', 'duration'])['view_count'].mean().reset_index()
    fig, ax = plt.subplots(figsize=(10, 6))
    for category in trend_data['categories'].unique():
        category_data = trend_data[trend_data['categories'] == category]
        sns.lineplot(x='duration', y='view_count', data=category_data, label=category, ax=ax)
    ax.set_title("Trend of Average Views for Different Categories Over Duration Length")
    ax.set_xlabel("Video Duration (seconds)")
    ax.set_ylabel("Average View Count")
    ax.legend(title="Category", bbox_to_anchor=(1.05, 1), loc='upper left')
    st.pyplot(fig)
    st.markdown("**Conclusion:** Different music categories show distinct viewing patterns depending on video length.")
    
    # 3.Relationship Explorer (based on sidebar selection) 
    st.subheader("Interactive Relationship Explorer")

    if analysis_option == "View Count vs Duration":
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.scatterplot(data=filtered_df, x='duration', y='view_count', color='royalblue', alpha=0.6)
        ax.set_xlabel('Video Duration (seconds)')
        ax.set_ylabel('View Count')
        ax.set_title('View Count vs Duration')
        st.pyplot(fig)
        st.markdown("**Conclusion:** The relationship between duration and views is weak, suggesting that shorter or longer videos do not guarantee higher popularity.")

    elif analysis_option == "View Count by Channel Size":
        avg_view_by_scale = filtered_df.groupby('scale')['view_count'].mean().reset_index()
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(x='scale', y='view_count', data=avg_view_by_scale, ax=ax, palette='coolwarm')
        ax.set_xlabel('Channel Size')
        ax.set_ylabel('Average View Count')
        ax.set_title('Average View Count by Channel Size')
        st.pyplot(fig)
        st.markdown("**Conclusion:** Larger channels tend to attract more views on average due to stronger fan engagement.")

    elif analysis_option == "View Count by Category":
        top_cats = filtered_df['categories'].value_counts().head(6).index.tolist()
        box_df = filtered_df[filtered_df['categories'].isin(top_cats)]
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.boxplot(x='categories', y='view_count', data=box_df, palette='pastel')
        ax.set_xlabel('Category')
        ax.set_ylabel('View Count')
        ax.set_title('View Count Distribution by Category')
        plt.xticks(rotation=25)
        st.pyplot(fig)
        st.markdown("**Conclusion:** Categories with higher median views represent stable audience appeal and consistent engagement.")

# ------------------ right:overall data------------------
with right_col:
    st.subheader("Overall Dataset Overview (Unfiltered)")
    st.write(df)

    # data 
    total_songs = len(df)
    avg_views_all = df['view_count'].mean()
    median_views_all = df['view_count'].median()
    avg_duration_all = df['duration'].mean()
    median_duration_all = df['duration'].median()

    st.markdown("### Overall Statistics")
    st.write(f"- **Total songs in dataset:** {total_songs}")
    st.write(f"- **Average view count:** {avg_views_all:,.0f}")
    st.write(f"- **Median view count:** {median_views_all:,.0f}")
    st.write(f"- **Average duration:** {avg_duration_all:.1f} sec")
    st.write(f"- **Median duration:** {median_duration_all:.1f} sec")

    # Top 5 channels（全量）
    st.markdown("### Top 5 Channels (Overall)")
    st.write(df['channel'].value_counts().head(5))

    # category
    st.markdown("### Category Distribution (Overall)")
    fig5, ax5 = plt.subplots(figsize=(5, 3))
    df['categories'].value_counts().plot(kind='bar', color='lightcoral', ax=ax5)
    ax5.set_title('Category Count (Overall)')
    ax5.set_xlabel('Category')
    ax5.set_ylabel('Count')
    st.pyplot(fig5)





