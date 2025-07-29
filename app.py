import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from chat_parser import preprocess_chat
from wordcloud import WordCloud
import emoji
from collections import Counter

# Streamlit settings
st.set_page_config(page_title="WhatsApp Chat Analyzer", layout="wide")
st.title("📱 WhatsApp Chat Analyzer")

# File uploader
uploaded_file = st.file_uploader("Upload your WhatsApp chat file (.txt)", type="txt")

if uploaded_file is not None:
    try:
        # Read and process chat
        chat_data = uploaded_file.read().decode("utf-8")
        df = preprocess_chat(chat_data)

        # -------------------- Chat Preview ------------------------
        st.subheader("📄 Chat Preview")
        st.dataframe(df.head(20), use_container_width=True)

        # -------------------- Statistics --------------------------
        st.subheader("📊 Basic Statistics")
        total_messages = df.shape[0]
        total_words = df['message'].apply(lambda x: len(x.split())).sum()
        total_media = df['message'].str.contains('<Media omitted>').sum()
        total_links = df['message'].str.contains(r'http[s]?://', regex=True).sum()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Messages", total_messages)
        col2.metric("Words", total_words)
        col3.metric("Media Shared", total_media)
        col4.metric("Links Shared", total_links)

        # -------------------- Top Users ---------------------------
        st.subheader("👤 Top 10 Active Users")
        top_users = df['user'].value_counts().head(10)
        fig, ax = plt.subplots()
        top_users.plot(kind='barh', ax=ax, color='skyblue')
        ax.set_xlabel("Message Count")
        ax.invert_yaxis()
        st.pyplot(fig)

        # -------------------- Daily Timeline ----------------------
        st.subheader("📅 Daily Chat Timeline")
        timeline = df.groupby('date').size()
        fig, ax = plt.subplots()
        timeline.plot(kind='line', ax=ax, marker='o')
        ax.set_ylabel("Messages")
        ax.set_xlabel("Date")
        st.pyplot(fig)

        # -------------------- Weekday Activity ---------------------
        st.subheader("📆 Activity by Day of Week")
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekday_counts = df['day_name'].value_counts().reindex(day_order)
        fig, ax = plt.subplots()
        weekday_counts.plot(kind='bar', ax=ax, color='lightgreen')
        ax.set_ylabel("Messages")
        st.pyplot(fig)

        # -------------------- Hourly Activity ----------------------
        st.subheader("⏰ Activity by Hour")
        hourly = df['hour'].value_counts().sort_index()
        fig, ax = plt.subplots()
        hourly.plot(kind='line', ax=ax, marker='o', color='orange')
        ax.set_xlabel("Hour of Day")
        ax.set_ylabel("Messages")
        st.pyplot(fig)

        # -------------------- Word Cloud --------------------------
        st.subheader("☁️ Word Cloud (Most Frequent Words)")
        text = " ".join(msg for msg in df['message'] if not msg.startswith('<Media') and 'http' not in msg)
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis("off")
        st.pyplot(fig)

        # -------------------- Emoji Analysis ----------------------
        st.subheader("😊 Emoji Usage")

        def extract_emojis(s):
            return [c for c in s if c in emoji.EMOJI_DATA]

        def get_emoji_name(e):
            try:
                return emoji.EMOJI_DATA[e]['en']
            except:
                return "Unknown"

        all_emojis = []
        for message in df['message']:
            all_emojis += extract_emojis(message)

        total_emojis = len(all_emojis)
        st.markdown(f"**Total Emojis Used:** {total_emojis}")

        if total_emojis > 0:
            emoji_counter = Counter(all_emojis).most_common(10)
            emoji_df = pd.DataFrame(emoji_counter, columns=['Emoji', 'Count'])
            emoji_df['Name'] = emoji_df['Emoji'].apply(get_emoji_name)
            emoji_df = emoji_df[['Emoji', 'Name', 'Count']]

            st.markdown("**Top 10 Most Used Emojis**")
            st.dataframe(emoji_df, use_container_width=True)

            # Plot emoji bar chart
            fig, ax = plt.subplots()
            sns.barplot(x='Count', y='Emoji', data=emoji_df, palette='cool', ax=ax)
            ax.set_xlabel("Usage Count")
            ax.set_ylabel("Emoji")
            st.pyplot(fig)
        else:
            st.info("No emojis found in this chat.")

    except Exception as e:
        st.error(f"⚠️ Error: {e}")