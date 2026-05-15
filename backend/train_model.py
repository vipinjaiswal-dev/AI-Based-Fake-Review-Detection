# ================= train_model.py =================

import pandas as pd
import pickle

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

from xgboost import XGBClassifier

# ================= LOAD DATASET =================
df = pd.read_csv("backend/dataset/fake_review.csv")

# ================= CLEAN DATA =================
df["Product"] = df["Product"].astype(str).str.lower()
df["Category"] = df["Category"].astype(str).str.lower()
df["Review"] = df["Review"].astype(str).str.lower()

# ================= COMBINE CONTEXT =================
df["text"] = (
    df["Product"] + " " +
    df["Category"] + " " +
    df["Review"]
)

X = df["text"]
y = df["Label"]

# ================= TFIDF =================
vectorizer = TfidfVectorizer(
    stop_words="english",
    ngram_range=(1, 2),
    max_features=5000
)

X_vec = vectorizer.fit_transform(X)

# ================= TRAIN TEST SPLIT =================
X_train, X_test, y_train, y_test = train_test_split(
    X_vec,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# ================= MODELS =================
lr = LogisticRegression(max_iter=300)

rf = RandomForestClassifier(
    n_estimators=200,
    random_state=42
)

xgb = XGBClassifier(
    n_estimators=200,
    max_depth=5,
    learning_rate=0.1,
    eval_metric='logloss'
)

# ================= TRAIN =================
print("Training Logistic Regression...")
lr.fit(X_train, y_train)

print("Training Random Forest...")
rf.fit(X_train, y_train)

print("Training XGBoost...")
xgb.fit(X_train, y_train)

# ================= EVALUATE =================
models = {
    "LogisticRegression": lr,
    "RandomForest": rf,
    "XGBoost": xgb
}

print("\n================ RESULTS ================\n")

for name, model in models.items():

    pred = model.predict(X_test)

    acc = accuracy_score(y_test, pred)

    print(f"{name} Accuracy : {acc:.4f}")

    print(classification_report(y_test, pred))

    print("-" * 50)

# ================= SAVE =================
pickle.dump(lr, open("backend/models/lr.pkl", "wb"))
pickle.dump(rf, open("backend/models/rf.pkl", "wb"))
pickle.dump(xgb, open("backend/models/xgb.pkl", "wb"))
pickle.dump(vectorizer, open("backend/models/vectorizer.pkl", "wb"))

print("\n✅ Models Trained & Saved Successfully")