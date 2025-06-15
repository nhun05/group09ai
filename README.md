<<<<<<< HEAD
# Ứng dụng Phân Tích Cảm Xúc và Dịch Máy

Đây là một sản phẩm demo ứng dụng Xử lý ngôn ngữ tự nhiên (NLP) sử dụng các mô hình Transformer để phân tích cảm xúc và dịch văn bản tiếng Anh sang tiếng Việt. Giao diện web cho phép người dùng:

- Nhập một đánh giá và phân tích cảm xúc (Positive / Negative).
- Tải lên file CSV chứa nhiều đánh giá và phân tích hàng loạt.
- Trích xuất file kết quả phân tích dưới dạng CSV.

## 📦 Cấu trúc thư mục

```
sentiment_web_project/
│
├── app.py                    # Flask backend xử lý yêu cầu
├── static/                   # Thư mục chứa HTML, CSS, JS
│   └── index.html            # Giao diện chính
├── requirements.txt          # Các thư viện cần cài đặt
├── README.md                 # File giới thiệu này
```

## 🚀 Cài đặt và chạy dự án

1. **Clone repo hoặc giải nén thư mục**
2. **Tạo môi trường ảo (tuỳ chọn)**:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **Cài đặt thư viện**:
```bash
pip install -r requirements.txt
```

4. **Chạy ứng dụng Flask**:
```bash
python app.py
```

5. **Truy cập trình duyệt tại** `http://127.0.0.1:5000`

## 🔧 Công nghệ sử dụng

- Python 3
- Flask
- Hugging Face Transformers
- Pandas

## 🤖 Mô hình NLP sử dụng

- `distilbert-base-uncased-finetuned-sst-2-english`: Phân tích cảm xúc
- `Helsinki-NLP/opus-mt-en-vi`: Dịch tiếng Anh sang tiếng Việt

## 📄 License

Dành cho mục đích học tập và nghiên cứu.

---

✅ *Đề tài: Ứng dụng NLP trong phân tích cảm xúc và dịch máy với mô hình Transformer*

# group09ai

