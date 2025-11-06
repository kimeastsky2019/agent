"""
통합 다국어 지원 라이브러리
모든 마이크로서비스에서 공통으로 사용할 수 있는 i18n 모듈
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Optional, Any
from functools import lru_cache

# 지원 언어 목록
SUPPORTED_LANGUAGES = {
    "en": "English",
    "ko": "한국어",
    "ja": "日本語",
    "de": "Deutsch",
    "fr": "Français",
    "es": "Español",
    "el": "Ελληνικά",  # Greek
    "ro": "Română",  # Romanian
    "sv": "Svenska",  # Swedish
    "fi": "Suomi",  # Finnish
}

# 기본 언어
DEFAULT_LANGUAGE = "ko"

# 번역 파일 경로
TRANSLATIONS_DIR = Path(__file__).parent.parent / "translations"


class TranslationError(Exception):
    """번역 관련 에러"""
    pass


class I18n:
    """다국어 지원 클래스"""
    
    def __init__(self, translations_dir: Optional[Path] = None):
        """
        초기화
        
        Args:
            translations_dir: 번역 파일 디렉토리 경로
        """
        self.translations_dir = translations_dir or TRANSLATIONS_DIR
        self._translations: Dict[str, Dict[str, Any]] = {}
        self._load_translations()
    
    def _load_translations(self):
        """번역 파일 로드"""
        if not self.translations_dir.exists():
            raise TranslationError(
                f"Translation directory not found: {self.translations_dir}"
            )
        
        for lang_code in SUPPORTED_LANGUAGES.keys():
            translation_file = self.translations_dir / f"{lang_code}.json"
            if translation_file.exists():
                with open(translation_file, 'r', encoding='utf-8') as f:
                    self._translations[lang_code] = json.load(f)
    
    @staticmethod
    def normalize_language(lang: Optional[str]) -> str:
        """
        언어 코드 정규화
        
        Args:
            lang: 언어 코드 (예: "en", "en-US", "ko-KR")
            
        Returns:
            정규화된 언어 코드
        """
        if not lang:
            return DEFAULT_LANGUAGE
        
        # 소문자로 변환
        lang = lang.lower()
        
        # 지역 코드 제거 (en-US -> en)
        if "-" in lang:
            lang = lang.split("-")[0]
        
        # 지원하지 않는 언어면 기본 언어 반환
        return lang if lang in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE
    
    def get_translation(
        self,
        key: str,
        lang: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        번역 텍스트 가져오기
        
        Args:
            key: 번역 키 (점으로 구분된 경로, 예: "errors.not_found")
            lang: 언어 코드
            **kwargs: 템플릿 변수
            
        Returns:
            번역된 텍스트
        """
        locale = self.normalize_language(lang)
        
        # 현재 언어의 번역 가져오기
        translation = self._get_nested_value(
            self._translations.get(locale, {}),
            key
        )
        
        # 현재 언어에 번역이 없으면 영어로 fallback
        if translation is None and locale != "en":
            translation = self._get_nested_value(
                self._translations.get("en", {}),
                key
            )
        
        # 영어에도 없으면 키 그대로 반환
        if translation is None:
            translation = key
        
        # 템플릿 변수 치환
        try:
            if kwargs:
                translation = translation.format(**kwargs)
        except (KeyError, ValueError):
            # 템플릿 치환 실패 시 원본 반환
            pass
        
        return translation
    
    @staticmethod
    def _get_nested_value(data: Dict, key: str) -> Optional[str]:
        """
        중첩된 딕셔너리에서 값 가져오기
        
        Args:
            data: 딕셔너리
            key: 점으로 구분된 키 (예: "errors.not_found")
            
        Returns:
            값 또는 None
        """
        keys = key.split(".")
        current = data
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None
        
        return current if isinstance(current, str) else None
    
    def translate(self, key: str, lang: Optional[str] = None, **kwargs) -> str:
        """get_translation의 별칭"""
        return self.get_translation(key, lang, **kwargs)
    
    def t(self, key: str, lang: Optional[str] = None, **kwargs) -> str:
        """get_translation의 짧은 별칭"""
        return self.get_translation(key, lang, **kwargs)
    
    def get_translations_for_language(self, lang: Optional[str] = None) -> Dict:
        """
        특정 언어의 모든 번역 가져오기
        
        Args:
            lang: 언어 코드
            
        Returns:
            번역 딕셔너리
        """
        locale = self.normalize_language(lang)
        return self._translations.get(locale, {})
    
    def get_available_languages(self) -> Dict[str, str]:
        """
        사용 가능한 언어 목록
        
        Returns:
            언어 코드 -> 언어 이름 매핑
        """
        return SUPPORTED_LANGUAGES.copy()
    
    def is_language_supported(self, lang: str) -> bool:
        """
        언어 지원 여부 확인
        
        Args:
            lang: 언어 코드
            
        Returns:
            지원 여부
        """
        normalized = self.normalize_language(lang)
        return normalized in SUPPORTED_LANGUAGES


# 전역 인스턴스
_global_i18n: Optional[I18n] = None


def get_i18n() -> I18n:
    """전역 I18n 인스턴스 가져오기"""
    global _global_i18n
    if _global_i18n is None:
        _global_i18n = I18n()
    return _global_i18n


def translate(key: str, lang: Optional[str] = None, **kwargs) -> str:
    """번역 텍스트 가져오기 (편의 함수)"""
    return get_i18n().translate(key, lang, **kwargs)


def t(key: str, lang: Optional[str] = None, **kwargs) -> str:
    """번역 텍스트 가져오기 (짧은 별칭)"""
    return get_i18n().t(key, lang, **kwargs)


# Flask 통합
def get_locale_from_request(request) -> str:
    """
    Flask/FastAPI request에서 언어 설정 가져오기
    
    우선순위:
    1. 쿼리 파라미터 (?lang=ko)
    2. 세션
    3. Accept-Language 헤더
    4. 기본 언어
    """
    # 쿼리 파라미터
    lang = request.args.get('lang') if hasattr(request, 'args') else None
    if lang:
        return I18n.normalize_language(lang)
    
    # 세션
    if hasattr(request, 'session') and 'lang' in request.session:
        return I18n.normalize_language(request.session['lang'])
    
    # Accept-Language 헤더
    if hasattr(request, 'accept_languages'):
        best_match = request.accept_languages.best_match(
            list(SUPPORTED_LANGUAGES.keys())
        )
        if best_match:
            return I18n.normalize_language(best_match)
    
    return DEFAULT_LANGUAGE


def create_flask_translator(app):
    """
    Flask 앱에 번역 컨텍스트 프로세서 추가
    
    Usage:
        from shared.i18n import create_flask_translator
        create_flask_translator(app)
        
        # 템플릿에서:
        {{ _('common.welcome') }}
    """
    i18n_instance = get_i18n()
    
    @app.context_processor
    def inject_translations():
        from flask import request, session
        
        lang = get_locale_from_request(request)
        
        def _translate(key, **kwargs):
            return i18n_instance.translate(key, lang, **kwargs)
        
        return {
            "_": _translate,
            "t": _translate,
            "current_lang": lang,
            "supported_languages": SUPPORTED_LANGUAGES,
        }


def create_fastapi_middleware(app):
    """
    FastAPI 앱에 다국어 미들웨어 추가
    
    Usage:
        from shared.i18n import create_fastapi_middleware
        create_fastapi_middleware(app)
    """
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.requests import Request
    
    class I18nMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            # Accept-Language 헤더에서 언어 가져오기
            accept_language = request.headers.get("Accept-Language", "")
            lang = DEFAULT_LANGUAGE
            
            if accept_language:
                # 첫 번째 언어 추출
                parts = accept_language.split(",")
                if parts:
                    lang_code = parts[0].split(";")[0].strip()
                    lang = I18n.normalize_language(lang_code)
            
            # request state에 언어 저장
            request.state.lang = lang
            
            response = await call_next(request)
            response.headers["Content-Language"] = lang
            return response
    
    app.add_middleware(I18nMiddleware)


# 번역 키 검증 도구
def validate_translations() -> Dict[str, list]:
    """
    모든 번역 파일의 키 일관성 검증
    
    Returns:
        언어별 누락된 키 목록
    """
    i18n = get_i18n()
    en_keys = _get_all_keys(i18n._translations.get("en", {}))
    
    missing_keys = {}
    for lang_code in SUPPORTED_LANGUAGES.keys():
        if lang_code == "en":
            continue
        
        lang_keys = _get_all_keys(i18n._translations.get(lang_code, {}))
        missing = set(en_keys) - set(lang_keys)
        
        if missing:
            missing_keys[lang_code] = sorted(list(missing))
    
    return missing_keys


def _get_all_keys(data: Dict, prefix: str = "") -> list:
    """딕셔너리의 모든 키를 점 표기법으로 추출"""
    keys = []
    for key, value in data.items():
        full_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            keys.extend(_get_all_keys(value, full_key))
        else:
            keys.append(full_key)
    return keys


if __name__ == "__main__":
    # 테스트
    i18n = get_i18n()
    
    print("=== I18n Library Test ===")
    print(f"Supported languages: {i18n.get_available_languages()}")
    print(f"\nEnglish: {i18n.t('common.welcome', lang='en', username='John')}")
    print(f"Korean: {i18n.t('common.welcome', lang='ko', username='김동호')}")
    print(f"Japanese: {i18n.t('common.welcome', lang='ja', username='山田')}")
    
    print("\n=== Translation Validation ===")
    missing = validate_translations()
    if missing:
        print("Missing translations found:")
        for lang, keys in missing.items():
            print(f"\n{lang}: {len(keys)} keys missing")
            for key in keys[:5]:  # 처음 5개만 표시
                print(f"  - {key}")
    else:
        print("All translations are complete!")
