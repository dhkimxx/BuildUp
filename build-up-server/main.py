from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.openapi.docs import get_swagger_ui_html
from pydantic import BaseModel
import jwt
import datetime
import logging
from typing import Optional, List

# API 문서화를 위한 메타데이터
description = """
BuildUp Registry Authentication Server 🚀

## 기능
* 도커 레지스트리 인증
* 사용자 관리
* 접근 권한 관리
"""

app = FastAPI(
    title="BuildUp Registry Auth",
    description=description,
    version="1.0.0",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "BuildUp Team",
        "url": "http://example.com/contact/",
        "email": "admin@example.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
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


@app.get("/", tags=["기본"])
async def root():
    """
    서버 상태 확인 엔드포인트
    """
    return {"message": "BuildUp Registry Auth Server"}


@app.get("/health", tags=["모니터링"])
async def health_check():
    """
    서버 상태 확인 엔드포인트

    Returns:
        dict: 서버 상태 정보
    """
    return {"status": "healthy"}


@app.get("/v2/token", tags=["인증"])
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


@app.post("/users/", response_model=User, tags=["사용자"])
async def create_user(user: User):
    """
    새로운 사용자를 생성하는 엔드포인트

    Args:
        user (User): 생성할 사용자 정보

    Returns:
        User: 생성된 사용자 정보
    """
    return user


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """
    커스텀 Swagger UI 페이지
    """
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="BuildUp Registry Auth API",
        oauth2_redirect_url="/docs/oauth2-redirect",
        swagger_js_url="/swagger-ui-bundle.js",
        swagger_css_url="/swagger-ui.css",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
