import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme()

# ---- App Title ----
st.title('YouTube Top 100 Songs (2025) Data Analysis')

# ---- Load Dataset ----
df = pd.read_csv('youtube-top-100-songs-2025.csv')

# ---- Sidebar Filters ----
st.sidebar.header("Filters")

# Filter 1: View count range观看区间选定
min_views = int(df['view_count'].min())
max_views = int(df['view_count'].max())
view_filter = st.sidebar.slider('Select view count range:',
                                min_views, max_views, (min_views, max_views))
#Filter 2:类型
categories = df['categories'].dropna().unique().tolist()
selected_categories = st.sidebar.multiselect('Select categories:', categories, categories)
#Filter 3:频道大小
channel_size = st.sidebar.selectbox(
    'Select channel size (by the amount of fans)：',
    ['All', 'Small (<1M)', 'Medium (1M-10M)', 'Large (>10M)'],
    index=0
)
# Apply filters这个就是筛选条件的集合，总共一个是肯定的，还有一个备选
filtered_df = df[
    (df['view_count'] >= view_filter[0]) &
    (df['view_count'] <= view_filter[1])&(df['categories'].isin(selected_categories)) ].copy()
#进一步过滤
if 'Small (<1M)' not in channel_size:
    filtered_df = filtered_df[filtered_df['channel_follower_count'] >= 1_000_000]
if 'Medium (1M-10M)' not in channel_size:
    filtered_df = filtered_df[
        (filtered_df['channel_follower_count'] < 1_000_000) |
        (filtered_df['channel_follower_count'] >= 10_000_000)
    ]
if 'Large (>10M)' not in channel_size:
    filtered_df = filtered_df[filtered_df['channel_follower_count'] < 10_000_000]

#整体预览
st.write("### Data Preview")
st.write(filtered_df)    
st.subheader("Filtered Data Sample")
st.write(filtered_df.head())

st.markdown(f"**Total filtered songs:** {len(filtered_df)}")

# Question 1: Which artist is mentioned the most times?
st.write("### singers mentioned most")
artist_counts = filtered_df['channel'].value_counts()
st.bar_chart(artist_counts)
# ---- Additional Chart: 视频长度分布 ----要的
st.subheader("Video Duration Distribution (Histogram)")
fig3, ax3 = plt.subplots(figsize=(8, 5))
ax3.hist(filtered_df['duration'], bins=20, color='skyblue', edgecolor='black')
ax3.set_xlabel('Video Duration (seconds)')
ax3.set_ylabel('Frequency')
ax3.set_title('Distribution of Video Durations')
st.pyplot(fig3)


# Question: Average view count by category over time
st.write("### The trend of average views for different categories of videos over time")

filtered_df['uration_string'] = pd.to_datetime(filtered_df['duration_string'])

trend_data = filtered_df.groupby(['categories', 'uration_string'])['view_count'].mean().reset_index()

fig, ax = plt.subplots(figsize=(10, 6))
for category in trend_data['categories'].unique():
    category_data = trend_data[trend_data['categories'] == category]
    sns.lineplot(x='uration_string', y='view_count', data=category_data, label=category, ax=ax)

ax.set_title("The trend of average views for different categories of videos over time", fontsize=16)
ax.set_xlabel("Upload date", fontsize=14)
ax.set_ylabel("Average View Counts", fontsize=14)
ax.legend(title="categories")
ax.grid(True)
st.pyplot(fig)
# ---------------- 问题：不同频道规模的平均观看量 ---------------- #
st.write("### Question: Average view count by different channel sizes")

# 定义规模分类函数
def get_scale(followers):
    if followers < 1_000_000:
        return 'Small (<1M)'
    elif followers < 10_000_000:
        return 'Medium (1M–10M)'
    else:
        return 'Large (>10M)'

# 新增一列 scale
filtered_df['scale'] = filtered_df['channel_follower_count'].apply(get_scale)

# 按频道规模过滤（基于 selectbox 选择）
if channel_size != 'All':
    filtered_df = filtered_df[filtered_df['scale'] == channel_size]

# 绘制散点图
fig5, ax5 = plt.subplots(figsize=(8, 5))
sns.scatterplot(data=filtered_df, x='duration', y='view_count', color='royalblue', alpha=0.6)
ax5.set_xlabel('Video Duration (seconds)')
ax5.set_ylabel('View Count')
ax5.set_title(f'Video Duration vs View Count for {channel_size} Channels')
st.pyplot(fig5)

# 简短结论
st.write(f"结论：在 {channel_size} 频道中，视频时长与观看量的关系较弱，说明内容质量可能比时长更重要。")