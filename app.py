from flask import Flask, request, jsonify, send_file, send_from_directory
from transformers import pipeline
from flask_cors import CORS
import re
import pandas as pd
import io
import csv
from googletrans import Translator  # Thêm Google Translate

app = Flask(__name__, static_folder="static")
CORS(app)

# 1. Mô hình phân tích cảm xúc (tiếng Anh)
sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

# 2. Mô hình phân loại khía cạnh (zero-shot)
aspect_classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# 3. Các nhãn khía cạnh
aspect_labels = [
    "Food (taste, quality, freshness)",
    "Service (staff, attitude, speed)",
    "Atmosphere (ambience, decoration, music)",
    "Promotion (discount, price, value)",
    "Overall"
]

aspect_vi_labels = {
    "Food (taste, quality, freshness)": "🍽️ Đồ ăn & thức uống (hương vị, chất lượng, độ tươi)",
    "Service (staff, attitude, speed)": "🧑‍💼 Dịch vụ (nhân viên, thái độ, tốc độ)",
    "Atmosphere (ambience, decoration, music)": "🪑 Không gian quán (không khí, trang trí, âm nhạc)",
    "Promotion (discount, price, value)": "💸 Giá cả & khuyến mãi (giảm giá, giá cả, giá trị)",
    "Overall": "⭐ Nhận xét chung (không rõ chủ đề cụ thể)"
}

last_summary = {}  # Dữ liệu tổng hợp mới nhất

translator = Translator()  # Khởi tạo Google Translate

def translate_en_to_vi(text):
    """Dịch tiếng Anh sang tiếng Việt bằng Google Translate"""
    try:
        result = translator.translate(text, src='en', dest='vi')
        return result.text
    except Exception as e:
        print("Translation error:", e)
        return text  # Nếu lỗi thì trả lại bản gốc

def clean(text):
    return re.sub(r"\s+", " ", str(text).strip())

def analyze_text(text):
    """Phân tích 1 feedback"""
    original = clean(text)

    # Phân tích sentiment
    sentiment_result = sentiment_pipeline(original)[0]
    sentiment_label_raw = sentiment_result["label"]
    sentiment_label = f"{sentiment_label_raw} ({sentiment_result['score']*100:.2f}%)"

    # Phân tích aspect
    aspect_result = aspect_classifier(original, aspect_labels)
    top_label = aspect_result["labels"][0]
    top_score = aspect_result["scores"][0]
    aspect = top_label if top_score > 0.25 else "Không rõ"

    # Dịch sang tiếng Việt
    translated_text = translate_en_to_vi(original)

    return {
        "Original Review": original,
        "Translated Review": translated_text,
        "Sentiment": sentiment_label,
        "Sentiment Label": sentiment_label_raw,
        "Main Aspect": aspect_vi_labels.get(aspect, "Không rõ"),
        "Aspect Confidence": f"{top_score*100:.2f}%" if aspect != "Không rõ" else "-"
    }

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


# Phân tích đánh giá thủ công
@app.route("/analyze-batch", methods=["POST"])
def analyze_batch():
    data = request.get_json()
    feedbacks = data.get("feedbacks", [])
    results = [analyze_text(text) for text in feedbacks]

    if len(results) == 1:
        return jsonify({"results": results})

    df = pd.DataFrame(results)
    summary = {
        "total": len(df),
        "positive": int((df["Sentiment Label"] == "POSITIVE").sum()),
        "negative": int((df["Sentiment Label"] == "NEGATIVE").sum()),
        "unclear_aspect": int((df["Main Aspect"] == "Không rõ").sum()),
        "aspect_counts": df["Main Aspect"].value_counts().to_dict(),
        "negative_by_aspect": df[df["Sentiment Label"] == "NEGATIVE"]["Main Aspect"].value_counts().to_dict()
    }

    return jsonify({"results": results, "summary": summary})


# Phân tích đánh giá từ file CSV
@app.route("/analyze-csv", methods=["POST"])
def analyze_csv():
    global last_summary

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    df = pd.read_csv(file, header=None, skiprows=1)
    df['review'] = df.apply(lambda row: ' '.join(row.dropna().astype(str)), axis=1)

    results = [analyze_text(text) for text in df["review"]]
    df_result = pd.DataFrame(results)

    last_summary = {
        "total": len(df_result),
        "positive": int((df_result["Sentiment Label"] == "POSITIVE").sum()),
        "negative": int((df_result["Sentiment Label"] == "NEGATIVE").sum()),
        "unclear_aspect": int((df_result["Main Aspect"] == "Không rõ").sum()),
        "aspect_counts": df_result["Main Aspect"].value_counts().to_dict(),
        "negative_by_aspect": df_result[df_result["Sentiment Label"] == "NEGATIVE"]["Main Aspect"].value_counts().to_dict()
    }

    # Xuất CSV
    output = io.StringIO()
    df_result.to_csv(output, index=False, encoding='utf-8-sig', columns=["Original Review", "Translated Review", "Sentiment", "Main Aspect"])
    output.seek(0)

    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='review_analysis_output.csv'
    )

@app.route("/get-latest-summary", methods=["GET"])
def get_latest_summary():
    if not last_summary:
        return jsonify({"error": "No summary available"}), 404
    return jsonify(last_summary)

if __name__ == "__main__":
    print("Starting Flask app...")
    app.run(debug=True, port=5000)

