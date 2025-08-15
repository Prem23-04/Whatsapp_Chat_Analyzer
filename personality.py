from collections import Counter
import nltk
from nltk.corpus import stopwords
import string

nltk.download('punkt')
nltk.download('stopwords')

def profile_personality(df):
    text = ' '.join(df['message'].tolist())
    tokens = nltk.word_tokenize(text.lower())
    words = [w for w in tokens if w.isalpha() and w not in stopwords.words('english')]

    word_counts = Counter(words)
    total_words = len(words)

    personality_traits = {
        "Extraversion": word_counts['party'] + word_counts['fun'] + word_counts['friends'],
        "Agreeableness": word_counts['thanks'] + word_counts['sorry'] + word_counts['please'],
        "Conscientiousness": word_counts['work'] + word_counts['time'] + word_counts['plan'],
        "Neuroticism": word_counts['angry'] + word_counts['worried'] + word_counts['hate'],
        "Openness": word_counts['idea'] + word_counts['think'] + word_counts['dream']
    }

    profile = {trait: round(count / total_words, 4) for trait, count in personality_traits.items()}
    return profile
