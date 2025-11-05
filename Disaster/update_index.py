import re

# Read current index.html
with open('/var/www/html/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add assets modal and scripts before closing body tag
assets_modal = '''    <!-- Assets Management Modal -->
    <div id="assetsModal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000;">
        <div style="background: white; border-radius: 16px; padding: 40px; max-width: 500px; margin: 50px auto; position: relative;">
            <div style="margin-bottom: 30px;">
                <h2 style="color: #667eea; font-size: 1.8em;">자산 추가</h2>
            </div>
            <form id="assetForm">
                <div style="margin-bottom: 25px;">
                    <label style="display: block; margin-bottom: 10px; color: #333; font-weight: 600;">이름</label>
                    <input type="text" id="assetName" name="name" required style="width: 100%; padding: 14px; border: 2px solid #e0e0e0; border-radius: 10px; font-size: 1em;">
                </div>
                <div style="margin-bottom: 25px;">
                    <label style="display: block; margin-bottom: 10px; color: #333; font-weight: 600;">부문 선택</label>
                    <select id="assetType" name="type" required style="width: 100%; padding: 14px; border: 2px solid #e0e0e0; border-radius: 10px; font-size: 1em;">
                        <option value="">선택하세요</option>
                        <option value="demand">수요 부문</option>
                        <option value="supply">공급 부문</option>
                        <option value="video">영상 부문</option>
                    </select>
                </div>
                <div style="margin-bottom: 25px;">
                    <label style="display: block; margin-bottom: 10px; color: #333; font-weight: 600;">API URL</label>
                    <input type="text" id="assetApiUrl" name="api_url" placeholder="https://api.example.com" required style="width: 100%; padding: 14px; border: 2px solid #e0e0e0; border-radius: 10px; font-size: 1em;">
                </div>
                <div style="display: flex; gap: 10px; margin-top: 30px;">
                    <button type="submit" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 14px 28px; border: none; border-radius: 10px; font-size: 1em; font-weight: 600; cursor: pointer; flex: 1;">추가</button>
                    <button type="button" onclick="closeAssetsModal()" style="background: #e0e0e0; color: #333; padding: 14px 28px; border: none; border-radius: 10px; font-size: 1em; cursor: pointer; flex: 1;">취소</button>
                </div>
            </form>
        </div>
    </div>
    
    <script>
        // Assets management functions
        function openAssetsModal() {
            document.getElementById("assetsModal").style.display = "block";
        }
        
        function closeAssetsModal() {
            document.getElementById("assetsModal").style.display = "none";
            document.getElementById("assetForm").reset();
        }
        
        // Load assets and create cards
        async function loadAssets() {
            try {
                const response = await fetch("/assets/api/assets");
                const result = await response.json();
                if (result.success && result.data) {
                    const servicesGrid = document.querySelector(".services-grid");
                    if (!servicesGrid) return;
                    
                    // Clear existing dynamic cards
                    const existingCards = servicesGrid.querySelectorAll("[data-asset-id]");
                    existingCards.forEach(card => card.remove());
                    
                    // Add asset cards
                    result.data.forEach(asset => {
                        const card = createAssetCard(asset);
                        servicesGrid.appendChild(card);
                    });
                }
            } catch (err) {
                console.error("Failed to load assets:", err);
            }
        }
        
        function createAssetCard(asset) {
            const card = document.createElement("a");
            card.href = asset.service_url;
            card.className = "service-card";
            card.setAttribute("data-asset-id", asset.id);
            
            const icons = {
                "demand": "📊",
                "supply": "⚡",
                "video": "📡"
            };
            
            const titles = {
                "demand": "Energy Demand",
                "supply": "Energy Supply",
                "video": "Image Broadcasting Service"
            };
            
            card.innerHTML = `
                <span class="service-icon">${icons[asset.type] || "📦"}</span>
                <div class="service-title">${asset.name}</div>
                <div class="service-description">${titles[asset.type] || "자산 서비스"}</div>
                <div class="service-path">${asset.service_url}</div>
            `;
            
            return card;
        }
        
        // Handle asset form submission
        document.addEventListener("DOMContentLoaded", function() {
            const assetForm = document.getElementById("assetForm");
            if (assetForm) {
                assetForm.addEventListener("submit", async (e) => {
                    e.preventDefault();
                    const formData = new FormData(e.target);
                    const data = {
                        name: formData.get("name"),
                        type: formData.get("type"),
                        api_url: formData.get("api_url")
                    };
                    
                    try {
                        const response = await fetch("/assets/api/assets", {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            credentials: "same-origin",
                            body: JSON.stringify(data)
                        });
                        
                        const result = await response.json();
                        if (result.success) {
                            closeAssetsModal();
                            loadAssets(); // Reload assets
                            alert("자산이 추가되었습니다!");
                        } else {
                            alert("오류: " + (result.error || "알 수 없는 오류"));
                        }
                    } catch (err) {
                        alert("오류: " + err.message);
                    }
                });
            }
            
            // Load assets on page load
            loadAssets();
        });
        
        window.onclick = function(event) {
            const modal = document.getElementById("assetsModal");
            if (event.target == modal) {
                closeAssetsModal();
            }
        }
    </script>'''

# Insert before closing body tag
if '</body>' in content:
    content = content.replace('</body>', assets_modal + '</body>')
    print('✅ Added assets modal and scripts')
else:
    content += assets_modal
    print('✅ Added assets modal and scripts at end')

# Update assets link to open modal
content = content.replace('href="/assets"', 'href="/assets" onclick="event.preventDefault(); openAssetsModal(); return false;" style="cursor: pointer;"')

# Write back
with open('/var/www/html/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Updated index.html with assets management')

