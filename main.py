import time
import secrets
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse

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

    # ✅ auth_link 값을 사용자의 Railway 서버 주소로 변경
    auth_link = f"https://web-production-339b.up.railway.app/auth?token={token}"

    return {
        "message": "Token generated",
        "token": token,
        "auth_link": auth_link  # ✅ 이제 올바른 URL 반환
    }

# ✅ 토큰 인증 API
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

    # ✅ ChatGPT 맞춤형 GPT 페이지로 리디렉트
    chatgpt_url = TOKENS[token]["redirect_url"]
    return RedirectResponse(url=chatgpt_url)
