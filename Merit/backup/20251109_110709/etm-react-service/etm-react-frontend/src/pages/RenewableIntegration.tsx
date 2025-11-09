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
import LightbulbOutlinedIcon from '@mui/icons-material/LightbulbOutlined';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip as RTooltip,
  AreaChart,
  Area,
  Legend,
  BarChart,
  Bar,
  ScatterChart,
  Scatter,
  ZAxis,
} from 'recharts';

// ----------------- Helpers & Baselines -----------------
const clamp = (n: number, min: number = 0, max: number = 100): number => 
  Math.min(Math.max(Number(n), min), max);

const round = (n: number, d: number = 1): number => 
  Math.round(n * Math.pow(10, d)) / Math.pow(10, d);

const years = Array.from({ length: 10 }, (_, i) => 2026 + i);

const baseline = {
  demandTWh: 500, // yearly electricity demand
  peakGW: 85, // system peak demand
  co2Mt: 220,
};

const defaultParams = {
  solarCapGW: 40,
  windCapGW: 35,
  hydroCapGW: 12,
  storageCapGW: 10,
  storageHours: 4,
  curtailmentCap: 12, // % allowed curtailment before penalties
  gridLimitGW: 110, // max instantaneous send-out (transmission)
  reserveMargin: 15, // %
};

const cfDefault = {
  solar: 20, // % capacity factor
  wind: 35,
  hydro: 45,
};

const lcoeDefault = {
  solar: 42, // $/MWh
  wind: 55,
  hydro: 60,
  storage: 120, // equivalent LCOS
  fossil: 95,
};

// perfect synthetic hourly profile for a typical day (normalized 0-1)
const hourlyProfile = Array.from({ length: 24 }, (_, h) => {
  const solar = Math.max(0, Math.sin((Math.PI * (h - 6)) / 12)); // day curve
  const wind = 0.55 + 0.35 * Math.sin((2 * Math.PI * (h + 4)) / 24); // breezy nights
  const demand = 0.7 + 0.3 * Math.sin((2 * Math.PI * (h - 14)) / 24); // evening peak
  return { hour: h, solar, wind, demand };
});

interface Params {
  solarCapGW: number;
  windCapGW: number;
  hydroCapGW: number;
  storageCapGW: number;
  storageHours: number;
  curtailmentCap: number;
  gridLimitGW: number;
  reserveMargin: number;
}

interface CF {
  solar: number;
  wind: number;
  hydro: number;
}

interface LCOE {
  solar: number;
  wind: number;
  hydro: number;
  storage: number;
  fossil: number;
}

interface KPI {
  renewableTWh: number;
  solarTWh: number;
  windTWh: number;
  hydroTWh: number;
  storageEnergyTWh: number;
  systemLCOE: number;
  curtailmentPct: number;
  adequacyOK: boolean;
  lolh: number;
}

interface HourlyData {
  hour: number;
  demandGW: number;
  genGW: number;
  deficitGW: number;
}

interface SeriesData {
  year: number;
  renTWh: number;
  cost: number;
  co2Avoided: number;
}

interface IntegrationResult {
  kpi: KPI;
  hourly: HourlyData[];
  series: SeriesData[];
}

function useIntegration(params: Params, cf: CF, lcoe: LCOE): IntegrationResult {
  return useMemo(() => {
    const toTWh = (gw: number, cfPct: number) => round((gw * 8760 * (cfPct / 100)) / 1000, 2);

    const solarTWh = toTWh(params.solarCapGW, cf.solar);
    const windTWh = toTWh(params.windCapGW, cf.wind);
    const hydroTWh = toTWh(params.hydroCapGW, cf.hydro);

    const renewableTWh = solarTWh + windTWh + hydroTWh;
    const storageEnergyTWh = round((params.storageCapGW * params.storageHours) / 1000 * 365 * 0.2, 2); // assume avg 0.2 cycle/day

    const surplusPct = clamp((renewableTWh / baseline.demandTWh) * 100 - 100, -100, 100);
    const curtailmentPct = Math.max(0, surplusPct);

    const curtailmentPenalty = curtailmentPct > params.curtailmentCap ? (curtailmentPct - params.curtailmentCap) * 0.15 : 0; // $/MWh adder to LCOE equivalent

    // Simple blended LCOE (weighted by energy share) + curtailment/storage effects
    const weightedCost =
      (solarTWh * lcoe.solar + windTWh * lcoe.wind + hydroTWh * lcoe.hydro) /
      Math.max(1, renewableTWh);

    const storageAdj = lcoe.storage * (params.storageCapGW > 0 ? 0.06 : 0); // light cost adder if storage present
    const lcoeSystem = round(weightedCost + storageAdj + curtailmentPenalty, 1);

    // Hourly adequacy / peak check (very simplified)
    const hourly: HourlyData[] = hourlyProfile.map((p) => {
      const solarGW = params.solarCapGW * p.solar;
      const windGW = params.windCapGW * (0.5 + 0.5 * p.wind); // normalize 0-1
      const hydroGW = Math.min(params.hydroCapGW * 0.7, params.hydroCapGW); // constant portion available
      const rawGen = solarGW + windGW + hydroGW;

      // storage dispatch: charge if surplus, discharge if deficit, respecting limits
      let net = rawGen;
      const peak = baseline.peakGW * (0.8 + 0.4 * p.demand);
      const deficit = Math.max(0, peak - net);
      const discharge = Math.min(deficit, params.storageCapGW);
      net += discharge;

      const gridLimited = Math.min(net, params.gridLimitGW);
      return {
        hour: p.hour,
        demandGW: round(peak, 1),
        genGW: round(gridLimited, 1),
        deficitGW: round(Math.max(0, peak - gridLimited), 1),
      };
    });

    const lossOfLoadHours = hourly.filter((h) => h.deficitGW > 0).length;
    const adequacyOK = lossOfLoadHours <= 1 && Math.max(...hourly.map((h) => h.genGW)) <= params.gridLimitGW;

    // Ten-year projection with gentle growth & improvements
    const series: SeriesData[] = years.map((y, i) => {
      const growth = 1 + i * 0.02; // 2%/yr growth
      const co2Avoided = round((renewableTWh * 0.4) * i * 0.1, 2); // synthetic cumulative impact
      return {
        year: y,
        renTWh: round(renewableTWh * growth, 1),
        cost: round(lcoeSystem * (1 - i * 0.02), 1),
        co2Avoided,
      };
    });

    return {
      kpi: {
        renewableTWh: round(renewableTWh, 1),
        solarTWh,
        windTWh,
        hydroTWh,
        storageEnergyTWh,
        systemLCOE: lcoeSystem,
        curtailmentPct: round(curtailmentPct, 1),
        adequacyOK,
        lolh: lossOfLoadHours,
      },
      hourly,
      series,
    };
  }, [params, cf, lcoe]);
}

interface KpiProps {
  label: string;
  value: string | number;
  unit: string;
  good?: boolean;
}

function Kpi({ label, value, unit, good }: KpiProps) {
  const color = good === undefined ? 'text.primary' : good ? 'success.main' : 'error.main';
  
  return (
    <Card sx={{ borderRadius: 2, boxShadow: 2, transition: 'transform 0.2s', '&:hover': { transform: 'translateY(-2px)' } }}>
      <CardContent sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
        <Typography variant="subtitle2" color="text.secondary" sx={{ fontWeight: 500 }}>{label}</Typography>
        <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 1 }}>
          <Typography variant="h5" sx={{ fontWeight: 600, color }}>
            {value}
          </Typography>
          <Typography variant="body2" color="text.secondary">{unit}</Typography>
        </Box>
      </CardContent>
    </Card>
  );
}

// --- Main Component ---
const RenewableIntegration: React.FC = () => {
  const [tab, setTab] = useState(0);
  const [params, setParams] = useState<Params>(defaultParams);
  const [cf, setCf] = useState<CF>(cfDefault);
  const [lcoe, setLcoe] = useState<LCOE>(lcoeDefault);
  const [autoRebalance, setAutoRebalance] = useState(true);

  const { kpi, hourly, series } = useIntegration(params, cf, lcoe);

  const totalCap = params.solarCapGW + params.windCapGW + params.hydroCapGW;

  const rebalance = (key: keyof Params, val: number) => {
    if (!autoRebalance) {
      setParams((p) => ({ ...p, [key]: val }));
      return;
    }
    // When one grows, proportionally reduce fossil proxy (grid limit / curtailment). Here we just keep total cap roughly stable.
    const others = { ...params, [key]: val };
    const targetTotal = Math.max(1, totalCap);
    const sum = others.solarCapGW + others.windCapGW + others.hydroCapGW;
    const scale = targetTotal / sum;
    setParams({ 
      ...others, 
      solarCapGW: round(others.solarCapGW * scale, 2), 
      windCapGW: round(others.windCapGW * scale, 2), 
      hydroCapGW: round(others.hydroCapGW * scale, 2) 
    });
  };

  const exportCSV = () => {
    const headers = Object.keys(hourly[0] || { hour: 0, demandGW: 0, genGW: 0, deficitGW: 0 });
    const rows = hourly.map((r) => headers.map((h) => String(r[h as keyof HourlyData])).join(','));
    const csv = [headers.join(','), ...rows].join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'renewable_integration_hourly.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  const saveSnapshot = () => {
    const payload = { ts: new Date().toISOString(), params, cf, lcoe, kpi };
    localStorage.setItem('renewable_integration_snapshot', JSON.stringify(payload));
    alert('Snapshot saved locally (renewable_integration_snapshot)');
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'grey.50' }}>
      <AppBar position="sticky" elevation={0} sx={{ bgcolor: 'background.paper', borderBottom: 1, borderColor: 'divider' }}>
        <Toolbar sx={{ display: 'flex', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Box sx={{ width: 32, height: 32, borderRadius: 2, bgcolor: 'warning.main', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <LightbulbOutlinedIcon sx={{ color: 'white', fontSize: 20 }} />
            </Box>
            <Box>
              <Typography variant="caption" sx={{ textTransform: 'uppercase', letterSpacing: 2, color: 'text.secondary' }}>
                Renewable
              </Typography>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Integration Studio
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
          <Tab label="Capacity & Costs" />
          <Tab label="Adequacy (Hourly)" />
          <Tab label="Projection" />
        </Tabs>
      </AppBar>

      {/* Overview */}
      {tab === 0 && (
        <Container maxWidth="xl" sx={{ py: 3 }}>
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} md={3}>
              <Kpi label="Renewable Output" value={kpi.renewableTWh} unit="TWh/yr" />
            </Grid>
            <Grid item xs={12} md={3}>
              <Kpi label="System LCOE" value={kpi.systemLCOE} unit="$ / MWh" good={true} />
            </Grid>
            <Grid item xs={12} md={3}>
              <Kpi label="Curtailment" value={kpi.curtailmentPct} unit="%" good={kpi.curtailmentPct <= defaultParams.curtailmentCap} />
            </Grid>
            <Grid item xs={12} md={3}>
              <Kpi label="Adequacy" value={kpi.adequacyOK ? 'OK' : `LOLH ${kpi.lolh}`} unit="" good={kpi.adequacyOK} />
            </Grid>
          </Grid>

          <Card sx={{ borderRadius: 2, boxShadow: 2, transition: 'transform 0.2s', '&:hover': { transform: 'translateY(-2px)' } }}>
            <CardContent>
              <Typography variant="subtitle1" sx={{ color: 'text.primary', mb: 2, fontWeight: 600 }}>Energy Balance vs Demand (Synthetic Year)</Typography>
              <Box sx={{ width: '100%', height: 320 }}>
                <ResponsiveContainer>
                  <AreaChart data={years.map((y, i) => ({
                    year: y,
                    demand: baseline.demandTWh * (1 + i * 0.02),
                    renewable: kpi.renewableTWh * (1 + i * 0.02)
                  }))}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="year" />
                    <YAxis />
                    <RTooltip />
                    <Legend />
                    <Area type="monotone" dataKey="demand" stroke="#64748b" fill="#cbd5e1" fillOpacity={0.4} name="Demand (TWh)" />
                    <Area type="monotone" dataKey="renewable" stroke="#22c55e" fill="#bbf7d0" fillOpacity={0.6} name="Renewable (TWh)" />
                  </AreaChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Container>
      )}

      {/* Capacity & Costs */}
      {tab === 1 && (
        <Container maxWidth="xl" sx={{ py: 3 }}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={5}>
              <Card sx={{ borderRadius: 2, boxShadow: 2, transition: 'transform 0.2s', '&:hover': { transform: 'translateY(-2px)' } }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                    <Typography variant="subtitle1" sx={{ color: 'text.primary', fontWeight: 600 }}>Installed Capacity</Typography>
                    <FormControlLabel 
                      control={<Switch checked={autoRebalance} onChange={(_, v) => setAutoRebalance(v)} />} 
                      label="Auto rebalance" 
                    />
                  </Box>
                  {[
                    ['Solar (GW)', 'solarCapGW'],
                    ['Wind (GW)', 'windCapGW'],
                    ['Hydro (GW)', 'hydroCapGW'],
                    ['Storage (GW)', 'storageCapGW'],
                  ].map(([label, key]) => (
                    <Box key={key} sx={{ py: 2 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2" sx={{ color: 'text.secondary' }}>{label}</Typography>
                        <Chip size="small" label={`${round(params[key as keyof Params] as number, 2)} GW`} />
                      </Box>
                      <Slider 
                        min={0} 
                        max={120} 
                        step={0.5} 
                        value={params[key as keyof Params] as number} 
                        onChange={(_, v) => rebalance(key as keyof Params, Number(v))}
                        valueLabelDisplay="auto"
                      />
                    </Box>
                  ))}
                  <Box sx={{ py: 2 }}>
                    <Typography variant="body2" sx={{ color: 'text.secondary', mb: 1 }}>Storage Duration (hours)</Typography>
                    <TextField 
                      size="small" 
                      type="number" 
                      fullWidth 
                      value={params.storageHours} 
                      onChange={(e) => setParams(p => ({ ...p, storageHours: clamp(Number(e.target.value), 1, 24) }))} 
                    />
                  </Box>
                  <Divider sx={{ my: 2 }} />
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    <Chip label={`Total Cap: ${round(totalCap, 2)} GW`} />
                    <Chip label={`Reserve Margin: ${params.reserveMargin}%`} />
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={7}>
              <Card sx={{ borderRadius: 2, boxShadow: 2 }}>
                <CardContent>
                  <Typography variant="subtitle1" sx={{ color: 'text.primary', mb: 2, fontWeight: 600 }}>Costs & Capacity Factors</Typography>
                  <Grid container spacing={2}>
                    {[
                      ['Solar CF (%)', 'solar', 'cf'],
                      ['Wind CF (%)', 'wind', 'cf'],
                      ['Hydro CF (%)', 'hydro', 'cf'],
                      ['Solar LCOE ($/MWh)', 'solar', 'lcoe'],
                      ['Wind LCOE ($/MWh)', 'wind', 'lcoe'],
                      ['Hydro LCOE ($/MWh)', 'hydro', 'lcoe'],
                      ['Storage LCOS ($/MWh)', 'storage', 'lcoe'],
                    ].map(([label, key, kind]) => (
                      <Grid key={label} item xs={12} sm={6}>
                        <Typography variant="body2" sx={{ color: 'text.secondary', mb: 1 }}>{label}</Typography>
                        <TextField 
                          size="small" 
                          fullWidth 
                          type="number" 
                          value={(kind === 'cf' ? cf : lcoe)[key as keyof CF | keyof LCOE] as number} 
                          onChange={(e) => {
                            if (kind === 'cf') {
                              setCf((prev) => ({ ...prev, [key]: Number(e.target.value) } as CF));
                            } else {
                              setLcoe((prev) => ({ ...prev, [key]: Number(e.target.value) } as LCOE));
                            }
                          }} 
                        />
                      </Grid>
                    ))}
                  </Grid>
                </CardContent>
              </Card>

              <Box sx={{ mt: 2 }}>
                <Card sx={{ borderRadius: 2, boxShadow: 2 }}>
                  <CardContent>
                    <Typography variant="subtitle1" sx={{ color: 'text.primary', mb: 2, fontWeight: 600 }}>Blended LCOE vs Capacity Mix</Typography>
                    <Box sx={{ width: '100%', height: 256 }}>
                      <ResponsiveContainer>
                        <ScatterChart>
                          <CartesianGrid />
                          <XAxis type="number" dataKey="x" name="Renewable Share (cap %)" unit="%" />
                          <YAxis type="number" dataKey="y" name="System LCOE" unit="$" />
                          <ZAxis type="number" range={[60, 200]} />
                          <RTooltip cursor={{ strokeDasharray: '3 3' }} />
                          <Scatter 
                            name="Scenarios" 
                            data={[
                              { x: round((params.solarCapGW) / (totalCap) * 100, 1), y: lcoe.solar },
                              { x: round((params.windCapGW) / (totalCap) * 100, 1), y: lcoe.wind },
                              { x: round((params.hydroCapGW) / (totalCap) * 100, 1), y: lcoe.hydro },
                            ]} 
                            fill="#22c55e" 
                          />
                        </ScatterChart>
                      </ResponsiveContainer>
                    </Box>
                  </CardContent>
                </Card>
              </Box>
            </Grid>
          </Grid>
        </Container>
      )}

      {/* Adequacy (Hourly) */}
      {tab === 2 && (
        <Container maxWidth="xl" sx={{ py: 3 }}>
          <Card sx={{ borderRadius: 2, boxShadow: 2, mb: 3 }}>
            <CardContent>
              <Typography variant="subtitle1" sx={{ color: 'text.primary', mb: 2, fontWeight: 600 }}>Hourly Net Generation vs Demand (Typical Day)</Typography>
              <Box sx={{ width: '100%', height: 320 }}>
                <ResponsiveContainer>
                  <LineChart data={hourly}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="hour" />
                    <YAxis />
                    <Legend />
                    <RTooltip />
                    <Line type="monotone" dataKey="demandGW" name="Demand (GW)" stroke="#64748b" strokeWidth={2} />
                    <Line type="monotone" dataKey="genGW" name="Gen (GW)" stroke="#22c55e" strokeWidth={2} />
                    <Line type="monotone" dataKey="deficitGW" name="Deficit (GW)" stroke="#ef4444" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>

          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card sx={{ borderRadius: 2, boxShadow: 2, height: '100%' }}>
                <CardContent>
                  <Typography variant="subtitle1" sx={{ color: 'text.primary', mb: 2, fontWeight: 600 }}>Curtailment & Grid Limits</Typography>
                  <Grid container spacing={2} sx={{ mb: 2 }}>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" sx={{ color: 'text.secondary', mb: 1 }}>Curtailment Threshold (%)</Typography>
                      <TextField 
                        size="small" 
                        type="number" 
                        fullWidth 
                        value={params.curtailmentCap} 
                        onChange={(e) => setParams(p => ({ ...p, curtailmentCap: clamp(Number(e.target.value), 0, 50) }))} 
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" sx={{ color: 'text.secondary', mb: 1 }}>Grid Max Send-out (GW)</Typography>
                      <TextField 
                        size="small" 
                        type="number" 
                        fullWidth 
                        value={params.gridLimitGW} 
                        onChange={(e) => setParams(p => ({ ...p, gridLimitGW: clamp(Number(e.target.value), 20, 200) }))} 
                      />
                    </Grid>
                  </Grid>
                  <Divider sx={{ my: 2 }} />
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    <Chip label={`Curtailment Now: ${kpi.curtailmentPct}%`} />
                    <Chip label={`LOLH: ${kpi.lolh} h`} />
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card sx={{ borderRadius: 2, boxShadow: 2, height: '100%' }}>
                <CardContent>
                  <Typography variant="subtitle1" sx={{ color: 'text.primary', mb: 2, fontWeight: 600 }}>Storage Utilization Proxy</Typography>
                  <Box sx={{ width: '100%', height: 256 }}>
                    <ResponsiveContainer>
                      <BarChart data={[
                        { k: 'Energy (TWh/yr)', v: kpi.storageEnergyTWh }, 
                        { k: 'Power (GW)', v: params.storageCapGW }
                      ]}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="k" />
                        <YAxis />
                        <RTooltip />
                        <Bar dataKey="v" fill="#06b6d4" />
                      </BarChart>
                    </ResponsiveContainer>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Container>
      )}

      {/* Projection */}
      {tab === 3 && (
        <Container maxWidth="xl" sx={{ py: 3 }}>
          <Card sx={{ borderRadius: 2, boxShadow: 2 }}>
            <CardContent>
              <Typography variant="subtitle1" sx={{ color: 'text.primary', mb: 2, fontWeight: 600 }}>10-year Projection</Typography>
              <Box sx={{ width: '100%', height: 320 }}>
                <ResponsiveContainer>
                  <LineChart data={series}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="year" />
                    <YAxis yAxisId="left" />
                    <YAxis yAxisId="right" orientation="right" />
                    <Legend />
                    <RTooltip />
                    <Line yAxisId="left" type="monotone" dataKey="renTWh" name="Renewable (TWh)" stroke="#22c55e" strokeWidth={2} />
                    <Line yAxisId="left" type="monotone" dataKey="co2Avoided" name="CO₂ Avoided (Mt eq)" stroke="#10b981" strokeWidth={2} />
                    <Line yAxisId="right" type="monotone" dataKey="cost" name="System LCOE ($/MWh)" stroke="#3b82f6" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Container>
      )}

      <Box sx={{ maxWidth: 'xl', mx: 'auto', px: 3, pb: 5, pt: 3, textAlign: 'center' }}>
        <Divider sx={{ mb: 2 }} />
        <Typography variant="caption" sx={{ color: 'text.secondary' }}>
          Energy Transition Model · Renewable Integration — Example implementation (MUI + Recharts)
        </Typography>
      </Box>
    </Box>
  );
};

export default RenewableIntegration;

