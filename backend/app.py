from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import os
import mysql.connector
from dotenv import load_dotenv
app = Flask(__name__)
CORS(app)

# ================= DATABASE =================
# db = mysql.connector.connect(
#     host="trolley.proxy.rlwy.net",
#     user="root",
#     password="PVCyfrSOSSzrEWnFnvWQXsJfvVrugfue",
#     database="fakereview",
#     port=57600

# )

load_dotenv()

db = mysql.connector.connect(

    host=os.getenv("MYSQLHOST"),

    user=os.getenv("MYSQLUSER"),

    password=os.getenv("MYSQLPASSWORD"),

    database=os.getenv("MYSQLDATABASE"),

    port=int(os.getenv("MYSQLPORT"))

)

cursor = db.cursor()

# ================= LOAD MODELS =================
lr = pickle.load(open("models/lr.pkl", "rb"))
rf = pickle.load(open("models/rf.pkl", "rb"))
xgb = pickle.load(open("models/xgb.pkl", "rb"))
vectorizer = pickle.load(open("models/vectorizer.pkl", "rb"))

# ================= CATEGORY MAP =================
product_categories = {
    "mobile": "electronics",
    "laptop": "electronics",
    "tv": "electronics",
    "t-shirt": "fashion",
    "shoes": "fashion",
    "perfume": "fashion"
}

fashion_words = {
    'shirt','t-shirt','cloth','jeans',
    'dress','shoes','fabric','cotton',
    'fit','size','style','fashion'
}

electronics_words = {
    'battery','charger','screen',
    'processor','ram','display',
    'camera','performance','mobile'
}

perfume_words = {
    'fragrance','smell','scent',
    'perfume','lasting'
}

# ================= REGISTER =================
@app.route("/register", methods=["POST"])
def register():
     try:
        data = request.json

        cursor.execute(
            "INSERT INTO users(username,password) VALUES(%s,%s)",
            (data["username"], data["password"])
        )

        db.commit()

        return jsonify({"msg":"registered"})
    
     except Exception as e:
       print("❌ DB ERROR:", e)


# ================= LOGIN =================
@app.route("/login", methods=["POST"])
def login():
     try:
        data = request.json

        cursor.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (data["username"], data["password"])
        )

        user = cursor.fetchone()

        return jsonify({"success": user != None})
     except Exception as e:

        print("❌ DB ERROR:", e)
     

# ================= PREDICT =================
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.json

        review = data["review"].lower()
        product = data["product"].lower()

        category = product_categories.get(product, "")

        # combine context
        text = product + " " + category + " " + review

        vec = vectorizer.transform([text])

        # predictions
        lr_pred = int(lr.predict(vec)[0])
        rf_pred = int(rf.predict(vec)[0])
        xgb_pred = int(xgb.predict(vec)[0])

        votes = [lr_pred, rf_pred, xgb_pred]

        final = max(set(votes), key=votes.count)

        # ================= RULE BASED CHECK =================
        words = set(review.split())

        fashion_match = any(w in words for w in fashion_words)
        electronics_match = any(w in words for w in electronics_words)
        perfume_match = any(w in words for w in perfume_words)

        reason = "Review matches product"

        # electronics products
        if product in ["mobile", "laptop", "tv"]:

            if fashion_match or perfume_match:
                final = 1
                reason = "Fashion/perfume review used for electronics"

        # fashion products
        elif product in ["t-shirt", "shoes"]:

            if electronics_match:
                final = 1
                reason = "Electronics review used for fashion product"

        # perfume
        elif product == "perfume":

            if electronics_match or fashion_match:
                final = 1
                reason = "Wrong review category for perfume"

        # confidence
        confidence = round(
            (votes.count(final) / len(votes)) * 100,
            2
        )

        # save
        cursor.execute(
            "INSERT INTO review(product,review,result) VALUES(%s,%s,%s)",
            (product, review, final)
        )

        db.commit()

        return jsonify({
            "final": int(final),
            "lr": lr_pred,
            "rf": rf_pred,
            "xgb": xgb_pred,
            "confidence": confidence,
            "reason": reason
        })
    
    except Exception as e:

        print("❌ DB ERROR:", e)


# ================= ALL REVIEWS =================
@app.route("/reviews", methods=["GET"])
def reviews():
   try:
    cursor.execute(
        "SELECT product,review,result FROM review"
    )

    rows = cursor.fetchall()

    data = []

    for r in rows:

        data.append({
            "product": r[0],
            "review": r[1],
            "final": r[2]
        })

    return jsonify(data)
   except Exception as e:

    print("❌ DB ERROR:", e)

# ================= RUN =================
# app.run(debug=True)
if __name__ == "__main__":
    
        port = int(os.environ.get("port",5000))
        app.run(host="0.0.0.0", port=port)
 
