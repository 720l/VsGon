# bot.py

import os
import discord
import json
import aiohttp
import re
import requests

def main():
    # 실행 시점에만 TOKEN 가져오기
    TOKEN = os.environ.get("Discord_TOKEN")
    if TOKEN is None:
        raise ValueError("Discord_TOKEN 환경 변수가 설정되지 않았습니다.")

    SERVER_URL = "http://127.0.0.1:5001/chat"

    # Discord 클라이언트 설정
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    MEMORY_FILE = "memory.json"

    # 🔥 메모리 로드
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            memory = json.load(f)
    else:
        memory = {}

    # 🔹 메모리 저장 함수
    def save_memory():
        with open(MEMORY_FILE, "w") as f:
            json.dump(memory, f, ensure_ascii=False, indent=2)

    # 🔹 비동기 서버 호출
    async def call_server(user_input, user_memory):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    SERVER_URL,
                    json={
                        "message": user_input,
                        "memory": user_memory,
                        "history": user_memory["history"]
                    },
                    timeout=10
                ) as resp:
                    data = await resp.json()
                    return data.get("reply", "응답 없음")
            except Exception as e:
                print("🔥 봇 에러:", e)
                return None

    # 🔹 봇 준비 이벤트
    @client.event
    async def on_ready():
        print(f"로그인 완료: {client.user}")

    # 🔹 메시지 이벤트
    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        if not message.content.startswith("!유이"):
            return

        user_id = str(message.author.id)
        user_input = message.content.replace("!유이", "").strip()

        if user_input == "":
            await message.channel.send("내용을 입력해줘!")
            return

        # 🔥 유저 초기화
        if user_id not in memory:
            memory[user_id] = {"name": "", "history": []}

        user_memory = memory[user_id]

        # 🔥 이름 기억
        if "이름은" in user_input:
            name = user_input.split("이름은")[-1].strip()
            user_memory["name"] = name
            save_memory()
            await message.channel.send(f"이름 {name} 기억했어!")
            return

        # 🔥 이름 확인
        if "내 이름 뭐야" in user_input:
            if user_memory["name"]:
                await message.channel.send(f"음..{user_memory['name']} 맞지?")
            else:
                await message.channel.send("누구세요?")
            return

        # 🔹 최근 메시지 삭제 명령어 처리
        if "지워" in user_input:
            match = re.search(r'(\d+)', user_input)
            limit = int(match.group(1)) if match else 1  # 기본 1개 삭제
            try:
                deleted = 0
                async for msg in message.channel.history(limit=limit):
                    await msg.delete()
                    deleted += 1
                confirm = await message.channel.send(f"{deleted}개 지웠어!")
                await confirm.delete(delay=5)
            except discord.Forbidden:
                await message.channel.send("메시지 삭제 권한을 줄래?")
            except discord.HTTPException as e:
                await message.channel.send(f"⚠️ 삭제 못하겠어: {e}")
            return

        # 🔹 AI 처리
        thinking_msg = await message.channel.send("...")

        reply = await call_server(user_input, user_memory)
        if reply is None:
            await thinking_msg.edit(content="서버 안열렸어")
            return

        user_memory["history"].append({"role": "user", "content": user_input})
        user_memory["history"].append({"role": "assistant", "content": reply})
        user_memory["history"] = user_memory["history"][-5:]
        save_memory()
        await thinking_msg.edit(content=reply)

    # 🔹 Discord 봇 실행
    client.run(TOKEN)

# 🔹 실행 시점에만 main() 호출
if __name__ == "__main__":
    main()
