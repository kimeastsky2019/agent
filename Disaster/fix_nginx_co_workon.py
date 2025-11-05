import re

# Read current Nginx config
with open('/etc/nginx/sites-available/agent.gngmeta.com', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace /co-workon location
pattern = r'location /co-workon \{.*?\n    \}'
new_location = '''    location /co-workon {
        rewrite ^/co-workon/?(.*)$ /$1 break;
        proxy_pass http://localhost:5010;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }'''

content = re.sub(pattern, new_location, content, flags=re.DOTALL)

# Write back
with open('/etc/nginx/sites-available/agent.gngmeta.com', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Updated /co-workon location with rewrite')





