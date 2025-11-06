"""
개선된 Disasters API - 다국어 지원 추가
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from src.database import get_db
from src.schemas.disaster import DisasterResponse

# 공통 i18n 라이브러리 import
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "shared"))
from i18n import translate, get_locale_from_request

# Mock data imports (기존)
from src.data.mock_data import (
    get_disasters,
    get_active_disasters,
    get_disaster as get_mock_disaster
)

router = APIRouter()


def get_language_from_request(request: Request) -> str:
    """
    Request에서 언어 설정 가져오기
    
    우선순위:
    1. Accept-Language 헤더
    2. 쿼리 파라미터 (?lang=ko)
    3. 기본 언어 (ko)
    """
    # Accept-Language 헤더
    accept_language = request.headers.get("Accept-Language", "")
    if accept_language:
        # 첫 번째 언어 추출 (예: "ko-KR,ko;q=0.9,en;q=0.8" -> "ko")
        parts = accept_language.split(",")
        if parts:
            lang = parts[0].split(";")[0].strip().split("-")[0]
            return lang.lower()
    
    # 쿼리 파라미터
    lang = request.query_params.get("lang")
    if lang:
        return lang.lower()
    
    return "ko"  # 기본 언어


@router.get("/", response_model=List[DisasterResponse])
async def get_disasters_endpoint(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    재난 목록 조회
    
    **다국어 지원**: Accept-Language 헤더 또는 ?lang=ko 쿼리 파라미터 사용
    """
    try:
        disasters = get_disasters()
        return disasters
    except Exception as e:
        lang = get_language_from_request(request)
        raise HTTPException(
            status_code=500,
            detail=translate("errors.server_error", lang=lang)
        )


@router.get("/active", response_model=List[DisasterResponse])
async def get_active_disasters_endpoint(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    활성 재난 목록 조회
    
    **다국어 지원**: Accept-Language 헤더 또는 ?lang=ko 쿼리 파라미터 사용
    """
    try:
        disasters = get_active_disasters()
        return disasters
    except Exception as e:
        lang = get_language_from_request(request)
        raise HTTPException(
            status_code=500,
            detail=translate("errors.server_error", lang=lang)
        )


@router.get("/{disaster_id}", response_model=DisasterResponse)
async def get_disaster_endpoint(
    disaster_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    재난 상세 정보 조회
    
    **다국어 지원**: Accept-Language 헤더 또는 ?lang=ko 쿼리 파라미터 사용
    """
    lang = get_language_from_request(request)
    
    disaster = get_mock_disaster(disaster_id)
    
    if not disaster:
        raise HTTPException(
            status_code=404,
            detail=translate("errors.disaster_not_found", lang=lang)
        )
    
    return disaster


# 추가: 재난 생성 API (다국어 응답)
@router.post("/", response_model=DisasterResponse)
async def create_disaster_endpoint(
    disaster_data: dict,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    새 재난 정보 생성
    
    **다국어 지원**: Accept-Language 헤더 또는 ?lang=ko 쿼리 파라미터 사용
    """
    lang = get_language_from_request(request)
    
    try:
        # 재난 생성 로직 (실제 구현 필요)
        # disaster = create_disaster(disaster_data)
        
        # 임시 응답
        raise HTTPException(
            status_code=501,
            detail=translate("errors.generic", lang=lang)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=translate("errors.server_error", lang=lang)
        )


# 추가: 재난 업데이트 API (다국어 응답)
@router.put("/{disaster_id}", response_model=DisasterResponse)
async def update_disaster_endpoint(
    disaster_id: str,
    disaster_data: dict,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    재난 정보 업데이트
    
    **다국어 지원**: Accept-Language 헤더 또는 ?lang=ko 쿼리 파라미터 사용
    """
    lang = get_language_from_request(request)
    
    # 재난 존재 확인
    disaster = get_mock_disaster(disaster_id)
    if not disaster:
        raise HTTPException(
            status_code=404,
            detail=translate("errors.disaster_not_found", lang=lang)
        )
    
    try:
        # 재난 업데이트 로직 (실제 구현 필요)
        # updated_disaster = update_disaster(disaster_id, disaster_data)
        
        # 임시 응답
        raise HTTPException(
            status_code=501,
            detail=translate("errors.generic", lang=lang)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=translate("errors.server_error", lang=lang)
        )


# 추가: 재난 삭제 API (다국어 응답)
@router.delete("/{disaster_id}")
async def delete_disaster_endpoint(
    disaster_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    재난 정보 삭제
    
    **다국어 지원**: Accept-Language 헤더 또는 ?lang=ko 쿼리 파라미터 사용
    """
    lang = get_language_from_request(request)
    
    # 재난 존재 확인
    disaster = get_mock_disaster(disaster_id)
    if not disaster:
        raise HTTPException(
            status_code=404,
            detail=translate("errors.disaster_not_found", lang=lang)
        )
    
    try:
        # 재난 삭제 로직 (실제 구현 필요)
        # delete_disaster(disaster_id)
        
        return {
            "success": True,
            "message": translate("api.success", lang=lang)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=translate("errors.server_error", lang=lang)
        )
