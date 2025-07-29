import re
import pandas as pd

def preprocess_chat(chat_data):
    # Pattern to match WhatsApp date-time format (adjust if format is different)
    # Supports formats like: 12/07/2023, 9:12 pm - User: Message
    pattern = r'(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2})\s?(AM|PM|am|pm)?\s?-\s(.*?):\s(.*)'

    messages = []
    for line in chat_data.split('\n'):
        match = re.match(pattern, line)
        if match:
            date = match.group(1)
            time = match.group(2)
            meridian = match.group(3) or ''
            user = match.group(4)
            message = match.group(5)
            full_datetime = f"{date} {time} {meridian}".strip()
            messages.append([full_datetime, user, message])
        else:
            # Append continuation of previous message
            if messages:
                messages[-1][2] += ' ' + line.strip()

    # Create DataFrame
    df = pd.DataFrame(messages, columns=['datetime', 'user', 'message'])

    # Convert to datetime object safely
    df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')

    # Drop rows where datetime conversion failed
    df = df.dropna(subset=['datetime'])

    # Extract date and time separately
    df['date'] = df['datetime'].dt.date
    df['time'] = df['datetime'].dt.time
    df['hour'] = df['datetime'].dt.hour
    df['minute'] = df['datetime'].dt.minute
    df['day_name'] = df['datetime'].dt.day_name()

    return df
