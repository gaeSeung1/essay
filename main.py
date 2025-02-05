import secrets
import requests
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response

app = FastAPI()

# ✅ 이메일 기반 토큰 저장소 (토큰은 영구적으로 유지됨)
TOKENS = {}

# ✅ 토큰 생성 API
@app.get("/generate_token")
def generate_token(email: str = Query(..., description="User email")):
    """이메일을 기반으로 영구적인 인증 토큰을 생성"""
    
    # ✅ 이미 등록된 이메일이면 기존 토큰 반환
    if email in TOKENS:
        return {
            "message": "Token already exists",
            "token": TOKENS[email]["token"],
            "auth_link": f"https://web-production-597ec.up.railway.app/auth?token={TOKENS[email]['token']}"
        }
    
    # ✅ 새 토큰 생성
    token = secrets.token_urlsafe(16)
    TOKENS[email] = {
        "token": token,
        "redirect_url": "https://chatgpt.com/g/g-67a089879d0c819184d793d8ab8ed247-ai-essay",
        "email": email
    }

    return {
        "message": "Token generated",
        "token": token,
        "auth_link": f"https://web-production-597ec.up.railway.app/auth?token={token}"
    }

# ✅ 프록시 방식 토큰 인증 API
@app.get("/auth")
def authenticate(token: str):
    """토큰을 검증하고 구매자의 이메일을 확인 후 데이터를 반환"""

    # ✅ 토큰이 유효한지 확인
    email = next((email for email, data in TOKENS.items() if data["token"] == token), None)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")

    # ✅ 로그 (선택적)
    print(f"User {email} authenticated successfully.")

    # ✅ FastAPI 서버가 `redirect_url`의 데이터를 직접 가져와서 반환 (프록시 방식)
    chatgpt_url = TOKENS[email]["redirect_url"]
    response = requests.get(chatgpt_url)

    # ✅ 구매자는 원본 `redirect_url`을 절대 알 수 없음
    return Response(content=response.content, media_type=response.headers.get("content-type"))
