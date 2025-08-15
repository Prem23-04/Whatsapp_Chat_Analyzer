import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from textblob import TextBlob
from transformers import pipeline

classifier = pipeline("text-classification", model="unitary/toxic-bert", top_k=None)

def get_stats(df):
    stats = {
        "Total Messages": len(df),
        "Total Words": df['message'].apply(lambda x: len(x.split())).sum(),
        "Media Shared": df[df['message'].str.contains("<Media omitted>", na=False)].shape[0],
        "Links Shared": df[df['message'].str.contains("http", na=False)].shape[0],
        "Participants": df['sender'].nunique()
    }
    return pd.DataFrame(stats.items(), columns=["Metric", "Value"])

def sentiment_analysis(df):
    df['polarity'] = df['message'].apply(lambda x: TextBlob(x).sentiment.polarity)
    df['subjectivity'] = df['message'].apply(lambda x: TextBlob(x).sentiment.subjectivity)
    return df[['sender', 'message', 'polarity', 'subjectivity']]

def plot_activity(df, mode='daily'):
    if mode == 'daily':
        daily = df['date'].value_counts().sort_index()
        fig, ax = plt.subplots()
        daily.plot(kind='line', ax=ax)
        ax.set_title("Daily Messages")
        ax.set_ylabel("Count")
        return fig
    elif mode == 'heatmap':
        heatmap_data = df.groupby(['weekday', 'hour']).size().unstack(fill_value=0)
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        heatmap_data = heatmap_data.reindex(days_order)
        fig, ax = plt.subplots(figsize=(12,6))
        sns.heatmap(heatmap_data, cmap='YlGnBu', ax=ax)
        ax.set_title("Message Activity Heatmap")
        return fig

def detect_toxicity(df):
    df['Toxicity'] = df['message'].apply(
        lambda x: any("toxic" in label['label'] and label['score'] > 0.5 for label in classifier(x) if 'toxic' in label['label'])
    )
    return df[['sender', 'message', 'Toxicity']]
