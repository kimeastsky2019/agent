# ETM React - Quick Start Guide

## 🚀 Get Running in 5 Minutes

### Prerequisites Check

```bash
docker --version    # Should be 20.10+
docker-compose --version  # Should be 2.0+
git --version      # Any recent version
```

### Step 1: Install

```bash
cd etm-react-service
chmod +x install.sh
./install.sh
```

Wait 5-10 minutes for installation to complete.

### Step 2: Access

Open browser: **http://localhost**

### Step 3: Create Scenario

1. Click **"Create New Scenario"**
2. Select **South Korea**
3. Choose **2050**
4. Click **"Create Scenario"**

### Step 4: Explore Dashboard

- Move sliders to adjust energy mix
- Watch metrics update in real-time
- See charts change dynamically

## 🎯 What You'll See

### Home Page
- Modern landing page
- Feature highlights
- Call-to-action buttons

### Scenario Builder
- Country dropdown
- Year selector
- Custom naming

### Dashboard
- 🎚️ Interactive sliders
- 📊 Live metrics
- 📈 Charts & graphs
- ⚡ Instant updates

## 🛠️ Common Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f react-frontend

# Check status
docker-compose ps

# Restart specific service
docker-compose restart react-frontend
```

## 💡 First Steps

### 1. Explore the Interface
- Navigate between pages using top menu
- Click through different sections
- Get familiar with the layout

### 2. Create a Scenario
- Try different countries
- Experiment with different years
- Give meaningful names

### 3. Adjust Energy Mix
- Move Solar PV slider
- Adjust Wind capacity
- Change Nuclear plants
- Watch results update live!

### 4. Analyze Results
- Check CO2 emissions
- Monitor renewable percentage
- Review total costs
- Compare present vs future

## 📊 Understanding the Dashboard

### Input Controls (Left Side)
- **Solar PV**: 0-150 GW
- **Wind Offshore**: 0-100 GW
- **Nuclear Plants**: 0-30 units

### Key Metrics (Top Right)
- **CO2 Emissions**: In Megatons
- **Renewable Share**: Percentage
- **Total Cost**: In billion EUR

### Visualizations (Bottom)
- **Pie Chart**: Energy mix breakdown
- **Bar Chart**: CO2 comparison

## 🎨 UI Features

### Material Design
- Clean, modern interface
- Consistent design language
- Professional appearance

### Responsive Layout
- Works on desktop
- Adapts to tablets
- Mobile-friendly

### Real-time Updates
- No page refreshes needed
- Instant feedback
- Smooth transitions

## 🔧 Customization Tips

### Change Theme Colors
Edit `etm-react-frontend/src/App.tsx`:
```typescript
primary: { main: '#YOUR_COLOR' }
```

### Add New Metrics
Edit `etm-react-frontend/src/pages/Dashboard.tsx`:
```typescript
fetchResults(['your_metric_key'])
```

### Modify Sliders
Adjust min/max values in Dashboard component.

## 🆘 Quick Troubleshooting

### App Not Loading?
```bash
docker-compose logs react-frontend
# Look for errors in output
```

### API Not Responding?
```bash
docker-compose logs etengine
# Check if ETEngine is running
```

### Port Conflicts?
Change ports in `docker-compose.yml`:
```yaml
ports:
  - "3010:3000"  # New port
```

### Reset Everything?
```bash
docker-compose down -v
./install.sh
```

## 📱 Mobile Access

The app works on mobile! Just open:
`http://YOUR_COMPUTER_IP:80` on your phone.

## 🎓 Learning Path

### Day 1: Basics
- [x] Install and access
- [x] Create scenario
- [x] Explore dashboard
- [x] Adjust sliders

### Day 2: Understanding
- [x] Learn about metrics
- [x] Interpret charts
- [x] Compare scenarios
- [x] Export results

### Week 1: Advanced
- [x] Customize interface
- [x] Add new features
- [x] Integrate APIs
- [x] Deploy to production

## 💡 Pro Tips

1. **Save Your Work**: Note scenario IDs for later
2. **Start Simple**: Begin with small changes
3. **Compare**: Create multiple scenarios
4. **Document**: Keep notes on assumptions
5. **Share**: Send links to team members

## 🔗 Useful Links

- **Main App**: http://localhost
- **React Direct**: http://localhost:3000
- **API Docs**: http://localhost:3001/api/v3

## 📞 Need Help?

1. Check logs: `docker-compose logs -f`
2. Read full README.md
3. Contact: donghokim@gnginternational.com

## ✅ Success Checklist

After 5 minutes, you should have:
- [x] Services running
- [x] Browser opened to http://localhost
- [x] Created your first scenario
- [x] Adjusted energy sliders
- [x] Seen charts update

**Congratulations! You're ready to model energy transitions! ⚡🌱**

---

## 🎯 Next: What to Do?

1. **Experiment**: Try different energy mixes
2. **Learn**: Read full documentation
3. **Customize**: Change colors and layout
4. **Integrate**: Connect SolarGuard AI
5. **Share**: Show to your team

**Happy modeling!**
