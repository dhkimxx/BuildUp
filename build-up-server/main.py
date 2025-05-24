from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import jwt
import datetime
import logging

app = FastAPI()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# JWT 설정 (실제 운영환경에서는 환경변수나 설정 파일에서 관리해야 함)
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"


@app.get("/")
async def root():
    return {"message": "BuildUp Registry Auth Server"}


@app.get("/v2/token")
async def get_token(request: Request):
    """
    Docker Registry 인증 토큰을 발급하는 엔드포인트
    """
    logger.info(f"Token request received: {request.headers}")

    # 실제 구현에서는 여기에 인증 로직 추가
    token = jwt.encode(
        {
            "access": [
                {"type": "repository", "name": "*", "actions": ["pull", "push"]}
            ],
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return JSONResponse(content={"token": token})


@app.get("/health")
async def health_check():
    """
    서버 상태 확인 엔드포인트
    """
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
