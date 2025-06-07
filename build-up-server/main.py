from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
import jwt
import datetime
import logging
from typing import Optional, List
import psutil

app = FastAPI(
    title="BuildUp Registry Auth",
    version="1.0.0",
)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# JWT 설정 (실제 운영환경에서는 환경변수나 설정 파일에서 관리해야 함)
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

# 기본 인증
security = HTTPBasic()


# Pydantic 모델 (Spring Boot의 DTO, Gin의 struct와 유사)
class User(BaseModel):
    username: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    disabled: Optional[bool] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegistryAccess(BaseModel):
    type: str
    name: str
    actions: List[str]


@app.get("/health", tags=["Monitoring"])
async def health_check():
    return Response(content="OK", status_code=200)


@app.get("/stats", tags=["Monitoring"])
async def stats_check():
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    net_io = psutil.net_io_counters()

    res = f"CPU Usage: {cpu_percent}% \
        \nMemory Usage: {memory.used / (1024 ** 2):.2f} MB / {memory.total / (1024 ** 2):.2f} MB \
        \nReceived: {net_io.bytes_recv / (1024 ** 2):.2f} MB, Sent: {net_io.bytes_sent / (1024 ** 2):.2f} MB"
    return Response(content=res, status_code=200)


@app.get("/v2/token", tags=["Authentication"])
async def get_token(
    request: Request, credentials: HTTPBasicCredentials = Depends(security)
):
    """
    Docker Registry 인증 토큰을 발급하는 엔드포인트

    Args:
        request (Request): HTTP 요청 객체
        credentials (HTTPBasicCredentials): 기본 인증 정보

    Returns:
        JSONResponse: JWT 토큰

    Raises:
        HTTPException: 인증 실패시 401 에러
    """
    logger.info(f"Token request received from: {credentials.username}")

    # 실제 구현에서는 여기에 사용자 인증 로직 추가
    if credentials.username == "testuser" and credentials.password == "testpass":
        token = jwt.encode(
            {
                "sub": credentials.username,
                "access": [
                    {"type": "repository", "name": "*", "actions": ["pull", "push"]}
                ],
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
            },
            SECRET_KEY,
            algorithm=ALGORITHM,
        )
        return JSONResponse(content={"token": token})
    else:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Basic"},
        )


@app.post("/users/", response_model=User, tags=["User"])
async def create_user(user: User):
    """
    새로운 사용자를 생성하는 엔드포인트

    Args:
        user (User): 생성할 사용자 정보

    Returns:
        User: 생성된 사용자 정보
    """
    return user


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
