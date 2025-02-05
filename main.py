from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse, Response
import time
import secrets
import uvicorn
import os
import requests


app = FastAPI()

# ✅ 이메일-토큰 저장소 (영구 저장용)
TOKENS = {}  # {email: {"token": token, "redirect_url": url}}

# ✅ 토큰 생성 API
@app.get("/generate_token")
def generate_token(email: str = Query(..., description="User email")):
    """구매자의 이메일을 기반으로 영구적인 인증 토큰을 생성"""
    
    # ✅ 이미 등록된 이메일이면 기존 토큰 반환
    if email in TOKENS:
        return {
            "message": "Token already exists",
            "token": TOKENS[email]["token"],
            "auth_link": f"https://web-production-339b.up.railway.app/auth?token={TOKENS[email]['token']}"
        }
    
    # ✅ 새 토큰 생성
    token = secrets.token_urlsafe(16)
    TOKENS[email] = {
        "token": token,
        "redirect_url": "https://chatgpt.com/g/g-67a089879d0c819184d793d8ab8ed247-ai-essay",
        "email": email
    }

    auth_link = f"https://web-production-339b.up.railway.app/auth?token={token}"

    return {
        "message": "Token generated",
        "token": token,
        "auth_link": auth_link
    }

# ✅ 이메일 기반 인증 API (프록시 방식)
@app.get("/auth")
def authenticate(token: str):
    """토큰을 검증하고 구매자의 이메일을 확인 후 리디렉션"""

    # ✅ 토큰이 유효한지 확인
    email = next((email for email, data in TOKENS.items() if data["token"] == token), None)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")

    # ✅ 구매자 이메일 정보 로깅 (선택적)
    print(f"User {email} authenticated successfully.")

    # ✅ FastAPI 서버가 `redirect_url` 데이터를 요청 후 반환 (프록시 방식)
    chatgpt_url = TOKENS[email]["redirect_url"]
    response = requests.get(chatgpt_url)

    return Response(content=response.content, media_type=response.headers.get("content-type"))







@app.get("/")
def read_root():
    return {"message": "FastAPI server is running!"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))  # 환경 변수에서 포트 값 가져오기
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
