import React, { useEffect, useMemo, useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Tabs,
  Tab,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Slider,
  Box,
  TextField,
  Button,
  Divider,
  IconButton,
  Tooltip,
  Switch,
  FormControlLabel,
  Select,
  MenuItem,
  Chip,
  Container,
} from '@mui/material';
import {
  Download,
  NoteAdd,
  Share,
  Delete,
  ContentCopy,
  Assessment,
  Info,
  Public,
  Add,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip as RTooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
  AreaChart,
  Area,
} from 'recharts';

// -------------------------------
// Types
// -------------------------------

type Scope = 'Room' | 'Building' | 'Community';

type MixKeys = 'solar' | 'wind' | 'hydro' | 'biomass' | 'gas' | 'grid' | 'ess';

interface Scenario {
  id: string;
  name: string;
  scope: Scope;
  region?: string;
  targetYear: number;
  mix: Record<MixKeys, number>; // percentage shares summing to 100
  demandReduction: number; // %
  efficiencyGain: number; // %
  notes?: string;
  createdAt: number;
  updatedAt: number;
}

interface KPI {
  totalCO2: number;
  totalCost: number;
  efficiency: number;
  netBalance: number;
}

// -------------------------------
// Helpers
// -------------------------------

const MIX_ORDER: MixKeys[] = ['solar', 'wind', 'hydro', 'biomass', 'gas', 'grid', 'ess'];

const MIX_LABEL: Record<MixKeys, string> = {
  solar: 'Solar',
  wind: 'Wind',
  hydro: 'Hydro',
  biomass: 'Biomass',
  gas: 'Gas',
  grid: 'Grid',
  ess: 'ESS',
};

const COLORS = ['#3b82f6', '#10b981', '#06b6d4', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

function uid(): string {
  return Math.random().toString(36).slice(2, 10);
}

function clamp(n: number, lo: number, hi: number): number {
  return Math.max(lo, Math.min(hi, n));
}

function sumValues(obj: Record<string, number>): number {
  return Object.values(obj).reduce((a, b) => a + b, 0);
}

function formatNumber(n: number): string {
  return new Intl.NumberFormat().format(n);
}

function toCSV(rows: Array<Record<string, string | number>>): string {
  if (!rows.length) return '';
  const headers = Object.keys(rows[0]);
  const esc = (v: any) =>
    typeof v === 'string' && /[",\n]/.test(v) ? `"${v.replace(/"/g, '""')}"` : v;
  const lines = [headers.join(','), ...rows.map((r) => headers.map((h) => esc(r[h] ?? '')).join(','))];
  return lines.join('\n');
}

// Basic synthetic curves for demand/supply (hourly 24h)
function generateHourlyCurve(seed: number = 1) {
  const rnd = (i: number) => Math.sin((i + seed) / 3) * 0.5 + Math.cos((i + seed) / 5) * 0.2;
  return Array.from({ length: 24 }).map((_, h) => ({
    hour: `${h}:00`,
    demand: Math.round(900 + 400 * Math.abs(rnd(h)) + (h >= 18 && h <= 22 ? 200 : 0)),
    supply: Math.round(950 + 380 * Math.abs(rnd(h + 2))),
  }));
}

function computeKPIs(s: Scenario): KPI {
  // Very simple proxies (replace with your real model):
  const baseCO2Factor = {
    solar: 10,
    wind: 8,
    hydro: 4,
    biomass: 50,
    gas: 400,
    grid: 500,
    ess: 5,
  } as const; // gCO2/kWh equivalent weights (illustrative)

  const baseLCOE = {
    solar: 70,
    wind: 80,
    hydro: 60,
    biomass: 110,
    gas: 120,
    grid: 100,
    ess: 90,
  } as const; // $/MWh equivalent weights (illustrative)

  const mixCO2 = MIX_ORDER.reduce(
    (acc, k) => acc + s.mix[k] * (baseCO2Factor[k as keyof typeof baseCO2Factor] / 100),
    0
  );
  const mixLCOE = MIX_ORDER.reduce(
    (acc, k) => acc + s.mix[k] * (baseLCOE[k as keyof typeof baseLCOE] / 100),
    0
  );

  const demandFactor = 1 - s.demandReduction / 100;
  const effFactor = 1 + s.efficiencyGain / 100;

  const totalCO2 = Math.max(0, Math.round((1000 * mixCO2 * demandFactor) / effFactor)); // tCO2/y (scaled)
  const totalCost = Math.round((1000 * mixLCOE * demandFactor) / effFactor); // arbitrary $ units
  const efficiency = Math.round(70 + s.efficiencyGain * 0.8); // % proxy
  const netBalance = Math.round((efficiency - 80) * 15); // MW proxy

  return { totalCO2, totalCost, efficiency, netBalance };
}

function normalizeMix(mix: Record<MixKeys, number>): Record<MixKeys, number> {
  const total = sumValues(mix);
  if (total === 100) return mix;
  const scale = 100 / (total || 1);
  const out: Record<MixKeys, number> = { ...mix } as any;
  for (const k of MIX_ORDER) out[k] = Math.max(0, Math.round(out[k] * scale));
  // Correct rounding drift
  let diff = 100 - sumValues(out);
  if (diff !== 0) {
    // Add/subtract diff to the largest (or smallest) bucket deterministically
    const sorted = [...MIX_ORDER].sort((a, b) => out[b] - out[a]);
    out[diff > 0 ? sorted[0] : sorted[sorted.length - 1]] += diff;
  }
  return out;
}

function rebalanceOnChange(
  current: Record<MixKeys, number>,
  changed: MixKeys,
  value: number
): Record<MixKeys, number> {
  // Keep sum=100 by proportionally scaling the others
  const val = clamp(value, 0, 100);
  const others = MIX_ORDER.filter((k) => k !== changed);
  const otherSum = others.reduce((acc, k) => acc + current[k], 0);
  const room = 100 - val;
  const next: Record<MixKeys, number> = { ...current, [changed]: val } as any;
  if (otherSum === 0) {
    const even = Math.floor(room / others.length);
    others.forEach((k, i) => (next[k] = i === 0 ? room - even * (others.length - 1) : even));
    return next;
  }
  others.forEach((k) => {
    next[k] = Math.round((current[k] / otherSum) * room);
  });
  return normalizeMix(next);
}

// -------------------------------
// Storage
// -------------------------------

const STORAGE_KEY = 'energyMixStudio.scenarios';

function loadScenarios(): Scenario[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const arr: Scenario[] = JSON.parse(raw);
    return arr.sort((a, b) => b.updatedAt - a.updatedAt);
  } catch {
    return [];
  }
}

function saveScenarios(items: Scenario[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
}

// -------------------------------
// UI Subcomponents
// -------------------------------

interface MetricCardProps {
  title: string;
  value: string;
  unit?: string;
  hint?: string;
}

function MetricCard({ title, value, unit, hint }: MetricCardProps) {
  return (
    <Card sx={{ borderRadius: 2, boxShadow: 2 }}>
      <CardHeader
        sx={{ pb: 1 }}
        title={
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Assessment sx={{ fontSize: 16, color: 'text.secondary' }} />
            <Typography variant="subtitle2" color="text.secondary">
              {title}
            </Typography>
          </Box>
        }
      />
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 1 }}>
          <Typography variant="h4" sx={{ fontWeight: 600 }}>
            {value}
          </Typography>
          {unit && (
            <Typography variant="body2" color="text.secondary">
              {unit}
            </Typography>
          )}
        </Box>
        {hint && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 1 }}>
            <Info sx={{ fontSize: 14, color: 'text.secondary' }} />
            <Typography variant="caption" color="text.secondary">
              {hint}
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}

interface MixSliderProps {
  label: string;
  value: number;
  onChange: (v: number) => void;
}

function MixSlider({ label, value, onChange }: MixSliderProps) {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Typography variant="body2" color="text.secondary">
          {label}
        </Typography>
        <Chip size="small" label={`${value}%`} />
      </Box>
      <Slider
        value={value}
        max={100}
        step={1}
        onChange={(_, v) => onChange(Number(v))}
        valueLabelDisplay="auto"
      />
    </Box>
  );
}

// -------------------------------
// Main Component
// -------------------------------

const EnergyMixStudio: React.FC = () => {
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [compareId, setCompareId] = useState<string | null>(null);
  const [darkMode, setDarkMode] = useState(false);
  const [tab, setTab] = useState(0);

  // Load scenarios on mount
  useEffect(() => {
    const items = loadScenarios();
    if (items.length) {
      setScenarios(items);
      setActiveId(items[0].id);
    } else {
      const def: Scenario = {
        id: uid(),
        name: 'Default Scenario',
        scope: 'Building',
        targetYear: new Date().getFullYear() + 5,
        mix: normalizeMix({ solar: 25, wind: 15, hydro: 5, biomass: 5, gas: 20, grid: 25, ess: 5 }),
        demandReduction: 10,
        efficiencyGain: 8,
        createdAt: Date.now(),
        updatedAt: Date.now(),
      };
      setScenarios([def]);
      setActiveId(def.id);
      saveScenarios([def]);
    }
  }, []);

  // Persist
  useEffect(() => {
    if (scenarios.length) saveScenarios(scenarios);
  }, [scenarios]);

  const active = useMemo(() => scenarios.find((s) => s.id === activeId) || null, [scenarios, activeId]);
  const compare = useMemo(() => scenarios.find((s) => s.id === compareId) || null, [scenarios, compareId]);

  const kpi = useMemo(() => (active ? computeKPIs(active) : null), [active]);
  const kpiCompare = useMemo(() => (compare ? computeKPIs(compare) : null), [compare]);

  function createScenario(partial?: Partial<Scenario>) {
    const base: Scenario = {
      id: uid(),
      name: partial?.name || 'New Scenario',
      scope: partial?.scope || 'Building',
      targetYear: partial?.targetYear || new Date().getFullYear() + 5,
      mix: normalizeMix(partial?.mix || { solar: 20, wind: 15, hydro: 5, biomass: 5, gas: 25, grid: 25, ess: 5 }),
      demandReduction: partial?.demandReduction ?? 0,
      efficiencyGain: partial?.efficiencyGain ?? 0,
      notes: partial?.notes,
      createdAt: Date.now(),
      updatedAt: Date.now(),
    };
    setScenarios((prev) => [base, ...prev]);
    setActiveId(base.id);
  }

  function updateScenario(next: Scenario) {
    setScenarios((prev) => prev.map((s) => (s.id === next.id ? { ...next, updatedAt: Date.now() } : s)));
  }

  function removeScenario(id: string) {
    setScenarios((prev) => prev.filter((s) => s.id !== id));
    if (activeId === id) setActiveId(null);
    if (compareId === id) setCompareId(null);
  }

  function duplicateScenario(s: Scenario) {
    const dup: Scenario = {
      ...s,
      id: uid(),
      name: `${s.name} (Copy)`,
      createdAt: Date.now(),
      updatedAt: Date.now(),
    };
    setScenarios((prev) => [dup, ...prev]);
    setActiveId(dup.id);
  }

  function exportScenario(s: Scenario, type: 'json' | 'csv') {
    if (type === 'json') {
      const blob = new Blob([JSON.stringify(s, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${s.name.replace(/\s+/g, '_')}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } else {
      const rows = [
        { key: 'name', value: s.name },
        { key: 'scope', value: s.scope },
        { key: 'targetYear', value: s.targetYear },
        { key: 'demandReduction(%)', value: s.demandReduction },
        { key: 'efficiencyGain(%)', value: s.efficiencyGain },
        ...MIX_ORDER.map((k) => ({ key: `mix.${k}`, value: s.mix[k] })),
      ];
      const csv = toCSV(rows.map((r) => ({ key: r.key, value: r.value })));
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${s.name.replace(/\s+/g, '_')}.csv`;
      a.click();
      URL.revokeObjectURL(url);
    }
  }

  const hourly = useMemo(() => generateHourlyCurve(3), [active?.id]);

  // Theme toggling (dark mode)
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
      document.body.style.backgroundColor = '#0f172a';
      document.body.style.color = '#f8fafc';
    } else {
      document.documentElement.classList.remove('dark');
      document.body.style.backgroundColor = '#f9fafb';
      document.body.style.color = '#111827';
    }
  }, [darkMode]);

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'grey.50' }}>
      <AppBar position="sticky" elevation={0} sx={{ bgcolor: 'background.paper', borderBottom: 1, borderColor: 'divider' }}>
        <Toolbar sx={{ display: 'flex', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Box sx={{ width: 32, height: 32, borderRadius: 2, bgcolor: 'primary.main' }} />
            <Box>
              <Typography variant="caption" sx={{ textTransform: 'uppercase', letterSpacing: 2, color: 'text.secondary' }}>
                Energy Mix
              </Typography>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Scenario Studio
              </Typography>
            </Box>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <FormControlLabel
              control={<Switch checked={darkMode} onChange={(_, v) => setDarkMode(v)} />}
              label="Dark"
            />
            <Button
              variant="outlined"
              size="small"
              startIcon={<Download />}
              onClick={() => active && exportScenario(active, 'csv')}
            >
              Export CSV
            </Button>
          </Box>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ py: 3 }}>
        <Grid container spacing={3}>
          {/* Left: scenario list */}
          <Grid item xs={12} lg={3}>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Typography variant="subtitle2" sx={{ textTransform: 'uppercase', color: 'text.secondary' }}>
                  Scenarios
                </Typography>
                <Button size="small" startIcon={<NoteAdd />} onClick={() => createScenario()}>
                  Create New
                </Button>
              </Box>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                {scenarios.map((s) => (
                  <Card
                    key={s.id}
                    sx={{
                      cursor: 'pointer',
                      borderRadius: 2,
                      border: activeId === s.id ? 2 : 1,
                      borderColor: activeId === s.id ? 'primary.main' : 'divider',
                      boxShadow: activeId === s.id ? 2 : 0,
                    }}
                    onClick={() => setActiveId(s.id)}
                  >
                    <CardContent sx={{ p: 2 }}>
                      <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
                        <Box>
                          <Typography variant="body2" sx={{ fontWeight: 600 }}>
                            {s.name}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {s.scope} · {s.targetYear}
                          </Typography>
                        </Box>
                        <Box sx={{ display: 'flex', gap: 0.5 }}>
                          <IconButton
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation();
                              duplicateScenario(s);
                            }}
                          >
                            <ContentCopy fontSize="small" />
                          </IconButton>
                          <IconButton
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation();
                              exportScenario(s, 'json');
                            }}
                          >
                            <Share fontSize="small" />
                          </IconButton>
                          <IconButton
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation();
                              removeScenario(s.id);
                            }}
                          >
                            <Delete fontSize="small" />
                          </IconButton>
                        </Box>
                      </Box>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 1 }}>
                        {MIX_ORDER.map((k) => (
                          <Chip
                            key={k}
                            size="small"
                            label={`${MIX_LABEL[k]} ${s.mix[k]}%`}
                            sx={{ fontSize: '0.7rem', height: 20 }}
                          />
                        ))}
                      </Box>
                    </CardContent>
                  </Card>
                ))}
              </Box>

              <Divider />

              <Box>
                <Typography variant="subtitle2" sx={{ textTransform: 'uppercase', color: 'text.secondary', mb: 1 }}>
                Compare With
              </Typography>
                <Select
                  size="small"
                  fullWidth
                  value={compareId || ''}
                  onChange={(e) => setCompareId(e.target.value || null)}
                  displayEmpty
                >
                  <MenuItem value="">None</MenuItem>
                  {scenarios
                    .filter((s) => s.id !== activeId)
                    .map((s) => (
                      <MenuItem key={s.id} value={s.id}>
                        {s.name}
                      </MenuItem>
                    ))}
                </Select>
              </Box>
            </Box>
          </Grid>

          {/* Right: editor & dashboard */}
          <Grid item xs={12} lg={9}>
            {active ? (
              <Card sx={{ borderRadius: 2, boxShadow: 2 }}>
                <CardHeader
                  title={
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                      <TextField
                        size="small"
                        value={active.name}
                        onChange={(e) => updateScenario({ ...active, name: e.target.value })}
                        sx={{ maxWidth: 400 }}
                      />
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
                        <Typography variant="caption" color="text.secondary">
                          Scope:
                        </Typography>
                        {(['Room', 'Building', 'Community'] as Scope[]).map((x) => (
                          <Button
                            key={x}
                            size="small"
                            variant={active.scope === x ? 'contained' : 'outlined'}
                            onClick={() => updateScenario({ ...active, scope: x })}
                          >
                            {x}
                          </Button>
                        ))}
                        <Typography variant="caption" color="text.secondary">
                          Target Year:
                        </Typography>
                        <TextField
                          type="number"
                          size="small"
                          sx={{ width: 100 }}
                          value={active.targetYear}
                          onChange={(e) => updateScenario({ ...active, targetYear: Number(e.target.value) })}
                        />
                      </Box>
                    </Box>
                  }
                  action={
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Button
                        variant="outlined"
                        size="small"
                        startIcon={<Download />}
                        onClick={() => exportScenario(active, 'csv')}
                      >
                        Export Settings
                      </Button>
                      <Button
                        variant="outlined"
                        size="small"
                        startIcon={<Share />}
                        onClick={() => exportScenario(active, 'json')}
                      >
                        Share JSON
                      </Button>
                      <Button variant="contained" size="small" startIcon={<Add />} onClick={() => duplicateScenario(active)}>
                        Duplicate Scenario
                      </Button>
                    </Box>
                  }
                />

                <CardContent>
                  <Tabs value={tab} onChange={(_, v) => setTab(v)}>
                    <Tab label="Settings" />
                    <Tab label="Results" />
                    <Tab label="Compare" />
                  </Tabs>

                  {/* EDIT TAB */}
                  {tab === 0 && (
                    <Box sx={{ mt: 3 }}>
                      <Grid container spacing={3}>
                        <Grid item xs={12} xl={4}>
                          <Card sx={{ borderRadius: 2 }}>
                            <CardHeader title="Energy Mix Share (%)" />
                            <CardContent sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                              {MIX_ORDER.map((k) => (
                                <MixSlider
                                  key={k}
                                  label={MIX_LABEL[k]}
                                  value={active.mix[k]}
                                  onChange={(v) => updateScenario({ ...active, mix: rebalanceOnChange(active.mix, k, v) })}
                                />
                              ))}
                              <Typography variant="caption" color="text.secondary">
                                Total {sumValues(active.mix)}% (Auto-balanced)
                              </Typography>
                            </CardContent>
                          </Card>
                        </Grid>

                        <Grid item xs={12} xl={8}>
                          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                            <Card sx={{ borderRadius: 2 }}>
                              <CardHeader title="Demand/Efficiency Assumptions" />
                              <CardContent>
                                <Grid container spacing={3}>
                                  <Grid item xs={12} sm={6}>
                                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                                      <Typography variant="body2">Demand Reduction</Typography>
                                      <Slider
                                        value={active.demandReduction}
                                        max={50}
                                        step={1}
                                        onChange={(_, v) => updateScenario({ ...active, demandReduction: Number(v) })}
                                        valueLabelDisplay="auto"
                                      />
                                      <Typography variant="body2" color="text.secondary">
                                        {active.demandReduction}%
                                      </Typography>
                                    </Box>
                                  </Grid>
                                  <Grid item xs={12} sm={6}>
                                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                                      <Typography variant="body2">Efficiency Gain</Typography>
                                      <Slider
                                        value={active.efficiencyGain}
                                        max={50}
                                        step={1}
                                        onChange={(_, v) => updateScenario({ ...active, efficiencyGain: Number(v) })}
                                        valueLabelDisplay="auto"
                                      />
                                      <Typography variant="body2" color="text.secondary">
                                        {active.efficiencyGain}%
                                      </Typography>
                                    </Box>
                                  </Grid>
                                </Grid>
                              </CardContent>
                            </Card>

                            <Card sx={{ borderRadius: 2 }}>
                              <CardHeader title="Energy Mix Donut" />
                              <CardContent>
                                <Box sx={{ width: '100%', height: 288 }}>
                                  <ResponsiveContainer>
                                    <PieChart>
                                      <Pie
                                        data={MIX_ORDER.map((k) => ({ name: MIX_LABEL[k], value: active.mix[k] }))}
                                        dataKey="value"
                                        nameKey="name"
                                        innerRadius={70}
                                        outerRadius={110}
                                        paddingAngle={1}
                                      >
                                        {MIX_ORDER.map((k, i) => (
                                          <Cell key={k} fill={COLORS[i % COLORS.length]} />
                                        ))}
                                      </Pie>
                                      <Legend />
                                      <RTooltip />
                                    </PieChart>
                                  </ResponsiveContainer>
                                </Box>
                              </CardContent>
                            </Card>
                          </Box>
                        </Grid>
                      </Grid>
                    </Box>
                  )}

                  {/* RESULTS TAB */}
                  {tab === 1 && (
                    <Box sx={{ mt: 3 }}>
                      <Grid container spacing={3}>
                        <Grid item xs={12} lg={8}>
                          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                            <Card sx={{ borderRadius: 2 }}>
                              <CardHeader title="Demand/Supply Curve (24h)" />
                              <CardContent>
                                <Box sx={{ width: '100%', height: 288 }}>
                                  <ResponsiveContainer>
                                    <LineChart data={hourly}>
                                      <CartesianGrid strokeDasharray="3 3" />
                                      <XAxis dataKey="hour" />
                                      <YAxis />
                                      <RTooltip />
                                      <Line type="monotone" dataKey="demand" stroke="#ef4444" strokeWidth={2} />
                                      <Line type="monotone" dataKey="supply" stroke="#22c55e" strokeWidth={2} />
                                    </LineChart>
                                  </ResponsiveContainer>
                                </Box>
                              </CardContent>
                            </Card>

                            <Card sx={{ borderRadius: 2 }}>
                              <CardHeader title="Annual Power Balance (Example)" />
                              <CardContent>
                                <Box sx={{ width: '100%', height: 240 }}>
                                  <ResponsiveContainer>
                                    <AreaChart data={hourly}>
                                      <CartesianGrid strokeDasharray="3 3" />
                                      <XAxis dataKey="hour" />
                                      <YAxis />
                                      <RTooltip />
                                      <Area type="monotone" dataKey="supply" stroke="#22c55e" fill="#22c55e" fillOpacity={0.6} />
                                      <Area type="monotone" dataKey="demand" stroke="#ef4444" fill="#ef4444" fillOpacity={0.6} />
                                    </AreaChart>
                                  </ResponsiveContainer>
                                </Box>
                              </CardContent>
                            </Card>
                          </Box>
                        </Grid>

                        <Grid item xs={12} lg={4}>
                          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                            <MetricCard
                              title="Total CO₂ Emissions"
                              value={kpi ? formatNumber(kpi.totalCO2) : '-'}
                              unit="tCO₂/y"
                            />
                            <MetricCard
                              title="Total System Cost"
                              value={kpi ? formatNumber(kpi.totalCost) : '-'}
                              unit="$"
                            />
                            <MetricCard title="Efficiency" value={kpi ? `${kpi.efficiency}` : '-'} unit="%" />
                            <MetricCard
                              title="Power Balance"
                              value={kpi ? `${kpi.netBalance}` : '-'}
                              unit="MW"
                            />
                          </Box>
                        </Grid>
                      </Grid>
                    </Box>
                  )}

                  {/* COMPARE TAB */}
                  {tab === 2 && (
                    <Box sx={{ mt: 3 }}>
                      {compare ? (
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                          <Grid container spacing={3}>
                            <Grid item xs={12} lg={8}>
                              <Card sx={{ borderRadius: 2 }}>
                                <CardHeader title="Mix Comparison Donut" />
                                <CardContent>
                                  <Grid container spacing={3}>
                                    {[active, compare].map((s, idx) => (
                                      <Grid key={s!.id} item xs={12} sm={6}>
                                        <Box>
                                          <Typography variant="body2" sx={{ mb: 1, fontWeight: 500 }}>
                                            {idx === 0 ? 'Current' : 'Compare'} · {s!.name}
                                          </Typography>
                                          <Box sx={{ width: '100%', height: 256 }}>
                                            <ResponsiveContainer>
                                              <PieChart>
                                                <Pie
                                                  data={MIX_ORDER.map((k) => ({ name: MIX_LABEL[k], value: s!.mix[k] }))}
                                                  dataKey="value"
                                                  nameKey="name"
                                                  innerRadius={60}
                                                  outerRadius={100}
                                                  paddingAngle={1}
                                                >
                                                  {MIX_ORDER.map((k, i) => (
                                                    <Cell key={k} fill={COLORS[i % COLORS.length]} />
                                                  ))}
                                                </Pie>
                                                <Legend />
                                                <RTooltip />
                                              </PieChart>
                                            </ResponsiveContainer>
                                          </Box>
                                        </Box>
                                      </Grid>
                                    ))}
                                  </Grid>
                                </CardContent>
                              </Card>
                            </Grid>

                            <Grid item xs={12} lg={4}>
                              <Card sx={{ borderRadius: 2 }}>
                                <CardHeader title="Metrics Comparison" />
                                <CardContent>
                                  {kpi && kpiCompare ? (
                                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                                      {(['totalCO2', 'totalCost', 'efficiency', 'netBalance'] as Array<keyof KPI>).map((key) => {
                                        const a = kpi[key];
                                        const b = kpiCompare[key];
                                        const diff = a - b;
                                        const labelMap: Record<string, string> = {
                                          totalCO2: 'Total CO₂',
                                          totalCost: 'Total Cost',
                                          efficiency: 'Efficiency',
                                          netBalance: 'Power Balance',
                                        };
                                        return (
                                          <Box
                                            key={key}
                                            sx={{
                                              display: 'flex',
                                              alignItems: 'center',
                                              justifyContent: 'space-between',
                                              p: 1.5,
                                              borderRadius: 2,
                                              bgcolor: 'grey.50',
                                            }}
                                          >
                                            <Typography variant="body2" color="text.secondary">
                                              {labelMap[key]}
                                            </Typography>
                                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                              <Typography variant="body2">
                                                {formatNumber(a)} → {formatNumber(b)}
                                              </Typography>
                                              <Chip
                                                size="small"
                                                label={`${diff > 0 ? '+' : ''}${formatNumber(Math.abs(diff))}`}
                                                color={diff > 0 ? 'error' : diff < 0 ? 'success' : 'default'}
                                              />
                                            </Box>
                                          </Box>
                                        );
                                      })}
                                    </Box>
                                  ) : (
                                    <Typography variant="body2" color="text.secondary">
                                      Please select a comparison target.
                                    </Typography>
                                  )}
                                </CardContent>
                              </Card>
                            </Grid>
                          </Grid>
                        </Box>
                      ) : (
                        <Box
                          sx={{
                            p: 8,
                            textAlign: 'center',
                            border: 2,
                            borderColor: 'divider',
                            borderStyle: 'dashed',
                            borderRadius: 2,
                            color: 'text.secondary',
                          }}
                        >
                          Please select a scenario from the left to compare.
                        </Box>
                      )}
                    </Box>
                  )}
                </CardContent>
              </Card>
            ) : (
              <Box
                sx={{
                  p: 8,
                  textAlign: 'center',
                  border: 2,
                  borderColor: 'divider',
                  borderStyle: 'dashed',
                  borderRadius: 2,
                  color: 'text.secondary',
                }}
              >
                Please select or create a scenario.
              </Box>
            )}
          </Grid>
        </Grid>
      </Container>

      <Box sx={{ maxWidth: 'xl', mx: 'auto', px: 3, pb: 5, pt: 3, textAlign: 'center' }}>
        <Divider sx={{ mb: 2 }} />
        <Typography variant="caption" sx={{ color: 'text.secondary' }}>
          © {new Date().getFullYear()} GNGMETA · Energy Mix Scenario Studio
        </Typography>
      </Box>
    </Box>
  );
};

export default EnergyMixStudio;

