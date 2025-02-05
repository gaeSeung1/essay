from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse
import secrets
import uvicorn
import os

app = FastAPI()

# ✅ 토큰 저장소 (이메일 기반, 영구 유지)
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

# ✅ 토큰 인증 API (FastAPI가 프록시 역할 수행)
@app.get("/auth")
def authenticate(token: str):
    """토큰을 검증하고, 유효하면 리디렉트"""

    # ✅ 토큰이 유효한지 확인
    email = next((email for email, data in TOKENS.items() if data["token"] == token), None)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")

    # ✅ 로그 (선택적)
    print(f"User {email} authenticated successfully.")

    # ✅ ChatGPT 맞춤형 GPT 페이지로 리디렉트
    chatgpt_url = TOKENS[email]["redirect_url"]
    return RedirectResponse(url=chatgpt_url)

# ✅ 서버 상태 확인용 기본 엔드포인트
@app.get("/")
def read_root():
    return {"message": "FastAPI server is running!"}

# ✅ FastAPI 실행
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))  # 환경 변수에서 포트 값 가져오기
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
