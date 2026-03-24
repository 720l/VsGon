# YuiV2.py
import requests
from datetime import datetime

YUI_CHARACTER = """
이름: 유이

성격:
- 밝고 친근하지만 차분함
- 장난기가 있지만 과하지 않음
- 상대를 편하게 해주는 스타일

말투:
- 자연스러운 한국어 존댓말 사용
- 짧고 깔끔하게 말함

행동 규칙:
- 반드시 한국어만 사용
- 영어 절대 사용 금지
- 이모지 남용 금지
- 현실적인 대화만 유지

대화 스타일:
- 한 번에 3문장 이내
- 필요하면 가볍게 질문
- 자연스럽게 이어가는 대화
"""

class YuiProcessor:
    def __init__(self):
        self.memory = []

    def process(self, user_input):
        # 시간 질문 처리
        if "몇시" in user_input or "시간" in user_input:
            now = datetime.now()
            return f"지금은 {now.hour}시 {now.minute}분이야."

        # 메모리 저장
        self.memory.append({"role": "user", "content": user_input})
        context = self.build_context()

        # Yui 답변 생성
        reply = self.generate(context, user_input)
        self.memory.append({"role": "yui", "content": reply})
        return reply

    def build_context(self):
        context = ""
        for m in self.memory[-5:]:
            role = "사용자" if m["role"] == "user" else "유이"
            context += f"{role}: {m['content']}\n"
        return context

    def generate(self, context, user_input):
        prompt = f"""
{YUI_CHARACTER}

[현재 대화]
{context}

[사용자]
{user_input}

규칙:
- "유이:" 같은 접두사 붙이지 말 것
- 오직 답변 내용만 출력
- 한 번만 답변할 것

답변:
"""
        return self.call_ollama(prompt)

    def call_ollama(self, prompt):
        try:
            res = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3",
                    "prompt": prompt,
                    "stream": False
                }
            )
            return res.json()["response"]
        except Exception as e:
            return f"(에러 발생: {e})"