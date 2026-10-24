import json
import random
import string
from pathlib import Path

import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

# Download NLTK resources (once)
nltk.download("punkt", quiet=True)
nltk.download("stopwords", quiet=True)
nltk.download("punkt_tab", quiet=True)

stemmer = PorterStemmer()
stop_words = set(stopwords.words("english"))

INTENTS_PATH = Path(__file__).parent / "data" / "intents.json"
FALLBACK = "Sorry, I didn't understand that. Can you please rephrase?"
THRESHOLD = 0.3  # minimum match score to accept an intent


def load_intents(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)["intents"]


def preprocess(text):
    """Normalize text and reduce related words to a shared root.

    Stemming removes word endings, so words such as ``running`` and ``runs``
    can be matched as the same concept (for example, ``run``).
    """
    tokens = word_tokenize(text.lower())
    return {
        stemmer.stem(t)
        for t in tokens
        if t not in stop_words and t not in string.punctuation
    }


def build_keywords(intents):
    """Turn each intents pattern into a set of keywords for matching."""
    return {
        intent["tag"]: set().union(*(preprocess(p) for p in intent["patterns"]))
        for intent in intents
    }


def detect_intent(text, keywords):
    """Return the tag whose keywords bets match the text or None."""
    words = preprocess(text)
    if not words:
        return None
    best_tag, best_score = None, 0
    for tag, intent_words in keywords.items():
        score = len(words & intent_words) / len(words)  # Calculate the similarity score
        if score > best_score:
            best_tag, best_score = tag, score
    return best_tag if best_score >= THRESHOLD else None


def main():
    intents = load_intents(INTENTS_PATH)
    keywords = build_keywords(intents)
    responses = {intent["tag"]: intent["responses"] for intent in intents}

    print("HPC Assistant is ready! Type 'quit' to exit.")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("quit", "exit"):
            print("Bot: Goodbye!")
            break
        tag = detect_intent(user_input, keywords)
        print("Bot:", random.choice(responses[tag]) if tag else FALLBACK)


if __name__ == "__main__":
    main()
