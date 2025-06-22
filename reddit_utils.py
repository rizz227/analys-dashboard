import praw
from datetime import datetime

# Remplace ces valeurs avec tes vraies clés API
reddit = praw.Reddit(
    client_id="426bfOUV_-tembatnyhESA",
    client_secret="6V5MQfJN3OheGCLMC6fEyxrsMu7jlw",
    user_agent="tennis-sentiment-analysis"
)

def get_reddit_comments(query, limit=50, year=None):
    results = []
    subreddit = reddit.subreddit("tennis")

    for submission in subreddit.search(query, sort="new", limit=limit*2):
        if year:
            try:
                post_year = datetime.utcfromtimestamp(submission.created_utc).year
                if post_year != year:
                    continue
            except:
                continue

        submission.comments.replace_more(limit=0)
        for comment in submission.comments[:10]:
            results.append({
                "text": comment.body,
                "date": datetime.utcfromtimestamp(comment.created_utc).date()
            })
            if len(results) >= limit:
                return results
    return results