from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

genai.configure(api_key="API_KEY")
if api_key is None:
    raise ValueError("API_KEY 환경 변수가 설정되지 않았습니다.")
# 🔥 최신 안정 모델
model = genai.GenerativeModel("gemini-2.5-flash")


@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        user_message = data.get("message", "")

        response = model.generate_content(user_message)

        return jsonify({"reply": response.text})

    except Exception as e:
        print("🔥 서버 에러:", e)
        return jsonify({"reply": "에러 발생 😢"}), 200


if __name__ == "__main__":
    print("🔥 서버 시작됨")
    app.run(port=5001)
