from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import pipeline
from urllib.parse import quote as url_quote
import threading

# 創建 Flask 應用
app = Flask(__name__)
CORS(app)  # 啟用 CORS 允許跨域請求

# 加載 Hugging Face 的情緒分析模型
classifier = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment",use_fast=False)

# 定義細分的情緒範疇
def categorize_sentiment(label):
    if label in ['1 star', '2 stars']:
        return 'Negative'
    elif label == '3 stars':
        return 'Neutral'
    elif label in ['4 stars', '5 stars']:
        return 'Positive'
    else:
        return 'Unknown'

@app.route('/analyze', methods=['POST'])
def analyze_text():
    # 從請求中獲取文本數據
    data = request.get_json()
    text = data.get('text', '')

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    try:
        # 使用 Hugging Face 模型進行情緒分析
        result = classifier(text)[0]
        sentiment_label = result['label']
        confidence = result['score']

        # 將模型的星級轉換為細分情緒
        sentiment = categorize_sentiment(sentiment_label)

        # 返回分析結果
        return jsonify({
            'sentiment': sentiment,
            'sentiment_label': sentiment_label,  # 返回原始星級標籤
            'confidence': confidence
        })

    except Exception as e:
        # 處理異常情況
        return jsonify({'error': str(e)}), 500

# 啟動 Flask 應用的函數
def run_flask():
    app.run(port=5005, debug=False, use_reloader=False)

# 在新的線程中啟動 Flask 應用
threading.Thread(target=run_flask).start()
