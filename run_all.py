import subprocess
import sys

print("🔥 서버 실행 중...")
server = subprocess.Popen([sys.executable, "server.py"])

print("🤖 디스코드 봇 실행 중...")
bot = subprocess.Popen([sys.executable, "bot.py"])

try:
    server.wait()
    bot.wait()
except KeyboardInterrupt:
    print("\n종료 중...")
    server.terminate()
    bot.terminate()