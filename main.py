from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse
import time
import secrets
import uvicorn
import os


app = FastAPI()

# ✅ 토큰 저장소 (DB 대신 임시 사용)
TOKENS = {}

# ✅ 토큰 생성 API
@app.get("/generate_token")
def generate_token(email: str = Query(..., description="User email")):
    token = secrets.token_urlsafe(16)  # 랜덤한 16바이트 토큰 생성
    TOKENS[token] = {
        "expires": time.time() + 86400,  # 24시간 유효
        "redirect_url": "https://chatgpt.com/g/g-67a089879d0c819184d793d8ab8ed247-ai-essay",
        "email": email
    }
    return {"message": "Token generated", "token": token, "auth_link": f"https://your-server.com/auth?token={token}"}

# ✅ 토큰 인증 API
@app.get("/auth")
def authenticate(token: str):
    # ✅ 토큰 유효성 검사
    if token not in TOKENS or time.time() > TOKENS[token]["expires"]:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # ✅ ChatGPT 맞춤형 GPT 페이지로 리디렉트
    chatgpt_url = TOKENS[token]["redirect_url"]
    return RedirectResponse(url=chatgpt_url)


@app.get("/")
def read_root():
    return {"message": "FastAPI server is running!"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))  # 환경 변수에서 포트 값 가져오기
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
