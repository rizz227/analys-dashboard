from textblob import TextBlob
import pandas as pd

def analyze_sentiments(comments):
    rows = []
    for c in comments:
        text = c["text"]
        date = c["date"]
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        if polarity > 0:
            sentiment = "Positif"
        elif polarity < 0:
            sentiment = "Négatif"
        else:
            sentiment = "Neutre"
        rows.append({
            "date": date,
            "commentaire": text,
            "score": round(polarity, 2),
            "sentiment": sentiment
        })
    return pd.DataFrame(rows)
