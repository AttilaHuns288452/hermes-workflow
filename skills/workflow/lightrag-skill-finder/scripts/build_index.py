#!/usr/bin/env python
"""Build TF-IDF skill index — run once, or when skills change."""
import os, glob, json, re
from collections import defaultdict
from math import log

SKILL_SRC = os.path.expandvars(r"${APPDATA}\hermes\skills").replace("${APPDATA}", os.environ.get("APPDATA", ""))
if not SKILL_SRC or not os.path.isdir(SKILL_SRC):
    SKILL_SRC = os.path.expanduser("~/AppData/Local/hermes/skills")
INDEX_FILE = os.path.join(os.path.dirname(SKILL_SRC), "lightrag_index", "skill_index.json")

def tokenize(text):
    return re.findall(r'[a-z0-9-]+', text.lower())

def build():
    skills = {}
    for path in glob.glob(f"{SKILL_SRC}/**/SKILL.md", recursive=True):
        name = path.replace(SKILL_SRC + "\\", "").replace("\\SKILL.md", "")
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        skills[name] = content[:4000]
    
    docs, df = {}, defaultdict(int)
    for name, content in skills.items():
        tokens = tokenize(content)
        tf = defaultdict(int)
        for t in tokens:
            tf[t] += 1
        docs[name] = dict(tf)
        for t in set(tokens):
            df[t] += 1
    
    N = len(docs)
    index = {"docs": docs, "df": dict(df), "N": N, "skills": {n: s[:500] for n,s in skills.items()}}
    os.makedirs(os.path.dirname(INDEX_FILE), exist_ok=True)
    with open(INDEX_FILE, "w") as f:
        json.dump(index, f)
    print(f"Indexed {N} skills → {INDEX_FILE} ({os.path.getsize(INDEX_FILE)} bytes)")

if __name__ == "__main__":
    build()
