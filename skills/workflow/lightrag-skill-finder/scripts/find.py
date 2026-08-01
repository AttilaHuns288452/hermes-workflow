#!/usr/bin/env python
"""Query the TF-IDF skill index — sub-second, zero API calls."""
import sys, json, re
from collections import defaultdict
from math import log
from pathlib import Path

INDEX_FILE = Path(__file__).parent.parent.parent.parent / "lightrag_index" / "skill_index.json"
# ponytail: resolve relative to skills dir
INDEX_FILE = Path.home() / "AppData" / "Local" / "hermes" / "lightrag_index" / "skill_index.json"

def tokenize(text):
    return re.findall(r'[a-z0-9-]+', text.lower())

def find(query, top_k=10):
    if not INDEX_FILE.exists():
        print(f"ERROR: No index at {INDEX_FILE}. Run build_index.py first.")
        sys.exit(1)
    
    with open(INDEX_FILE) as f:
        idx = json.load(f)
    
    docs, df, N = idx["docs"], idx["df"], idx["N"]
    idf = {t: log(N / df[t]) for t in df}
    
    q_tokens = tokenize(query)
    q_tf = defaultdict(int)
    for t in q_tokens:
        q_tf[t] += 1
    
    scores = {}
    for name, tf in docs.items():
        score = 0
        v_len = sum(tf.values()) or 1
        for t in set(q_tokens):
            if t in idf:
                score += (q_tf[t] / len(q_tokens)) * (tf.get(t, 0) / v_len) * idf[t]
        scores[name] = score
    
    return sorted(scores.items(), key=lambda x: -x[1])[:top_k]

if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else sys.stdin.read().strip()
    if not query:
        print("Usage: python find.py 'some query about what skills you need'")
        sys.exit(1)
    
    results = find(query, top_k=10)
    for name, score in results:
        if score > 0:
            print(f"{score:.4f}\t{name}")
