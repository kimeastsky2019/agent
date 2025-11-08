# ETM React - Modern Energy Transition Model

Modern React-based frontend for the Energy Transition Model with Material-UI design and real-time visualizations.

## 🚀 Key Features

### Modern Technology Stack
- ⚛️ **React 18** with TypeScript
- 🎨 **Material-UI (MUI)** for beautiful, responsive design
- 📊 **Recharts** for interactive data visualizations
- 🔄 **Vite** for lightning-fast development
- 🏗️ **Context API** for state management
- 🔌 **Axios** for API communication

### User Experience
- 🎯 Intuitive drag-and-drop interface
- 📱 Fully responsive design (mobile, tablet, desktop)
- ⚡ Real-time scenario updates
- 📈 Interactive charts and visualizations
- 🌐 Multi-language support ready
- ♿ Accessible (WCAG 2.1 compliant)

### Integration
- 🔗 RESTful API integration with ETEngine
- 🤖 Ready for SolarGuard AI integration
- 🔋 NanoGrid AI MCP compatible
- 📡 WebSocket support for real-time updates

## 📋 Architecture

```
┌─────────────┐
│   Nginx     │  ← http://localhost (Port 80)
└──────┬──────┘
       │
   ┌───┴────┬─────────────┐
   │        │             │
┌──▼───┐ ┌─▼────┐    ┌──▼─────┐
│React │ │ETEngine│   │Redis  │
│:3000 │ │:3001  │   │:6379  │
└──────┘ └───┬───┘   └───────┘
             │
        ┌────▼────┐
        │PostgreSQL│
        │  :5432   │
        └──────────┘
```

## 💻 System Requirements

- **Docker**: 20.10 or higher
- **Docker Compose**: 2.0 or higher
- **Git**: Latest version
- **RAM**: Minimum 8GB
- **Disk**: 20GB free space
- **Browser**: Chrome, Firefox, Safari, Edge (latest versions)

## 🚀 Quick Start

### 1. Clone and Install

```bash
# Extract or clone this repository
cd etm-react-service

# Make install script executable
chmod +x install.sh

# Run installation
./install.sh
```

### 2. Access Application

Open your browser and go to: **http://localhost**

### 3. Create Your First Scenario

1. Click "Create New Scenario"
2. Select country (e.g., South Korea)
3. Choose target year (e.g., 2050)
4. Adjust energy mix with sliders
5. View real-time results!

## 📂 Project Structure

```
etm-react-service/
├── etm-react-frontend/         # React application
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   │   └── Layout.tsx      # App layout with navigation
│   │   ├── contexts/           # React Context for state
│   │   │   └── ScenarioContext.tsx
│   │   ├── pages/              # Page components
│   │   │   ├── Home.tsx        # Landing page
│   │   │   ├── ScenarioBuilder.tsx
│   │   │   └── Dashboard.tsx   # Main dashboard
│   │   ├── services/           # API services
│   │   │   └── api.ts          # ETEngine API client
│   │   ├── App.tsx             # Main app component
│   │   └── main.tsx            # Entry point
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
├── etengine/                   # Cloned from GitHub
├── etsource/                   # Cloned from GitHub
├── docker-compose.yml
├── nginx.conf
└── install.sh
```

## 🎨 Key Components

### Home Page
- Hero section with CTAs
- Feature showcase
- Quick start guide

### Scenario Builder
- Country/region selection
- Target year picker
- Custom scenario naming
- Form validation

### Dashboard
- **Input Controls**: Interactive sliders for energy mix
- **Key Metrics**: CO2, renewables, costs
- **Pie Chart**: Energy mix distribution
- **Bar Chart**: CO2 comparison (present vs future)
- **Real-time Updates**: Instant recalculation

## 🔧 Development

### Local Development

```bash
# Start all services
docker-compose up -d

# View React logs
docker-compose logs -f react-frontend

# View API logs
docker-compose logs -f etengine

# Stop services
docker-compose down
```

### Development Without Docker

```bash
# Start ETEngine (in one terminal)
cd etengine
bundle install
bundle exec rails server -p 3001

# Start React (in another terminal)
cd etm-react-frontend
npm install
npm run dev
```

### Hot Reload

The React app supports hot module replacement (HMR). Changes to source files will automatically reload in the browser.

## 🔌 API Integration

The React app communicates with ETEngine via the API client:

```typescript
import apiClient from './services/api';

// Create scenario
const scenario = await apiClient.createScenario({
  area_code: 'kr',
  end_year: 2050,
  title: 'My Scenario'
});

// Update inputs
await apiClient.updateScenario(scenario.id, {
  'capacity_of_energy_power_solar_pv': 100000
});

// Get results
const co2 = await apiClient.getGQuery(
  scenario.id,
  'co2_emissions_total'
);
```

## 📊 Available Visualizations

### Current Implementations
- **Pie Chart**: Energy mix distribution
- **Bar Chart**: CO2 emissions comparison
- **Metric Cards**: Key performance indicators

### Easy to Add
- Line charts for trends over time
- Area charts for stacked energy sources
- Gauge charts for progress indicators
- Map visualizations for regional data

## 🎨 Customization

### Theme Customization

Edit `src/App.tsx`:

```typescript
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2', // Your brand color
    },
    secondary: {
      main: '#4caf50',
    },
  },
});
```

### Adding New Pages

1. Create page component in `src/pages/`
2. Add route in `src/App.tsx`
3. Add navigation button in `src/components/Layout.tsx`

### Adding New Charts

```typescript
import { LineChart, Line } from 'recharts';

<ResponsiveContainer width="100%" height={300}>
  <LineChart data={yourData}>
    <Line type="monotone" dataKey="value" stroke="#8884d8" />
  </LineChart>
</ResponsiveContainer>
```

## 🔐 Environment Variables

### Development
All defaults are configured for local development.

### Production
Create `.env.production`:

```bash
VITE_API_URL=https://your-api.com
VITE_APP_TITLE=Energy Transition Model
```

## 🚢 Production Deployment

### Build for Production

```bash
cd etm-react-frontend
npm run build
```

This creates an optimized build in `dist/` folder.

### Docker Production Build

Create `Dockerfile.prod`:

```dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 🧪 Testing

```bash
# Add testing library
npm install --save-dev @testing-library/react @testing-library/jest-dom vitest

# Run tests
npm test
```

## 📱 Mobile Support

The app is fully responsive and works on:
- 📱 Mobile phones (320px+)
- 📱 Tablets (768px+)
- 💻 Laptops (1024px+)
- 🖥️ Desktops (1440px+)

## ♿ Accessibility

- ARIA labels on all interactive elements
- Keyboard navigation support
- High contrast mode compatible
- Screen reader friendly

## 🌍 Internationalization

Ready for i18n:

```bash
npm install react-i18next i18next

# Add translations in src/i18n/
```

## 🔄 Updates

```bash
# Update dependencies
npm update

# Rebuild Docker images
docker-compose build --no-cache

# Restart services
docker-compose up -d
```

## 🆘 Troubleshooting

### Port Already in Use
```bash
# Change port in docker-compose.yml
ports:
  - "3010:3000"  # Use 3010 instead
```

### React App Not Loading
```bash
# Check logs
docker-compose logs -f react-frontend

# Rebuild
docker-compose build react-frontend
docker-compose up -d react-frontend
```

### API Connection Issues
```bash
# Verify ETEngine is running
docker-compose ps etengine

# Check API health
curl http://localhost:3001/api/v3
```

## 📚 Learning Resources

- [React Documentation](https://react.dev/)
- [Material-UI Components](https://mui.com/material-ui/)
- [Recharts Examples](https://recharts.org/en-US/examples)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Vite Guide](https://vitejs.dev/guide/)

## 🤝 GnG International Integration

### SolarGuard AI Integration

```typescript
// Add to src/services/solarguard.ts
export const fetchSolarForecast = async () => {
  const response = await fetch('YOUR_SOLARGUARD_API');
  return response.json();
};

// Use in Dashboard
const forecast = await fetchSolarForecast();
await updateInputs({
  solar_capacity: forecast.predicted_capacity
});
```

### NanoGrid AI Integration

```typescript
// Real-time grid status updates
const wsConnection = new WebSocket('ws://nanogrid-api');
wsConnection.onmessage = (event) => {
  const gridData = JSON.parse(event.data);
  updateDashboard(gridData);
};
```

## 📄 License

MIT License - GnG International

## 🎯 Advantages Over Rails Frontend

✅ **Faster**: Vite dev server starts in seconds
✅ **Modern**: Latest React, TypeScript, Material-UI
✅ **Responsive**: Mobile-first design
✅ **Interactive**: Real-time updates without page refresh
✅ **Customizable**: Easy to theme and extend
✅ **Developer Experience**: Hot reload, TypeScript autocomplete
✅ **Lighter**: No Ruby dependencies for frontend
✅ **Scalable**: Component-based architecture

## 🚀 Next Steps

1. ✅ Install and run locally
2. ✅ Create your first scenario
3. ✅ Explore the dashboard
4. 📝 Customize theme and branding
5. 🔌 Integrate with SolarGuard AI
6. 🚢 Deploy to production

---

**Developed for GnG International**  
**Version**: 2.0.0 (React)  
**Date**: 2025-11-07

**Welcome to the future of energy modeling! ⚡🌱**
