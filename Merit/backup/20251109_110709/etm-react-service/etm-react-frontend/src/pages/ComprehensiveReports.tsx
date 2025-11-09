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
  TextField,
  Select,
  MenuItem,
  Chip,
  Button,
  Divider,
  IconButton,
  Tooltip,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Checkbox,
  Drawer,
  List,
  ListItem,
  ListItemText,
  Switch,
  FormControlLabel,
  LinearProgress,
  Box,
  Container,
  InputAdornment,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import DownloadOutlinedIcon from '@mui/icons-material/DownloadOutlined';
import CloudUploadOutlinedIcon from '@mui/icons-material/CloudUploadOutlined';
import SaveOutlinedIcon from '@mui/icons-material/SaveOutlined';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import HistoryIcon from '@mui/icons-material/History';
import RateReviewOutlinedIcon from '@mui/icons-material/RateReviewOutlined';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import AssessmentIcon from '@mui/icons-material/Assessment';
import { ResponsiveContainer, LineChart, Line, CartesianGrid, XAxis, YAxis, Legend, Tooltip as RTooltip, BarChart, Bar } from 'recharts';

// ---------------- Mock data ----------------
interface Report {
  id: string;
  name: string;
  scenario: string;
  region: string;
  status: 'Draft' | 'In Review' | 'Approved' | 'Rejected';
  owner: string;
  updated: string;
}

const MOCK_REPORTS: Report[] = [
  { id: 'r1', name: 'KR 2030 – Cost & CO₂', scenario: 'KR_2030_S1', region: 'KR', status: 'Approved', owner: 'bora', updated: '2025-06-01' },
  { id: 'r2', name: 'EU 2035 – RE mix', scenario: 'EU_2035_A', region: 'EU', status: 'In Review', owner: 'yoonsik', updated: '2025-05-22' },
  { id: 'r3', name: 'US 2030 – Policy A', scenario: 'US_2030_A', region: 'US', status: 'Draft', owner: 'alice', updated: '2025-05-11' },
];

interface KpiData {
  year: number;
  co2: number;
  lcoe: number;
  ren: number;
}

const MOCK_KPIS: KpiData[] = [
  { year: 2026, co2: 210, lcoe: 78, ren: 45 },
  { year: 2027, co2: 205, lcoe: 76, ren: 47 },
  { year: 2028, co2: 198, lcoe: 74, ren: 49 },
  { year: 2029, co2: 192, lcoe: 72, ren: 51 },
  { year: 2030, co2: 185, lcoe: 71, ren: 54 },
];

const EMPTY_TEMPLATE = `# Report: {{name}}

**Scenario**: {{scenario}} / **Region**: {{region}} / **Year**: {{year}}

## Summary
- LCOE: {{kpi.lcoe}} $/MWh
- CO₂: {{kpi.co2}} Mt
- Renewable share: {{kpi.ren}} %

## Notes
- Assumptions: {{assumptions}}
- Data sources: {{sources}}
`;

// ---------------- Helpers ----------------
const statusColor = (s: string): { bg: string; text: string } => {
  const colors: Record<string, { bg: string; text: string }> = {
    Draft: { bg: 'grey.200', text: 'grey.700' },
    'In Review': { bg: 'warning.100', text: 'warning.700' },
    Approved: { bg: 'success.100', text: 'success.700' },
    Rejected: { bg: 'error.100', text: 'error.700' },
  };
  return colors[s] || { bg: 'grey.100', text: 'grey.700' };
};

function useFilter(reports: Report[], q: string, region: string, status: string): Report[] {
  return useMemo(() => 
    reports.filter(r => 
      (!q || r.name.toLowerCase().includes(q.toLowerCase())) && 
      (!region || r.region === region) && 
      (!status || r.status === status)
    ), 
    [reports, q, region, status]
  );
}

// ---------------- Components ----------------
function KpiCards() {
  const latest = MOCK_KPIS[MOCK_KPIS.length - 1];
  return (
    <Grid container spacing={2}>
      <Grid item xs={12} md={4}>
        <Card sx={{ borderRadius: 2, boxShadow: 2, transition: 'transform 0.2s', '&:hover': { transform: 'translateY(-2px)' } }}>
          <CardContent sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            <Typography variant="subtitle2" color="text.secondary" sx={{ fontWeight: 500 }}>CO₂ Emissions</Typography>
            <Typography variant="h5" sx={{ fontWeight: 600 }}>{latest.co2} Mt</Typography>
            <LinearProgress 
              variant="determinate" 
              value={Math.max(0, 300 - latest.co2) / 3} 
              sx={{ mt: 1.5 }} 
            />
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={4}>
        <Card sx={{ borderRadius: 2, boxShadow: 2, transition: 'transform 0.2s', '&:hover': { transform: 'translateY(-2px)' } }}>
          <CardContent sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            <Typography variant="subtitle2" color="text.secondary" sx={{ fontWeight: 500 }}>System LCOE</Typography>
            <Typography variant="h5" sx={{ fontWeight: 600 }}>{latest.lcoe} $/MWh</Typography>
            <LinearProgress 
              variant="determinate" 
              value={Math.min(100, 120 - latest.lcoe)} 
              sx={{ mt: 1.5 }} 
            />
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={4}>
        <Card sx={{ borderRadius: 2, boxShadow: 2, transition: 'transform 0.2s', '&:hover': { transform: 'translateY(-2px)' } }}>
          <CardContent sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            <Typography variant="subtitle2" color="text.secondary" sx={{ fontWeight: 500 }}>Renewable Share</Typography>
            <Typography variant="h5" sx={{ fontWeight: 600 }}>{latest.ren}%</Typography>
            <LinearProgress variant="determinate" value={latest.ren} sx={{ mt: 1.5 }} />
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
}

interface ReportsTableProps {
  data: Report[];
  onOpen: (report: Report) => void;
}

function ReportsTable({ data, onOpen }: ReportsTableProps) {
  return (
    <Card sx={{ borderRadius: 2, boxShadow: 2, transition: 'transform 0.2s', '&:hover': { transform: 'translateY(-2px)' } }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="subtitle1" sx={{ color: 'text.primary', fontWeight: 600 }}>Reports</Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button startIcon={<CloudUploadOutlinedIcon />} variant="outlined">Import CSV</Button>
            <Button startIcon={<DownloadOutlinedIcon />} variant="outlined">Export</Button>
          </Box>
        </Box>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell width={32}></TableCell>
              <TableCell>Name</TableCell>
              <TableCell>Scenario</TableCell>
              <TableCell>Region</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Owner</TableCell>
              <TableCell>Updated</TableCell>
              <TableCell align="right">Open</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {data.map((r) => {
              const colors = statusColor(r.status);
              return (
                <TableRow key={r.id} hover>
                  <TableCell><Checkbox size="small" /></TableCell>
                  <TableCell sx={{ fontWeight: 500 }}>{r.name}</TableCell>
                  <TableCell>{r.scenario}</TableCell>
                  <TableCell><Chip size="small" label={r.region} /></TableCell>
                  <TableCell>
                    <Chip 
                      size="small" 
                      label={r.status}
                      sx={{ 
                        bgcolor: colors.bg, 
                        color: colors.text,
                        fontWeight: 500
                      }}
                    />
                  </TableCell>
                  <TableCell>{r.owner}</TableCell>
                  <TableCell>{r.updated}</TableCell>
                  <TableCell align="right">
                    <Button size="small" onClick={() => onOpen(r)}>Open</Button>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}

interface KnowledgePanelProps {
  open: boolean;
  onClose: () => void;
  selection: Report | null;
}

function KnowledgePanel({ open, onClose, selection }: KnowledgePanelProps) {
  return (
    <Drawer anchor="right" open={open} onClose={onClose} PaperProps={{ sx: { width: 420 } }}>
      <Box sx={{ p: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
        <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>Knowledge Panel</Typography>
        {selection ? (
          <>
            <Card sx={{ borderRadius: 2 }}>
              <CardContent>
                <Typography variant="body2" color="text.secondary">Scenario</Typography>
                <Typography variant="body1" sx={{ fontWeight: 500 }}>{selection.scenario}</Typography>
                <Divider sx={{ my: 2 }} />
                <Typography variant="body2" color="text.secondary">Linked Assumptions</Typography>
                <List dense>
                  <ListItem>
                    <ListItemText 
                      primary="LCOE table v2" 
                      secondary="source: GovStat 2024, license: CC-BY" 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="CF curves – KR" 
                      secondary="source: IEA 2024, confidence: High" 
                    />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
            <Card sx={{ borderRadius: 2 }}>
              <CardContent>
                <Typography variant="body2" color="text.secondary">Lineage</Typography>
                <List dense>
                  <ListItem>
                    <HistoryIcon sx={{ mr: 1, color: 'text.secondary' }} />
                    <ListItemText 
                      primary="calc:lcoe_mix@1.3" 
                      secondary="inputs: lcoe_v2, mix_2030, demand_kor" 
                    />
                  </ListItem>
                  <ListItem>
                    <HistoryIcon sx={{ mr: 1, color: 'text.secondary' }} />
                    <ListItemText 
                      primary="calc:co2_factor@0.9" 
                      secondary="inputs: emission_factors, fossil_share" 
                    />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </>
        ) : (
          <Typography variant="body2" color="text.secondary">
            Select a report to see linked data, assumptions, and lineage.
          </Typography>
        )}
      </Box>
    </Drawer>
  );
}

interface ReportModel {
  name: string;
  scenario: string;
  region: string;
  year: number;
  status: 'Draft' | 'In Review' | 'Approved' | 'Rejected';
  assumptions: string;
  sources: string;
}

interface EditorProps {
  model: ReportModel;
  setModel: (model: ReportModel | ((prev: ReportModel) => ReportModel)) => void;
  onValidate: () => void;
  onSave: () => void;
}

function Editor({ model, setModel, onValidate, onSave }: EditorProps) {
  const [template, setTemplate] = useState(EMPTY_TEMPLATE);

  const filled = useMemo(() => template
    .replace('{{name}}', model.name || 'Untitled')
    .replace('{{scenario}}', model.scenario || '-')
    .replace('{{region}}', model.region || '-')
    .replace('{{year}}', String(model.year || 2030))
    .replace('{{kpi.lcoe}}', '71.5')
    .replace('{{kpi.co2}}', '185')
    .replace('{{kpi.ren}}', '54')
    .replace('{{assumptions}}', model.assumptions || 'lcoe_v2, cf_kor_2030')
    .replace('{{sources}}', model.sources || 'IEA 2024; GovStat 2023'), 
    [template, model]);

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={5}>
        <Card sx={{ borderRadius: 2, boxShadow: 2, height: '100%', transition: 'transform 0.2s', '&:hover': { transform: 'translateY(-2px)' } }}>
          <CardContent sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <Typography variant="subtitle1" sx={{ color: 'text.primary', fontWeight: 600 }}>Report Meta</Typography>
            <TextField 
              label="Name" 
              fullWidth 
              size="small" 
              value={model.name} 
              onChange={(e) => setModel(m => ({ ...m, name: e.target.value }))} 
            />
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <TextField 
                  label="Scenario" 
                  size="small" 
                  fullWidth
                  value={model.scenario} 
                  onChange={(e) => setModel(m => ({ ...m, scenario: e.target.value }))} 
                />
              </Grid>
              <Grid item xs={6}>
                <TextField 
                  label="Region" 
                  size="small" 
                  fullWidth
                  value={model.region} 
                  onChange={(e) => setModel(m => ({ ...m, region: e.target.value }))} 
                />
              </Grid>
              <Grid item xs={6}>
                <TextField 
                  label="Year" 
                  size="small" 
                  type="number" 
                  fullWidth
                  value={model.year} 
                  onChange={(e) => setModel(m => ({ ...m, year: Number(e.target.value) }))} 
                />
              </Grid>
              <Grid item xs={6}>
                <Select 
                  size="small" 
                  fullWidth
                  value={model.status} 
                  onChange={(e) => setModel(m => ({ ...m, status: e.target.value as ReportModel['status'] }))}
                >
                  {['Draft', 'In Review', 'Approved', 'Rejected'].map(s => (
                    <MenuItem key={s} value={s}>{s}</MenuItem>
                  ))}
                </Select>
              </Grid>
            </Grid>
            <TextField 
              label="Assumptions" 
              fullWidth 
              size="small" 
              value={model.assumptions} 
              onChange={(e) => setModel(m => ({ ...m, assumptions: e.target.value }))} 
            />
            <TextField 
              label="Sources" 
              fullWidth 
              size="small" 
              value={model.sources} 
              onChange={(e) => setModel(m => ({ ...m, sources: e.target.value }))} 
            />
            <Divider />
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button 
                variant="outlined" 
                startIcon={<RateReviewOutlinedIcon />} 
                onClick={onValidate}
              >
                Validate (SHACL)
              </Button>
              <Button 
                variant="contained" 
                startIcon={<SaveOutlinedIcon />} 
                onClick={onSave}
              >
                Save Draft
              </Button>
            </Box>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={7}>
        <Card sx={{ borderRadius: 2, boxShadow: 2, height: '100%', transition: 'transform 0.2s', '&:hover': { transform: 'translateY(-2px)' } }}>
          <CardContent sx={{ height: '100%' }}>
            <Typography variant="subtitle1" sx={{ color: 'text.primary', mb: 2, fontWeight: 600 }}>Template</Typography>
            <TextField 
              multiline 
              minRows={18} 
              fullWidth 
              value={template} 
              onChange={(e) => setTemplate(e.target.value)} 
            />
            <Divider sx={{ my: 2 }} />
            <Typography variant="subtitle1" sx={{ color: 'text.primary', mb: 2, fontWeight: 600 }}>Preview</Typography>
            <Box 
              component="pre" 
              sx={{ 
                bgcolor: 'grey.50', 
                border: 1, 
                borderColor: 'grey.200', 
                borderRadius: 2, 
                p: 2, 
                overflow: 'auto', 
                fontSize: '0.875rem',
                whiteSpace: 'pre-wrap',
                maxHeight: 400,
                overflowY: 'auto'
              }}
            >
              {filled}
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
}

interface ValidationIssue {
  rule: string;
  detail: string;
}

interface ValidationResults {
  ok: boolean;
  issues: ValidationIssue[];
}

interface ValidationPanelProps {
  results: ValidationResults | null;
}

function ValidationPanel({ results }: ValidationPanelProps) {
  if (!results) return null;
  const ok = results.ok;
  return (
    <Card sx={{ borderRadius: 2, boxShadow: 2, transition: 'transform 0.2s', '&:hover': { transform: 'translateY(-2px)' } }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
          {ok ? (
            <CheckCircleOutlineIcon sx={{ color: 'success.main' }} />
          ) : (
            <ErrorOutlineIcon sx={{ color: 'error.main' }} />
          )}
          <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>Validation {ok ? 'Passed' : 'Failed'}</Typography>
        </Box>
        <List dense>
          {results.issues.map((i, idx) => (
            <ListItem key={idx}>
              <ListItemText primary={i.rule} secondary={i.detail} />
            </ListItem>
          ))}
        </List>
      </CardContent>
    </Card>
  );
}

interface ReviewDiffProps {
  before: Record<string, any>;
  after: Record<string, any>;
  onApprove: () => void;
  onReject: () => void;
}

function ReviewDiff({ before, after, onApprove, onReject }: ReviewDiffProps) {
  const diff = useMemo(() => {
    const keys = Array.from(new Set([...Object.keys(before || {}), ...Object.keys(after || {})]));
    return keys.map(k => ({
      key: k,
      a: before?.[k],
      b: after?.[k],
      changed: JSON.stringify(before?.[k]) !== JSON.stringify(after?.[k])
    }));
  }, [before, after]);

  return (
    <Card sx={{ borderRadius: 2, boxShadow: 2, transition: 'transform 0.2s', '&:hover': { transform: 'translateY(-2px)' } }}>
      <CardContent>
        <Typography variant="subtitle1" sx={{ color: 'text.primary', mb: 2, fontWeight: 600 }}>Change Requests</Typography>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Field</TableCell>
              <TableCell>Before</TableCell>
              <TableCell>After</TableCell>
              <TableCell>Changed</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {diff.map(row => (
              <TableRow 
                key={row.key} 
                sx={{ bgcolor: row.changed ? 'warning.50' : 'transparent' }}
              >
                <TableCell sx={{ fontWeight: 500 }}>{row.key}</TableCell>
                <TableCell sx={{ color: 'text.secondary' }}>{String(row.a ?? '-')}</TableCell>
                <TableCell>{String(row.b ?? '-')}</TableCell>
                <TableCell>
                  {row.changed ? (
                    <Chip size="small" label="changed" color="warning" />
                  ) : null}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
          <Button variant="contained" color="success" onClick={onApprove}>Approve</Button>
          <Button variant="outlined" color="error" onClick={onReject}>Reject</Button>
        </Box>
      </CardContent>
    </Card>
  );
}

// --- Main Component ---
const ComprehensiveReports: React.FC = () => {
  const [tab, setTab] = useState(0);
  const [q, setQ] = useState('');
  const [region, setRegion] = useState('');
  const [status, setStatus] = useState('');
  const [panelOpen, setPanelOpen] = useState(false);
  const [selection, setSelection] = useState<Report | null>(null);

  const filtered = useFilter(MOCK_REPORTS, q, region, status);

  const [model, setModel] = useState<ReportModel>({
    name: 'KR 2030 – Cost & CO₂',
    scenario: 'KR_2030_S1',
    region: 'KR',
    year: 2030,
    status: 'Draft',
    assumptions: 'lcoe_v2, cf_kor_2030',
    sources: 'IEA 2024; GovStat 2023'
  });
  const [validation, setValidation] = useState<ValidationResults | null>(null);
  const [reviewBefore] = useState({ name: 'KR 2030 – Cost & CO₂', region: 'KR', year: 2030, sources: 'IEA 2023' });
  const [reviewAfter] = useState({ name: 'KR 2030 – Cost & CO₂ (rev)', region: 'KR', year: 2031, sources: 'IEA 2024; GovStat 2023' });
  const [publicView, setPublicView] = useState(false);

  const runValidation = () => {
    // Mock SHACL rules
    const issues: ValidationIssue[] = [];
    if (!model.name) issues.push({ rule: 'Report.name required', detail: 'Provide a non-empty name' });
    if (!(model.year >= 2000 && model.year <= 2100)) {
      issues.push({ rule: 'Year range', detail: 'Year must be between 2000 and 2100' });
    }
    if (String(model.sources || '').length < 4) {
      issues.push({ rule: 'Sources required', detail: 'Provide at least one data source' });
    }
    const ok = issues.length === 0;
    setValidation({
      ok,
      issues: ok ? [{ rule: 'OK', detail: 'All constraints satisfied' }] : issues
    });
  };

  const saveDraft = () => alert('Draft saved (mock)');

  const openPanel = (r: Report) => {
    setSelection(r);
    setPanelOpen(true);
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'grey.50' }}>
      <AppBar position="sticky" elevation={0} sx={{ bgcolor: 'background.paper', borderBottom: 1, borderColor: 'divider' }}>
        <Toolbar sx={{ display: 'flex', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Box sx={{ width: 32, height: 32, borderRadius: 2, bgcolor: 'info.main', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <AssessmentIcon sx={{ color: 'white', fontSize: 20 }} />
            </Box>
            <Box>
              <Typography variant="caption" sx={{ textTransform: 'uppercase', letterSpacing: 2, color: 'text.secondary' }}>
                Collaborative
              </Typography>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Ontology Building
              </Typography>
            </Box>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Tooltip title="Toggle public view">
              <FormControlLabel 
                control={<Switch checked={publicView} onChange={(_, v) => setPublicView(v)} size="small" />} 
                label="Public" 
              />
            </Tooltip>
            <Button
              variant="outlined"
              size="small"
              startIcon={<DownloadOutlinedIcon />}
            >
              Export
            </Button>
          </Box>
        </Toolbar>
        <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ px: 2 }}>
          <Tab label="Reports Hub" />
          <Tab label="Editor" />
          <Tab label="Review" />
        </Tabs>
      </AppBar>

      {/* Reports Hub */}
      {tab === 0 && (
        <Container maxWidth="xl" sx={{ py: 3 }}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            <KpiCards />

            <Card sx={{ borderRadius: 2, boxShadow: 2, transition: 'transform 0.2s', '&:hover': { transform: 'translateY(-2px)' } }}>
              <CardContent>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={3}>
                    <TextField 
                      size="small" 
                      placeholder="Search reports" 
                      fullWidth
                      value={q} 
                      onChange={(e) => setQ(e.target.value)} 
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <SearchIcon sx={{ color: 'text.secondary' }} />
                          </InputAdornment>
                        )
                      }}
                    />
                  </Grid>
                  <Grid item xs={12} md={2}>
                    <Select 
                      size="small" 
                      displayEmpty 
                      fullWidth
                      value={region} 
                      onChange={(e) => setRegion(e.target.value)}
                    >
                      <MenuItem value="">All regions</MenuItem>
                      {['KR', 'EU', 'US'].map(r => (
                        <MenuItem key={r} value={r}>{r}</MenuItem>
                      ))}
                    </Select>
                  </Grid>
                  <Grid item xs={12} md={2}>
                    <Select 
                      size="small" 
                      displayEmpty 
                      fullWidth
                      value={status} 
                      onChange={(e) => setStatus(e.target.value)}
                    >
                      <MenuItem value="">All status</MenuItem>
                      {['Draft', 'In Review', 'Approved'].map(s => (
                        <MenuItem key={s} value={s}>{s}</MenuItem>
                      ))}
                    </Select>
                  </Grid>
                  <Grid item xs={12} md={5}>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Button variant="contained">New Report</Button>
                      <Button variant="outlined" startIcon={<RateReviewOutlinedIcon />}>
                        Send to Review
                      </Button>
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>

            <ReportsTable data={filtered} onOpen={openPanel} />

            <Card sx={{ borderRadius: 2, boxShadow: 2, transition: 'transform 0.2s', '&:hover': { transform: 'translateY(-2px)' } }}>
              <CardContent>
                <Typography variant="subtitle1" sx={{ color: 'text.primary', mb: 2, fontWeight: 600 }}>KPI Trends</Typography>
                <Box sx={{ width: '100%', height: 320 }}>
                  <ResponsiveContainer>
                    <LineChart data={MOCK_KPIS}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="year" />
                      <YAxis />
                      <Legend />
                      <RTooltip />
                      <Line dataKey="co2" name="CO₂ (Mt)" stroke="#ef4444" strokeWidth={2} />
                      <Line dataKey="lcoe" name="LCOE ($/MWh)" stroke="#3b82f6" strokeWidth={2} />
                      <Line dataKey="ren" name="Renewables (%)" stroke="#22c55e" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </Box>
              </CardContent>
            </Card>

            <KnowledgePanel open={panelOpen} onClose={() => setPanelOpen(false)} selection={selection} />
          </Box>
        </Container>
      )}

      {/* Editor */}
      {tab === 1 && (
        <Container maxWidth="xl" sx={{ py: 3 }}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            <Editor model={model} setModel={setModel} onValidate={runValidation} onSave={saveDraft} />
            <ValidationPanel results={validation} />
          </Box>
        </Container>
      )}

      {/* Review */}
      {tab === 2 && (
        <Container maxWidth="xl" sx={{ py: 3 }}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card sx={{ borderRadius: 2, boxShadow: 2, transition: 'transform 0.2s', '&:hover': { transform: 'translateY(-2px)' } }}>
                  <CardContent>
                    <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>Reviewer Checklist</Typography>
                    <List dense>
                      <ListItem>
                        <CheckCircleOutlineIcon sx={{ mr: 1, color: 'success.main' }} />
                        <ListItemText primary="All required fields present" />
                      </ListItem>
                      <ListItem>
                        <CheckCircleOutlineIcon sx={{ mr: 1, color: 'success.main' }} />
                        <ListItemText primary="Sources and licenses attached" />
                      </ListItem>
                      <ListItem>
                        <ErrorOutlineIcon sx={{ mr: 1, color: 'warning.main' }} />
                        <ListItemText primary="Verify LCOE formula matches v1.3" />
                      </ListItem>
                    </List>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={6}>
                <Card sx={{ borderRadius: 2, boxShadow: 2, transition: 'transform 0.2s', '&:hover': { transform: 'translateY(-2px)' } }}>
                  <CardContent>
                    <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>Reviewer Actions</Typography>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Button startIcon={<ArrowForwardIcon />} variant="outlined">
                        Request Changes
                      </Button>
                      <Button color="success" variant="contained">
                        Approve & Publish
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            <ReviewDiff 
              before={reviewBefore} 
              after={reviewAfter} 
              onApprove={() => alert('Approved (mock)')} 
              onReject={() => alert('Rejected (mock)')} 
            />

            <Card sx={{ borderRadius: 2, boxShadow: 2, transition: 'transform 0.2s', '&:hover': { transform: 'translateY(-2px)' } }}>
              <CardContent>
                <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>Metric Plausibility Check</Typography>
                <Box sx={{ width: '100%', height: 288 }}>
                  <ResponsiveContainer>
                    <BarChart data={[
                      { k: 'CO₂', a: 200, b: 185 },
                      { k: 'LCOE', a: 75, b: 71 },
                      { k: 'Renewables', a: 50, b: 54 }
                    ]}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="k" />
                      <YAxis />
                      <Legend />
                      <RTooltip />
                      <Bar dataKey="a" name="Before" fill="#94a3b8" />
                      <Bar dataKey="b" name="After" fill="#22c55e" />
                    </BarChart>
                  </ResponsiveContainer>
                </Box>
              </CardContent>
            </Card>
          </Box>
        </Container>
      )}

      <Box sx={{ maxWidth: 'xl', mx: 'auto', px: 3, pb: 5, pt: 3, textAlign: 'center' }}>
        <Divider sx={{ mb: 2 }} />
        <Typography variant="caption" sx={{ color: 'text.secondary' }}>
          Energy Transition Model · Comprehensive Reports — UI mock (MUI + Recharts)
        </Typography>
      </Box>
    </Box>
  );
};

export default ComprehensiveReports;

