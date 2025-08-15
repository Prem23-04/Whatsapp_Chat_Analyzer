import pandas as pd
import re
from datetime import datetime

def preprocess_chat(chat_text):
    # Patterns for different WhatsApp formats
    patterns = [
        r"^(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2})\s?(AM|PM|am|pm)?\s-\s(.+?):\s(.*)",  # Android 12hr
        r"^(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2})\s-\s(.+?):\s(.*)",                   # Android 24hr
        r"^\[(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2}:\d{2}\s?(AM|PM|am|pm)?)\]\s(.+?):\s(.*)"  # iPhone
    ]

    data = []

    for line in chat_text.split("\n"):
        line = line.strip()
        if not line:
            continue

        matched = False
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                matched = True
                groups = match.groups()

                # Determine fields
                if len(groups) >= 5:
                    date_str = groups[0]
                    time_str = groups[1]
                    ampm = groups[2] if len(groups) > 5 else ""
                    sender = groups[3 if ampm else 2]
                    message = groups[4 if ampm else 3]
                else:
                    continue

                # Try multiple datetime formats
                dt_formats = [
                    "%d/%m/%y %I:%M %p", "%d/%m/%Y %I:%M %p",
                    "%m/%d/%y %I:%M %p", "%m/%d/%Y %I:%M %p",
                    "%d/%m/%y %H:%M", "%d/%m/%Y %H:%M",
                    "%m/%d/%y %H:%M", "%m/%d/%Y %H:%M"
                ]
                parsed_dt = None
                for fmt in dt_formats:
                    try:
                        parsed_dt = datetime.strptime(f"{date_str} {time_str} {ampm}".strip(), fmt)
                        break
                    except:
                        continue

                if parsed_dt:
                    data.append([parsed_dt.date(), parsed_dt.strftime("%A"), parsed_dt.hour, sender, message])
                break

        # If no match, append as continuation of last message
        if not matched and data:
            data[-1][4] += " " + line

    df = pd.DataFrame(data, columns=["date", "day_name", "hour", "user", "message"])
    return df
