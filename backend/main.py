"""
Calligraphy Coach Backend Server
FastAPI 기반 서예 학습 앱 백엔드
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sys
import os
from pathlib import Path

# AI 엔진 경로 추가
sys.path.append(str(Path(__file__).parent.parent))
from ai_engine.analysis.integrated_zhong_analyzer import IntegratedZhongAnalyzer
from ai_engine.analysis.char_comparison import CharComparison

app = FastAPI(
    title="Calligraphy Coach API",
    description="AI 기반 서예 학습 백엔드 서비스",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AI 분석기 초기화
zhong_analyzer = IntegratedZhongAnalyzer()
char_comparison = CharComparison()

@app.get("/")
async def root():
    """헬스 체크 엔드포인트"""
    return {"message": "Calligraphy Coach API is running", "status": "healthy"}

@app.post("/analyze/upload")
async def analyze_calligraphy(
    reference_image: UploadFile = File(...),
    user_image: UploadFile = File(...)
):
    """
    서예 이미지 분석 API
    
    Args:
        reference_image: 교본 이미지
        user_image: 사용자 작성 이미지
    
    Returns:
        분석 결과 (점수, 피드백, 개선점)
    """
    try:
        # 이미지 저장
        ref_path = f"temp/reference_{reference_image.filename}"
        user_path = f"temp/user_{user_image.filename}"
        
        os.makedirs("temp", exist_ok=True)
        
        # 파일 저장
        with open(ref_path, "wb") as f:
            content = await reference_image.read()
            f.write(content)
            
        with open(user_path, "wb") as f:
            content = await user_image.read()
            f.write(content)
        
        # AI 분석 실행
        result = char_comparison.compare_characters(ref_path, user_path)
        
        # 임시 파일 삭제
        os.remove(ref_path)
        os.remove(user_path)
        
        return JSONResponse(content={
            "success": True,
            "analysis": result
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/characters")
async def get_available_characters():
    """학습 가능한 한자 목록"""
    return {
        "characters": [
            {"id": "zhong", "char": "中", "name": "가운데 중", "level": 1},
            {"id": "shi", "char": "十", "name": "열 십", "level": 1},
            {"id": "kou", "char": "口", "name": "입 구", "level": 1},
            {"id": "ri", "char": "日", "name": "날 일", "level": 2},
            {"id": "tian", "char": "田", "name": "밭 전", "level": 2},
        ]
    }

@app.get("/user/progress")
async def get_user_progress(user_id: str):
    """사용자 학습 진도 조회"""
    # TODO: 데이터베이스 연동
    return {
        "user_id": user_id,
        "total_practice": 42,
        "characters_learned": 5,
        "average_score": 78.5,
        "streak_days": 7
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)