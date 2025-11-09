import React, { useMemo, useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Tabs,
  Tab,
  Grid,
  Card,
  CardContent,
  Slider,
  Box,
  Select,
  MenuItem,
  TextField,
  Button,
  Divider,
  Chip,
  Tooltip,
  IconButton,
  Switch,
  FormControlLabel,
  Container,
} from '@mui/material';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import DownloadOutlinedIcon from '@mui/icons-material/DownloadOutlined';
import SaveOutlinedIcon from '@mui/icons-material/SaveOutlined';
import CompareArrowsIcon from '@mui/icons-material/CompareArrows';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RTooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  Legend,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts';

// --- Utility helpers ---
const clamp = (n: number, min: number = 0, max: number = 100): number => 
  Math.min(Math.max(n, min), max);

const round = (n: number, d: number = 1): number => 
  Math.round(n * Math.pow(10, d)) / Math.pow(10, d);

const baseline = {
  demandTWh: 500, // total electricity demand
  co2Mt: 220, // baseline emissions (Mt)
  costPerMWh: 78, // $/MWh
  renewableShare: 42, // %
};

const years = Array.from({ length: 10 }, (_, i) => 2026 + i);

const defaultMix = {
  solar: 24,
  wind: 28,
  hydro: 10,
  fossil: 38,
};

const defaultParams = {
  gridEff: 92,
  storageEff: 85,
  carbonPrice: 50, // $/tCO2
  subsidy: 'Medium' as 'None' | 'Low' | 'Medium' | 'High',
  taxCredit: 10, // $/MWh
  industrialDemand: 100, // % of baseline
  transportElec: 35, // % electrification level
};

interface Mix {
  solar: number;
  wind: number;
  hydro: number;
  fossil: number;
}

interface Params {
  gridEff: number;
  storageEff: number;
  carbonPrice: number;
  subsidy: 'None' | 'Low' | 'Medium' | 'High';
  taxCredit: number;
  industrialDemand: number;
  transportElec: number;
}

interface KPI {
  demandTWh: number;
  co2Mt: number;
  costPerMWh: number;
  renewableShare: number;
  nMix: Mix;
}

interface Delta {
  demand: number;
  co2: number;
  cost: number;
  ren: number;
}

function normalizeMix(mix: Mix): Mix {
  const total = Object.values(mix).reduce((a, b) => a + b, 0);
  if (total === 0) return { ...defaultMix };
  const factor = 100 / total;
  const normalized = Object.fromEntries(
    Object.entries(mix).map(([k, v]) => [k, v * factor])
  ) as Mix;
  return normalized;
}

function useKpi(mix: Mix, params: Params): KPI {
  const nMix = normalizeMix(mix);
  return useMemo(() => {
    const renewablePct = nMix.solar + nMix.wind + nMix.hydro;
    // Simple modeled effects
    const effFactor = (params.gridEff / 100) * (params.storageEff / 100);

    // Demand scaling by industrial activity and transport electrification
    const demandScale =
      (params.industrialDemand / 100) * (1 + params.transportElec / 400);
    const demandTWh = (baseline.demandTWh * demandScale) / effFactor;

    // Emissions: proportional to fossil share, reduced by carbon price signal
    const priceSignal = 1 - clamp(params.carbonPrice / 400, 0, 0.6); // up to 60% reduction effect in fossil intensity
    const co2Mt =
      baseline.co2Mt * (nMix.fossil / defaultMix.fossil) * priceSignal * demandScale;

    // Cost model: renewables cheaper with subsidy & tax credit, storage/efficiency helps
    const subsidyLevel = { None: 0, Low: 0.5, Medium: 1, High: 1.6 }[params.subsidy] ?? 1;
    const creditEffect = clamp(params.taxCredit / 60, 0, 0.3); // up to 30% off
    const renewableCost = 60 * (1 - 0.15 * subsidyLevel - creditEffect);
    const fossilCost = 95 + params.carbonPrice * 0.25; // carbon price raises fossil cost
    const hydroCost = 50;

    const mixCost =
      (nMix.solar * renewableCost +
        nMix.wind * renewableCost +
        nMix.hydro * hydroCost +
        nMix.fossil * fossilCost) /
      100;

    const costPerMWh = round(mixCost * (1 - (effFactor - 0.8))); // efficiency improvement reduces cost

    return {
      demandTWh: round(demandTWh, 1),
      co2Mt: round(co2Mt, 1),
      costPerMWh: round(costPerMWh, 1),
      renewableShare: round(renewablePct, 1),
      nMix,
    };
  }, [mix, params]);
}

function kpiDelta(current: KPI): Delta {
  const del = (val: number, base: number) => round(((val - base) / base) * 100, 1);
  return {
    demand: del(current.demandTWh, baseline.demandTWh),
    co2: del(current.co2Mt, baseline.co2Mt),
    cost: del(current.costPerMWh, baseline.costPerMWh),
    ren: del(current.renewableShare, baseline.renewableShare),
  };
}

interface KpiCardProps {
  title: string;
  value: number;
  unit: string;
  delta: number;
}

function KpiCard({ title, value, unit, delta }: KpiCardProps) {
  const isGood = title.includes('CO₂') ? delta < 0 : title.includes('Cost') ? delta < 0 : title.includes('Renewable') ? delta > 0 : true;
  const color = isGood ? 'success.main' : 'error.main';
  const sign = delta > 0 ? '+' : '';
  
  return (
    <Card sx={{ borderRadius: 2, boxShadow: 2, transition: 'transform 0.2s', '&:hover': { transform: 'translateY(-2px)' } }}>
      <CardContent sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, color: 'text.secondary' }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 500 }}>
            {title}
          </Typography>
          <InfoOutlinedIcon fontSize="small" sx={{ color: 'text.secondary' }} />
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 1 }}>
          <Typography variant="h5" sx={{ fontWeight: 600 }}>
            {value}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {unit}
          </Typography>
        </Box>
        {delta !== undefined && (
          <Typography variant="body2" sx={{ color, mt: 1, fontWeight: 500 }}>
            {sign}{delta}% vs baseline
          </Typography>
        )}
      </CardContent>
    </Card>
  );
}

interface ControlSliderProps {
  label: string;
  value: number;
  setValue: (value: number) => void;
  min?: number;
  max?: number;
  step?: number;
  suffix?: string;
}

function ControlSlider({ label, value, setValue, min = 0, max = 100, step = 1, suffix = '%' }: ControlSliderProps) {
  return (
    <Box sx={{ py: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
        <Typography variant="body2" color="text.secondary">{label}</Typography>
        <Chip size="small" label={`${round(value, 1)}${suffix}`} />
      </Box>
      <Slider 
        value={value} 
        onChange={(_, v) => setValue(Number(v))} 
        min={min} 
        max={max} 
        step={step}
        valueLabelDisplay="auto"
      />
    </Box>
  );
}

// --- Main Component ---
const RealTimeAnalysis: React.FC = () => {
  const [tab, setTab] = useState(0);
  const [autoNormalize, setAutoNormalize] = useState(true);

  const [mix, setMix] = useState<Mix>(defaultMix);
  const [params, setParams] = useState<Params>(defaultParams);

  const computed = useKpi(mix, params);
  const delta = kpiDelta(computed);

  const displayMix = autoNormalize ? computed.nMix : mix;

  const timeSeries = useMemo(() => {
    // simple time projection: gradual improvements based on settings
    return years.map((y, i) => {
      const progress = i / (years.length - 1);
      const co2 = computed.co2Mt * (1 - progress * (computed.renewableShare / 200));
      const cost = computed.costPerMWh * (1 - progress * 0.08);
      const ren = computed.renewableShare * (1 + progress * 0.15);
      return {
        year: y,
        co2: round(co2, 1),
        cost: round(cost, 1),
        ren: round(Math.min(100, ren), 1),
        solar: round(displayMix.solar * (1 + progress * 0.25), 1),
        wind: round(displayMix.wind * (1 + progress * 0.25), 1),
        hydro: round(displayMix.hydro, 1),
        fossil: round(displayMix.fossil * (1 - progress * 0.4), 1),
      };
    });
  }, [computed, displayMix]);

  const saveSnapshot = () => {
    const payload = {
      ts: new Date().toISOString(),
      mix: normalizeMix(mix),
      params,
      kpi: computed,
    };
    localStorage.setItem('rtm_snapshot', JSON.stringify(payload));
    alert('Snapshot saved locally (rtm_snapshot)');
  };

  const exportCSV = () => {
    const headers = Object.keys(timeSeries[0]);
    const rows = timeSeries.map((r) => headers.map((h) => String(r[h as keyof typeof r])).join(','));
    const csv = [headers.join(','), ...rows].join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'real_time_analysis.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  const setMixField = (key: keyof Mix, val: number) =>
    setMix((m) => ({ ...m, [key]: clamp(Number(val)) }));

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'grey.50' }}>
      <AppBar position="sticky" elevation={0} sx={{ bgcolor: 'background.paper', borderBottom: 1, borderColor: 'divider' }}>
        <Toolbar sx={{ display: 'flex', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Box sx={{ width: 32, height: 32, borderRadius: 2, bgcolor: 'success.main', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <TrendingUpIcon sx={{ color: 'white', fontSize: 20 }} />
            </Box>
            <Box>
              <Typography variant="caption" sx={{ textTransform: 'uppercase', letterSpacing: 2, color: 'text.secondary' }}>
                Real-time
              </Typography>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Analysis Dashboard
              </Typography>
            </Box>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Tooltip title="Save snapshot">
              <IconButton onClick={saveSnapshot} size="small">
                <SaveOutlinedIcon />
              </IconButton>
            </Tooltip>
            <Button
              variant="outlined"
              size="small"
              startIcon={<DownloadOutlinedIcon />}
              onClick={exportCSV}
            >
              Export CSV
            </Button>
          </Box>
        </Toolbar>
        <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ px: 2 }}>
          <Tab label="Overview" />
          <Tab label="Scenario Control" />
          <Tab label="Results Dashboard" />
          <Tab label="Compare Scenarios" />
        </Tabs>
      </AppBar>

      {/* Overview */}
      {tab === 0 && (
        <Container maxWidth="xl" sx={{ py: 3 }}>
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} md={3}>
              <KpiCard title="Total Energy Demand" value={computed.demandTWh} unit="TWh" delta={delta.demand} />
            </Grid>
            <Grid item xs={12} md={3}>
              <KpiCard title="CO₂ Emissions" value={computed.co2Mt} unit="Mt" delta={delta.co2} />
            </Grid>
            <Grid item xs={12} md={3}>
              <KpiCard title="Cost per MWh" value={computed.costPerMWh} unit="$" delta={delta.cost} />
            </Grid>
            <Grid item xs={12} md={3}>
              <KpiCard title="Renewable Share" value={computed.renewableShare} unit="%" delta={delta.ren} />
            </Grid>
          </Grid>

          <Card sx={{ borderRadius: 2, boxShadow: 2, transition: 'transform 0.2s', '&:hover': { transform: 'translateY(-2px)' } }}>
            <CardContent>
              <Typography variant="subtitle1" sx={{ mb: 2, color: 'text.primary', fontWeight: 600 }}>Energy Mix Projection</Typography>
              <Box sx={{ width: '100%', height: 320 }}>
                <ResponsiveContainer>
                  <AreaChart data={timeSeries} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                    <defs>
                      <linearGradient id="solar" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#fbbf24" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#fbbf24" stopOpacity={0}/>
                      </linearGradient>
                      <linearGradient id="wind" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#60a5fa" stopOpacity={0.7}/>
                        <stop offset="95%" stopColor="#60a5fa" stopOpacity={0}/>
                      </linearGradient>
                      <linearGradient id="fossil" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#94a3b8" stopOpacity={0.7}/>
                        <stop offset="95%" stopColor="#94a3b8" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="year" />
                    <YAxis />
                    <RTooltip />
                    <Legend />
                    <Area type="monotone" dataKey="solar" stackId="1" stroke="#f59e0b" fill="url(#solar)" />
                    <Area type="monotone" dataKey="wind" stackId="1" stroke="#3b82f6" fill="url(#wind)" />
                    <Area type="monotone" dataKey="hydro" stackId="1" stroke="#06b6d4" fillOpacity={0.2} fill="#06b6d4" />
                    <Area type="monotone" dataKey="fossil" stackId="1" stroke="#64748b" fill="url(#fossil)" />
                  </AreaChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Container>
      )}

      {/* Scenario Control */}
      {tab === 1 && (
        <Container maxWidth="xl" sx={{ py: 3 }}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Card sx={{ borderRadius: 2, boxShadow: 2, transition: 'transform 0.2s', '&:hover': { transform: 'translateY(-2px)' } }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                    <Typography variant="subtitle1" sx={{ color: 'text.primary', fontWeight: 600 }}>Generation Mix</Typography>
                    <FormControlLabel 
                      control={<Switch checked={autoNormalize} onChange={(_, v) => setAutoNormalize(v)} />} 
                      label="Auto normalize" 
                    />
                  </Box>
                  {Object.entries(mix).map(([k, v]) => (
                    <ControlSlider 
                      key={k} 
                      label={k[0].toUpperCase() + k.slice(1)} 
                      value={v} 
                      setValue={(val) => setMixField(k as keyof Mix, val)} 
                    />
                  ))}
                  <Divider sx={{ my: 2 }} />
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    {Object.entries(displayMix).map(([k, v]) => (
                      <Chip key={k} label={`${k}: ${round(v, 1)}%`} size="small" />
                    ))}
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={4}>
              <Card sx={{ borderRadius: 2, boxShadow: 2, transition: 'transform 0.2s', '&:hover': { transform: 'translateY(-2px)' } }}>
                <CardContent>
                  <Typography variant="subtitle1" sx={{ color: 'text.primary', mb: 2, fontWeight: 600 }}>Efficiency Factors</Typography>
                  <ControlSlider label="Grid Efficiency" value={params.gridEff} setValue={(v) => setParams(p => ({ ...p, gridEff: v }))} />
                  <ControlSlider label="Storage Efficiency" value={params.storageEff} setValue={(v) => setParams(p => ({ ...p, storageEff: v }))} />
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="subtitle1" sx={{ color: 'text.primary', mb: 2, fontWeight: 600 }}>Demand Factors</Typography>
                  <ControlSlider label="Industrial Demand Level" value={params.industrialDemand} setValue={(v) => setParams(p => ({ ...p, industrialDemand: v }))} />
                  <ControlSlider label="Transport Electrification" value={params.transportElec} setValue={(v) => setParams(p => ({ ...p, transportElec: v }))} />
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={4}>
              <Card sx={{ borderRadius: 2, boxShadow: 2, transition: 'transform 0.2s', '&:hover': { transform: 'translateY(-2px)' } }}>
                <CardContent>
                  <Typography variant="subtitle1" sx={{ color: 'text.primary', mb: 2, fontWeight: 600 }}>Policy Levers</Typography>
                  <Box sx={{ py: 2 }}>
                    <Typography variant="body2" sx={{ color: 'text.secondary', mb: 1 }}>Carbon Price ($/tCO₂)</Typography>
                    <TextField 
                      size="small" 
                      fullWidth 
                      type="number" 
                      value={params.carbonPrice} 
                      onChange={(e) => setParams(p => ({ ...p, carbonPrice: Number(e.target.value) }))} 
                    />
                  </Box>
                  <Box sx={{ py: 2 }}>
                    <Typography variant="body2" sx={{ color: 'text.secondary', mb: 1 }}>Renewable Subsidy</Typography>
                    <Select 
                      size="small" 
                      fullWidth 
                      value={params.subsidy} 
                      onChange={(e) => setParams(p => ({ ...p, subsidy: e.target.value as Params['subsidy'] }))}
                    >
                      {['None', 'Low', 'Medium', 'High'].map((lvl) => (
                        <MenuItem key={lvl} value={lvl}>{lvl}</MenuItem>
                      ))}
                    </Select>
                  </Box>
                  <Box sx={{ py: 2 }}>
                    <Typography variant="body2" sx={{ color: 'text.secondary', mb: 1 }}>Tax Credit ($/MWh)</Typography>
                    <TextField 
                      size="small" 
                      fullWidth 
                      type="number" 
                      value={params.taxCredit} 
                      onChange={(e) => setParams(p => ({ ...p, taxCredit: Number(e.target.value) }))} 
                    />
                  </Box>
                  <Divider sx={{ my: 2 }} />
                  <Box sx={{ display: 'flex', gap: 2 }}>
                    <Button onClick={saveSnapshot} variant="contained" startIcon={<SaveOutlinedIcon />}>Save</Button>
                    <Button onClick={exportCSV} variant="outlined" startIcon={<DownloadOutlinedIcon />}>Export CSV</Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Container>
      )}

      {/* Results Dashboard */}
      {tab === 2 && (
        <Container maxWidth="xl" sx={{ py: 3 }}>
          <Grid container spacing={3} sx={{ mb: 3 }}>
            <Grid item xs={12} md={6}>
              <Card sx={{ borderRadius: 2, boxShadow: 2, height: '100%' }}>
                <CardContent sx={{ height: '100%' }}>
                  <Typography variant="subtitle1" sx={{ mb: 2, color: 'text.primary', fontWeight: 600 }}>CO₂ Emissions Trend</Typography>
                  <Box sx={{ width: '100%', height: 288 }}>
                    <ResponsiveContainer>
                      <LineChart data={timeSeries}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="year" />
                        <YAxis />
                        <RTooltip />
                        <Line type="monotone" dataKey="co2" stroke="#ef4444" strokeWidth={2} />
                      </LineChart>
                    </ResponsiveContainer>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card sx={{ borderRadius: 2, boxShadow: 2, height: '100%' }}>
                <CardContent sx={{ height: '100%' }}>
                  <Typography variant="subtitle1" sx={{ mb: 2, color: 'text.primary', fontWeight: 600 }}>System Cost ($/MWh)</Typography>
                  <Box sx={{ width: '100%', height: 288 }}>
                    <ResponsiveContainer>
                      <BarChart data={timeSeries}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="year" />
                        <YAxis />
                        <Legend />
                        <RTooltip />
                        <Bar dataKey="cost" fill="#0ea5e9" />
                      </BarChart>
                    </ResponsiveContainer>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card sx={{ borderRadius: 2, boxShadow: 2, height: '100%' }}>
                <CardContent sx={{ height: '100%' }}>
                  <Typography variant="subtitle1" sx={{ mb: 2, color: 'text.primary', fontWeight: 600 }}>Renewable vs Demand (Radar)</Typography>
                  <Box sx={{ width: '100%', height: 320 }}>
                    <ResponsiveContainer>
                      <RadarChart data={[
                        { key: 'Solar', v: displayMix.solar }, 
                        { key: 'Wind', v: displayMix.wind }, 
                        { key: 'Hydro', v: displayMix.hydro }, 
                        { key: 'Fossil', v: displayMix.fossil }
                      ]}>
                        <PolarGrid />
                        <PolarAngleAxis dataKey="key" />
                        <PolarRadiusAxis angle={30} domain={[0, 100]} />
                        <Radar name="Mix %" dataKey="v" stroke="#14b8a6" fill="#14b8a6" fillOpacity={0.3} />
                        <RTooltip />
                      </RadarChart>
                    </ResponsiveContainer>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card sx={{ borderRadius: 2, boxShadow: 2, height: '100%' }}>
                <CardContent sx={{ height: '100%', display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <Typography variant="subtitle1" sx={{ color: 'text.primary', fontWeight: 600 }}>AI Insight</Typography>
                  <Box sx={{ p: 2, bgcolor: 'success.50', border: 1, borderColor: 'success.200', borderRadius: 2 }}>
                    <Typography variant="body2" sx={{ color: 'text.primary' }}>
                      Your current adjustments yield a <strong>{Math.abs(delta.co2)}% {delta.co2 < 0 ? 'reduction' : 'increase'}</strong> in CO₂ and a <strong>{Math.abs(delta.cost)}% {delta.cost < 0 ? 'reduction' : 'increase'}</strong> in cost per MWh versus baseline.
                      Renewable share is <strong>{computed.renewableShare}%</strong>. Consider shifting <strong>+5% wind</strong> and <strong>-5% fossil</strong> to reach a 2030 target of <strong>≥55% renewables</strong> while keeping costs manageable.
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
                    <Button 
                      variant="outlined" 
                      onClick={() => setMix(m => ({ ...m, wind: clamp(m.wind + 5), fossil: clamp(m.fossil - 5) }))}
                    >
                      Apply Suggestion
                    </Button>
                    <Button 
                      variant="text" 
                      onClick={() => { setMix(defaultMix); setParams(defaultParams); }}
                    >
                      Reset to Baseline
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Container>
      )}

      {/* Compare Scenarios - placeholder */}
      {tab === 3 && (
        <Container maxWidth="lg" sx={{ py: 3 }}>
          <Card sx={{ borderRadius: 2, boxShadow: 2 }}>
            <CardContent sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <Typography variant="subtitle1" sx={{ color: 'text.primary' }}>Compare Scenarios</Typography>
              <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                This area will allow side-by-side comparison between saved snapshots. For now, use the Save button in Scenario Control and export CSV from Overview/Results.
              </Typography>
            </CardContent>
          </Card>
        </Container>
      )}

      <Box sx={{ maxWidth: 'xl', mx: 'auto', px: 3, pb: 5, pt: 3, textAlign: 'center' }}>
        <Divider sx={{ mb: 2 }} />
        <Typography variant="caption" sx={{ color: 'text.secondary' }}>
          Energy Transition Model · Real-time Analysis — Example implementation (MUI + Recharts)
        </Typography>
      </Box>
    </Box>
  );
};

export default RealTimeAnalysis;

