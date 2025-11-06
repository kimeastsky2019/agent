#!/usr/bin/env python3
"""
번역 관리 도구
- 번역 누락 키 감지
- 번역 커버리지 리포트
- 새 번역 키 추가
- 번역 파일 검증
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict

# 프로젝트 루트 디렉토리
PROJECT_ROOT = Path(__file__).parent.parent
TRANSLATIONS_DIR = PROJECT_ROOT / "translations"
SHARED_DIR = PROJECT_ROOT / "shared"

# 공통 i18n 라이브러리 import
sys.path.insert(0, str(SHARED_DIR))
from i18n import SUPPORTED_LANGUAGES, I18n


class TranslationValidator:
    """번역 검증기"""
    
    def __init__(self, translations_dir: Path = TRANSLATIONS_DIR):
        self.translations_dir = translations_dir
        self.translations: Dict[str, Dict] = {}
        self._load_translations()
    
    def _load_translations(self):
        """모든 번역 파일 로드"""
        for lang_code in SUPPORTED_LANGUAGES.keys():
            translation_file = self.translations_dir / f"{lang_code}.json"
            if translation_file.exists():
                with open(translation_file, 'r', encoding='utf-8') as f:
                    self.translations[lang_code] = json.load(f)
            else:
                print(f"⚠️  Warning: Translation file not found: {translation_file}")
                self.translations[lang_code] = {}
    
    def get_all_keys(self, data: Dict, prefix: str = "") -> Set[str]:
        """딕셔너리의 모든 키를 점 표기법으로 추출"""
        keys = set()
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                keys.update(self.get_all_keys(value, full_key))
            else:
                keys.add(full_key)
        return keys
    
    def validate_completeness(self) -> Dict[str, Set[str]]:
        """
        번역 완성도 검증
        
        Returns:
            언어별 누락된 키 목록
        """
        if "en" not in self.translations:
            print("❌ Error: English (en) translation file is missing")
            return {}
        
        # 영어를 기준으로 모든 키 추출
        en_keys = self.get_all_keys(self.translations["en"])
        
        # 각 언어별로 누락된 키 확인
        missing_keys = {}
        for lang_code in SUPPORTED_LANGUAGES.keys():
            if lang_code == "en":
                continue
            
            if lang_code not in self.translations:
                missing_keys[lang_code] = en_keys
                continue
            
            lang_keys = self.get_all_keys(self.translations[lang_code])
            missing = en_keys - lang_keys
            
            if missing:
                missing_keys[lang_code] = missing
        
        return missing_keys
    
    def validate_extra_keys(self) -> Dict[str, Set[str]]:
        """
        영어에 없는 추가 키 찾기
        
        Returns:
            언어별 추가 키 목록
        """
        if "en" not in self.translations:
            return {}
        
        en_keys = self.get_all_keys(self.translations["en"])
        
        extra_keys = {}
        for lang_code in SUPPORTED_LANGUAGES.keys():
            if lang_code == "en":
                continue
            
            if lang_code not in self.translations:
                continue
            
            lang_keys = self.get_all_keys(self.translations[lang_code])
            extra = lang_keys - en_keys
            
            if extra:
                extra_keys[lang_code] = extra
        
        return extra_keys
    
    def get_translation_stats(self) -> Dict[str, Dict]:
        """
        번역 통계
        
        Returns:
            언어별 번역 통계
        """
        if "en" not in self.translations:
            return {}
        
        en_keys = self.get_all_keys(self.translations["en"])
        total_keys = len(en_keys)
        
        stats = {}
        for lang_code in SUPPORTED_LANGUAGES.keys():
            if lang_code not in self.translations:
                stats[lang_code] = {
                    "total_keys": 0,
                    "translated_keys": 0,
                    "missing_keys": total_keys,
                    "coverage": 0.0
                }
                continue
            
            lang_keys = self.get_all_keys(self.translations[lang_code])
            translated = len(lang_keys)
            missing = total_keys - translated
            coverage = (translated / total_keys * 100) if total_keys > 0 else 0
            
            stats[lang_code] = {
                "total_keys": total_keys,
                "translated_keys": translated,
                "missing_keys": missing,
                "coverage": round(coverage, 2)
            }
        
        return stats
    
    def generate_report(self) -> str:
        """번역 검증 리포트 생성"""
        report = []
        report.append("=" * 80)
        report.append("Translation Validation Report")
        report.append("=" * 80)
        report.append("")
        
        # 통계
        stats = self.get_translation_stats()
        report.append("📊 Translation Coverage:")
        report.append("-" * 80)
        report.append(f"{'Language':<15} {'Total':<10} {'Translated':<12} {'Missing':<10} {'Coverage':<10}")
        report.append("-" * 80)
        
        for lang_code, stat in stats.items():
            lang_name = SUPPORTED_LANGUAGES.get(lang_code, lang_code)
            coverage_icon = "✅" if stat["coverage"] == 100 else "⚠️" if stat["coverage"] >= 50 else "❌"
            report.append(
                f"{coverage_icon} {lang_name:<13} "
                f"{stat['total_keys']:<10} "
                f"{stat['translated_keys']:<12} "
                f"{stat['missing_keys']:<10} "
                f"{stat['coverage']}%"
            )
        
        report.append("")
        
        # 누락된 키
        missing = self.validate_completeness()
        if missing:
            report.append("❌ Missing Translation Keys:")
            report.append("-" * 80)
            for lang_code, keys in missing.items():
                lang_name = SUPPORTED_LANGUAGES.get(lang_code, lang_code)
                report.append(f"\n{lang_name} ({lang_code}): {len(keys)} keys missing")
                
                # 처음 10개만 표시
                for key in sorted(list(keys))[:10]:
                    report.append(f"  - {key}")
                
                if len(keys) > 10:
                    report.append(f"  ... and {len(keys) - 10} more")
        else:
            report.append("✅ All translations are complete!")
        
        report.append("")
        
        # 추가 키
        extra = self.validate_extra_keys()
        if extra:
            report.append("⚠️  Extra Keys (not in English):")
            report.append("-" * 80)
            for lang_code, keys in extra.items():
                lang_name = SUPPORTED_LANGUAGES.get(lang_code, lang_code)
                report.append(f"\n{lang_name} ({lang_code}): {len(keys)} extra keys")
                for key in sorted(list(keys))[:10]:
                    report.append(f"  - {key}")
                
                if len(keys) > 10:
                    report.append(f"  ... and {len(keys) - 10} more")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def export_missing_keys(self, output_dir: Path = None):
        """누락된 키를 파일로 내보내기"""
        if output_dir is None:
            output_dir = self.translations_dir.parent / "translation_reports"
        
        output_dir.mkdir(exist_ok=True)
        
        missing = self.validate_completeness()
        
        for lang_code, keys in missing.items():
            if not keys:
                continue
            
            output_file = output_dir / f"missing_{lang_code}.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"Missing translation keys for {lang_code}:\n")
                f.write(f"Total: {len(keys)} keys\n\n")
                for key in sorted(keys):
                    # 영어 값도 함께 출력
                    en_value = self._get_nested_value(self.translations["en"], key)
                    f.write(f"{key}\n")
                    if en_value:
                        f.write(f"  EN: {en_value}\n")
                    f.write("\n")
            
            print(f"✅ Exported missing keys to: {output_file}")
    
    def _get_nested_value(self, data: Dict, key: str):
        """중첩된 딕셔너리에서 값 가져오기"""
        keys = key.split(".")
        current = data
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None
        
        return current


def main():
    """메인 함수"""
    print("🔍 Starting translation validation...\n")
    
    validator = TranslationValidator()
    
    # 리포트 생성
    report = validator.generate_report()
    print(report)
    
    # 누락된 키 내보내기
    print("\n📝 Exporting missing keys...")
    validator.export_missing_keys()
    
    # 리포트 파일 저장
    report_dir = PROJECT_ROOT / "translation_reports"
    report_dir.mkdir(exist_ok=True)
    report_file = report_dir / "validation_report.txt"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ Full report saved to: {report_file}")


if __name__ == "__main__":
    main()
