import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'
import Assets from './pages/Assets'
import Disasters from './pages/Disasters'
import Analytics from './pages/Analytics'
import Weather from './pages/Weather'
import DemandAnalysis from './pages/DemandAnalysis'
import SupplyAnalysis from './pages/SupplyAnalysis'
import DigitalTwin from './pages/DigitalTwin'

function App() {
  return (
    <Router>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Home />} />
          <Route path="/assets" element={<Assets />} />
          <Route path="/disasters" element={<Disasters />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/weather" element={<Weather />} />
          <Route path="/demand-analysis/:assetId" element={<DemandAnalysis />} />
          <Route path="/supply-analysis/:assetId" element={<SupplyAnalysis />} />
          <Route path="/digital-twin/:assetId" element={<DigitalTwin />} />
        </Route>
      </Routes>
    </Router>
  )
}

export default App

