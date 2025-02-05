from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response
import time
import secrets
import uvicorn
import os
import requests


app = FastAPI()

# ✅ 토큰 저장소 (임시 데이터베이스)
TOKENS = {}

# ✅ 토큰 생성 API
@app.get("/generate_token")
def generate_token(email: str = Query(..., description="User email")):
    """사용자의 이메일을 기반으로 24시간 유효한 토큰을 생성"""
    token = secrets.token_urlsafe(16)  # 랜덤한 16바이트 토큰 생성
    TOKENS[token] = {
        "expires": time.time() + 86400,  # 24시간 유효
        "redirect_url": "https://chatgpt.com/g/g-67a089879d0c819184d793d8ab8ed247-ai-essay",
        "email": email
    }

    # ✅ 보안이 강화된 auth_link 반환 (사용자는 최종 URL을 알 수 없음)
    auth_link = f"https://web-production-339b.up.railway.app/auth?token={token}"

    return {
        "message": "Token generated",
        "token": token,
        "auth_link": auth_link
    }

# ✅ 프록시 기반 토큰 인증 API
@app.get("/auth")
def authenticate(token: str):
    """구매자가 인증 링크를 클릭했을 때 실행되는 API"""
    if token not in TOKENS:
        raise HTTPException(status_code=401, detail="Invalid token")

    # ✅ 토큰 만료 여부 확인
    if time.time() > TOKENS[token]["expires"]:
        raise HTTPException(status_code=401, detail="Token expired")

    # ✅ 구매자 이메일 정보 로깅 (선택적)
    print(f"User {TOKENS[token]['email']} authenticated successfully.")

    # ✅ FastAPI 서버가 직접 `redirect_url`의 데이터를 가져와서 반환 (프록시 역할 수행)
    chatgpt_url = TOKENS[token]["redirect_url"]
    response = requests.get(chatgpt_url)

    # ✅ 원본 사이트의 응답을 그대로 반환 (구매자는 원본 URL을 모름)
    return Response(content=response.content, media_type=response.headers.get("content-type"))





@app.get("/")
def read_root():
    return {"message": "FastAPI server is running!"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))  # 환경 변수에서 포트 값 가져오기
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
