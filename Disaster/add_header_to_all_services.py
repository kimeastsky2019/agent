import os
import re
from pathlib import Path

# 헤더 HTML
header_html = '''
    <nav class="top-nav" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px 20px; color: white; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        <div style="display: flex; align-items: center; gap: 20px;">
            <a href="/eop" style="color: white; text-decoration: none; font-weight: 600; font-size: 1.2em;">🏠 Energy Orchestrator Platform</a>
            <a href="/da" style="color: white; text-decoration: none;">⚡ 수요 분석</a>
            <a href="/sa" style="color: white; text-decoration: none;">🔋 공급 분석</a>
            <a href="/dtwin" style="color: white; text-decoration: none;">🏫 디지털 트윈</a>
            <a href="/disaster" style="color: white; text-decoration: none;">🚨 재난 관리</a>
        </div>
        <div style="display: flex; align-items: center; gap: 15px;">
            <select id="language-selector" onchange="changeLanguage(this.value)" style="padding: 5px 10px; border-radius: 5px; border: none; background: white; color: #333;">
                <option value="ko">한국어</option>
                <option value="en">English</option>
                <option value="ja">日本語</option>
            </select>
        </div>
    </nav>
'''

# 다국어 지원 스크립트
i18n_script = '''
    <script>
        let currentLang = localStorage.getItem('language') || 'ko';
        let translations = {};
        
        async function loadTranslations(lang) {
            try {
                const response = await fetch(`/api/translations?lang=${lang}`);
                const data = await response.json();
                translations = data.translations || {};
                currentLang = lang;
                localStorage.setItem('language', lang);
                applyTranslations();
            } catch (error) {
                console.error('Failed to load translations:', error);
            }
        }
        
        function applyTranslations() {
            document.querySelectorAll('[data-i18n]').forEach(el => {
                const key = el.getAttribute('data-i18n');
                const translation = getNestedTranslation(translations, key);
                if (translation) {
                    if (el.tagName === 'INPUT' && el.type === 'placeholder') {
                        el.placeholder = translation;
                    } else {
                        el.textContent = translation;
                    }
                }
            });
        }
        
        function getNestedTranslation(obj, path) {
            return path.split('.').reduce((o, p) => o && o[p], obj);
        }
        
        function changeLanguage(lang) {
            loadTranslations(lang);
        }
        
        loadTranslations(currentLang);
    </script>
'''

# HTML 파일 찾기
html_files = []
for root, dirs, files in os.walk('.'):
    # node_modules, venv, __pycache__ 제외
    dirs[:] = [d for d in dirs if d not in ['node_modules', 'venv', '__pycache__', '.git']]
    for file in files:
        if file.endswith('.html'):
            html_files.append(os.path.join(root, file))

# 서비스별 HTML 파일 필터링
service_files = {
    'dtwin': [f for f in html_files if 'digitaltwin' in f.lower() or 'dtwin' in f.lower()],
    'weather': [f for f in html_files if 'weather' in f.lower()],
    'ontology': [f for f in html_files if 'ontology' in f.lower()],
    'ibs': [f for f in html_files if 'image_broadcasting' in f.lower() or 'ibs' in f.lower()],
    'disaster': [f for f in html_files if 'disaster' in f.lower() and 'disaster_p' in f]
}

# 각 서비스의 메인 HTML 파일 찾기
main_files = {}
for service, files in service_files.items():
    if files:
        # public/index.html 또는 build/index.html 우선
        main_file = next((f for f in files if 'public/index.html' in f or 'build/index.html' in f), None)
        if not main_file:
            # index.html 우선
            main_file = next((f for f in files if 'index.html' in f), None)
        if not main_file:
            # 첫 번째 파일
            main_file = files[0]
        main_files[service] = main_file

# 헤더 추가
for service, file_path in main_files.items():
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html = f.read()
        
        # 이미 헤더가 있으면 스킵
        if 'top-nav' in html:
            print(f'{file_path}: 이미 헤더가 있습니다.')
            continue
        
        # head 태그에 스크립트 추가
        if '</head>' in html:
            html = html.replace('</head>', i18n_script + '</head>')
        
        # body 태그 다음에 헤더 추가
        if '<body>' in html:
            html = html.replace('<body>', '<body>' + header_html)
        
        # 백업
        backup_path = file_path + '.backup'
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        # 저장
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f'{file_path}: 헤더와 다국어 지원이 추가되었습니다.')
    except Exception as e:
        print(f'{file_path}: 오류 - {e}')

print('\n완료!')
