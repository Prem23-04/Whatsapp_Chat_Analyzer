import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.terminal.shortcuts.auto_suggest import resume_hinting

from chat_parser import preprocess_chat
from wordcloud import WordCloud
import emoji
from collections import Counter
from admin_panel import admin_panel  # Import the admin panel

st.set_page_config(page_title="WhatsApp Chat Analyzer", layout="wide")

# ================== WhatsApp Chat Analyzer ==================
def whatsapp_chat_analyzer():
    if not st.session_state.get("admin_logged_in", False):
        st.warning("⚠ You must log in as admin to access the Chat Analyzer.")
        return

    st.title("📱 WhatsApp Chat Analyzer")

    uploaded_file = st.file_uploader("Upload your WhatsApp chat file (.txt)", type="txt")

    if uploaded_file is not None:
        try:
            # Read and preprocess chat
            chat_data = uploaded_file.read().decode("utf-8")
            df = preprocess_chat(chat_data)

            # ================== Chat Preview ==================
            st.subheader("📄 Chat Preview")
            st.dataframe(df.head(20), use_container_width=True)

            # ================== Basic Statistics ==================
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

            # ================== Top Users ==================
            st.subheader("👤 Top Active Users")
            top_users = df['user'].value_counts().head(10)
            fig, ax = plt.subplots()
            top_users.plot(kind='barh', ax=ax, color='skyblue')
            ax.set_xlabel("Message Count")
            ax.invert_yaxis()
            st.pyplot(fig)

            # ================== Word Cloud ==================
            st.subheader("☁️ Word Cloud")
            text = " ".join(
                msg for msg in df['message']
                if not msg.startswith('<Media') and 'http' not in msg
            )
            wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis("off")
            st.pyplot(fig)

            st.subheader("📊 Messages Distribution by User")

            user_counts = df['user'].value_counts()

            fig, ax = plt.subplots()
            ax.pie(
                user_counts,
                labels=user_counts.index,
                autopct='%1.1f%%',
                startangle=90,
                colors=plt.cm.tab20.colors  # Color palette
            )
            ax.axis('equal')  # Equal aspect ratio makes the pie chart circular
            st.pyplot(fig)

            # ================== Emoji Analysis ==================
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

                # Emoji bar chart
                fig, ax = plt.subplots()
                sns.barplot(x='Count', y='Emoji', data=emoji_df, palette='cool', ax=ax)
                ax.set_xlabel("Usage Count")
                ax.set_ylabel("Emoji")
                st.pyplot(fig)
            else:
                st.info("No emojis found in this chat.")

        except Exception as e:
            st.error(f"⚠️ Error: {e}")

# ================== Main Navigation ==================
def main():
    if "page" not in st.session_state:
        st.session_state.page = "Chat Analyzer"

    menu = ["Chat Analyzer", "Admin Panel"]
    choice = st.sidebar.selectbox("📌 Navigation", menu, index=menu.index(st.session_state.page))

    if choice != st.session_state.page:
        st.session_state.page = choice

    if st.session_state.page == "Chat Analyzer":
        whatsapp_chat_analyzer()
    elif st.session_state.page == "Admin Panel":
        admin_panel()

if __name__ == "__main__":
    main()
