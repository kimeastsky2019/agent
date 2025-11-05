#!/usr/bin/env python3
"""Nginx 설정 파일에서 /assets location 블록 수정"""

# Nginx 설정 파일 읽기
with open('/etc/nginx/sites-available/agent.gngmeta.com', 'r') as f:
    lines = f.readlines()

# /assets 블록 찾기 및 수정
new_lines = []
i = 0
while i < len(lines):
    if 'location /assets {' in lines[i]:
        # 올바른 블록으로 교체
        new_lines.append('    location /assets {\n')
        new_lines.append('        proxy_pass http://localhost:5009;\n')
        new_lines.append('        proxy_set_header Host $host;\n')
        new_lines.append('        proxy_set_header X-Real-IP $remote_addr;\n')
        new_lines.append('        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n')
        new_lines.append('        proxy_set_header X-Forwarded-Proto $scheme;\n')
        new_lines.append('        proxy_redirect off;\n')
        new_lines.append('        rewrite ^/assets/(.*)$ /$1 break;\n')
        new_lines.append('    }\n')
        # 기존 블록 건너뛰기
        i += 1
        while i < len(lines) and not lines[i].strip() == '}':
            i += 1
        i += 1  # } 건너뛰기
    else:
        new_lines.append(lines[i])
        i += 1

# 파일 저장
with open('/etc/nginx/sites-available/agent.gngmeta.com', 'w') as f:
    f.writelines(new_lines)

print('✅ Nginx 설정 수정 완료')





