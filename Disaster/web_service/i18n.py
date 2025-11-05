"""Simple translation utilities for the web service."""
from __future__ import annotations

from typing import Dict

LANGUAGES: Dict[str, str] = {
    "en": "English",
    "ko": "한국어",
}

_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        "app_name": "AI Energy Network",
        "login_html_title": "AI Energy Network - Login",
        "login_tagline": "Disaster-Response Energy Sharing Network",
        "login_info_title": "System Access",
        "login_info_body": "Energy network simulation and management system",
        "login_email_label": "Email address",
        "login_email_placeholder": "info@gngmeta.com",
        "login_password_label": "Password",
        "login_password_placeholder": "Enter your password",
        "login_button": "Log in",
        "language_label": "Language",
        "login_error_invalid_credentials": "Invalid username or password",
        "dashboard_html_title": "AI Energy Network - Dashboard",
        "dashboard_title_suffix": "Dashboard",
        "welcome_user": "Welcome, {username}",
        "logout": "Log out",
        "simulation_intro_title": "📊 Disaster-Response Energy Sharing Simulation",
        "simulation_intro_description": (
            "Simulate the cross-border energy sharing network across Japan, Korea, "
            "and the European Union."
        ),
        "simulation_run_title": "🚀 Run Simulation",
        "simulation_scenario_label": "Select scenario file",
        "simulation_scenario_sample": "Sample transnational event",
        "simulation_run_button": "Run simulation",
        "simulation_running": "Running simulation…",
        "simulation_results_title": "📈 Simulation Results",
        "simulation_results_placeholder": "Run a simulation to see results here.",
        "simulation_success": "Simulation completed successfully!",
        "dispatch_plan_title": "📊 Dispatch Plan",
        "dispatch_item_title": "Dispatch #{index}",
        "error_prefix": "Error: ",
        "error_unknown": "An unknown error occurred.",
        "footer_text": "Energy Orchestrator Platform © 2025",
        "language_switcher_hint": "Change language",
        "error_scenario_missing": "Scenario file not found: {path}",
    },
    "ko": {
        "app_name": "AI Energy Network",
        "login_html_title": "AI Energy Network - 로그인",
        "login_tagline": "재난 대응 에너지 공유 네트워크",
        "login_info_title": "시스템 접속",
        "login_info_body": "에너지 네트워크 시뮬레이션 및 관리 시스템",
        "login_email_label": "이메일 주소",
        "login_email_placeholder": "info@gngmeta.com",
        "login_password_label": "비밀번호",
        "login_password_placeholder": "비밀번호를 입력하세요",
        "login_button": "로그인",
        "language_label": "언어",
        "login_error_invalid_credentials": "아이디 또는 비밀번호가 올바르지 않습니다",
        "dashboard_html_title": "AI Energy Network - 대시보드",
        "dashboard_title_suffix": "대시보드",
        "welcome_user": "환영합니다, {username}",
        "logout": "로그아웃",
        "simulation_intro_title": "📊 재난 대응 에너지 공유 네트워크 시뮬레이션",
        "simulation_intro_description": "일본, 한국, EU 간의 국경을 넘나드는 에너지 공유 네트워크를 시뮬레이션합니다.",
        "simulation_run_title": "🚀 시뮬레이션 실행",
        "simulation_scenario_label": "시나리오 파일 선택",
        "simulation_scenario_sample": "샘플 국경간 이벤트",
        "simulation_run_button": "시뮬레이션 실행",
        "simulation_running": "시뮬레이션 실행 중…",
        "simulation_results_title": "📈 시뮬레이션 결과",
        "simulation_results_placeholder": "시뮬레이션을 실행하면 결과가 여기에 표시됩니다.",
        "simulation_success": "시뮬레이션이 성공적으로 완료되었습니다!",
        "dispatch_plan_title": "📊 디스패치 계획",
        "dispatch_item_title": "디스패치 #{index}",
        "error_prefix": "오류: ",
        "error_unknown": "알 수 없는 오류가 발생했습니다.",
        "footer_text": "Energy Orchestrator Platform © 2025",
        "language_switcher_hint": "언어 변경",
        "error_scenario_missing": "시나리오 파일을 찾을 수 없습니다: {path}",
    },
}

_DEFAULT_LANG = "ko"


def _normalize_lang(lang: str | None) -> str:
    if not lang:
        return _DEFAULT_LANG
    lang = lang.lower()
    if "-" in lang:
        lang = lang.split("-", 1)[0]
    return lang if lang in LANGUAGES else _DEFAULT_LANG


def translate(key: str, lang: str | None = None, **kwargs) -> str:
    locale = _normalize_lang(lang)
    catalog = _TRANSLATIONS.get(locale, {})
    default_catalog = _TRANSLATIONS.get("en", {})
    template = catalog.get(key, default_catalog.get(key, key))
    try:
        return template.format(**kwargs)
    except Exception:
        return template


def get_js_translations(lang: str | None = None) -> Dict[str, str]:
    locale = _normalize_lang(lang)
    keys = [
        "simulation_running",
        "simulation_success",
        "dispatch_plan_title",
        "dispatch_item_title",
        "error_prefix",
        "error_unknown",
        "simulation_results_placeholder",
    ]
    return {key: translate(key, locale) for key in keys}


def available_languages() -> Dict[str, str]:
    return LANGUAGES.copy()


def default_language() -> str:
    return _DEFAULT_LANG


def normalize_language(lang: str | None = None) -> str:
    return _normalize_lang(lang)

