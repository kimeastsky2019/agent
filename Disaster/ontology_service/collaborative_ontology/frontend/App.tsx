/**
 * Collaborative Energy Ontology Platform - Frontend
 * Main React Application Component
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Container,
  Drawer,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Avatar,
  Chip,
  Badge,
  IconButton,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  FormControl,
  InputLabel,
  Card,
  CardContent,
  CardActions,
  Grid,
  Paper,
  Tabs,
  Tab,
  Snackbar,
  Alert
} from '@mui/material';
import {
  Menu as MenuIcon,
  Home as HomeIcon,
  AccountTree as OntologyIcon,
  People as PeopleIcon,
  Notifications as NotificationsIcon,
  Settings as SettingsIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Check as CheckIcon,
  Close as CloseIcon,
  Comment as CommentIcon,
  History as HistoryIcon,
  Search as SearchIcon
} from '@mui/icons-material';
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
} from 'reactflow';
import 'reactflow/dist/style.css';
import io from 'socket.io-client';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws';

// Types
interface User {
  username: string;
  email: string;
  full_name: string;
  role: string;
  organization?: string;
}

interface OntologyClass {
  uri: string;
  label: string;
  description?: string;
  parent_classes: string[];
  properties: string[];
}

interface OntologyChange {
  id: string;
  change_type: string;
  author: string;
  timestamp: string;
  status: string;
  title: string;
  description: string;
  data: any;
  reviewers: string[];
  comments: any[];
}

// Custom Hooks
const useWebSocket = (url: string) => {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState<any[]>([]);

  useEffect(() => {
    const ws = new WebSocket(url);

    ws.onopen = () => {
      setIsConnected(true);
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setMessages((prev) => [...prev, data]);
    };

    ws.onclose = () => {
      setIsConnected(false);
      console.log('WebSocket disconnected');
    };

    setSocket(ws);

    return () => {
      ws.close();
    };
  }, [url]);

  const sendMessage = useCallback((message: any) => {
    if (socket && isConnected) {
      socket.send(JSON.stringify(message));
    }
  }, [socket, isConnected]);

  return { socket, isConnected, messages, sendMessage };
};

const useAuth = () => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(
    localStorage.getItem('token')
  );

  const login = async (username: string, password: string) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    const response = await fetch(`${API_BASE_URL}/token`, {
      method: 'POST',
      body: formData,
    });

    if (response.ok) {
      const data = await response.json();
      setToken(data.access_token);
      setUser(data.user);
      localStorage.setItem('token', data.access_token);
      return true;
    }
    return false;
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
  };

  return { user, token, login, logout };
};

// Components
const OntologyGraph: React.FC<{
  classes: OntologyClass[];
  onNodeClick: (node: any) => void;
}> = ({ classes, onNodeClick }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  useEffect(() => {
    // Convert ontology classes to nodes
    const newNodes = classes.map((cls, index) => ({
      id: cls.uri,
      type: 'default',
      data: { label: cls.label },
      position: { x: Math.random() * 500, y: Math.random() * 500 },
    }));

    // Create edges from parent relationships
    const newEdges: any[] = [];
    classes.forEach((cls) => {
      cls.parent_classes.forEach((parent) => {
        newEdges.push({
          id: `${cls.uri}-${parent}`,
          source: parent,
          target: cls.uri,
          type: 'smoothstep',
        });
      });
    });

    setNodes(newNodes);
    setEdges(newEdges);
  }, [classes, setNodes, setEdges]);

  const onConnect = useCallback(
    (params: any) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  return (
    <Box sx={{ width: '100%', height: '600px' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={(event, node) => onNodeClick(node)}
        fitView
      >
        <Controls />
        <MiniMap />
        <Background gap={12} size={1} />
      </ReactFlow>
    </Box>
  );
};

const ChangeProposalCard: React.FC<{
  change: OntologyChange;
  onReview: (id: string, approved: boolean) => void;
  currentUser: User;
}> = ({ change, onReview, currentUser }) => {
  const [showComments, setShowComments] = useState(false);

  const canReview =
    currentUser.role === 'energy_expert' ||
    currentUser.role === 'system_admin';

  return (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6">{change.title}</Typography>
          <Chip
            label={change.status}
            color={
              change.status === 'approved'
                ? 'success'
                : change.status === 'rejected'
                ? 'error'
                : 'default'
            }
            size="small"
          />
        </Box>

        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          {change.description}
        </Typography>

        <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
          <Chip
            label={change.change_type}
            size="small"
            variant="outlined"
          />
          <Chip
            label={`By ${change.author}`}
            size="small"
            variant="outlined"
          />
        </Box>

        {change.comments && change.comments.length > 0 && (
          <Box sx={{ mb: 2 }}>
            <Button
              size="small"
              startIcon={<CommentIcon />}
              onClick={() => setShowComments(!showComments)}
            >
              {change.comments.length} Comments
            </Button>
          </Box>
        )}
      </CardContent>

      {canReview && change.status === 'proposed' && (
        <CardActions>
          <Button
            size="small"
            color="success"
            startIcon={<CheckIcon />}
            onClick={() => onReview(change.id, true)}
          >
            Approve
          </Button>
          <Button
            size="small"
            color="error"
            startIcon={<CloseIcon />}
            onClick={() => onReview(change.id, false)}
          >
            Reject
          </Button>
        </CardActions>
      )}
    </Card>
  );
};

const CreateProposalDialog: React.FC<{
  open: boolean;
  onClose: () => void;
  onSubmit: (proposal: any) => void;
}> = ({ open, onClose, onSubmit }) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [changeType, setChangeType] = useState('add_class');
  const [classUri, setClassUri] = useState('');
  const [classLabel, setClassLabel] = useState('');

  const handleSubmit = () => {
    const proposal = {
      title,
      description,
      change_type: changeType,
      data: {
        uri: classUri,
        label: classLabel,
      },
    };
    onSubmit(proposal);
    onClose();
    // Reset form
    setTitle('');
    setDescription('');
    setChangeType('add_class');
    setClassUri('');
    setClassLabel('');
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Create Change Proposal</DialogTitle>
      <DialogContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
          <TextField
            label="Title"
            fullWidth
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />

          <TextField
            label="Description"
            fullWidth
            multiline
            rows={3}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />

          <FormControl fullWidth>
            <InputLabel>Change Type</InputLabel>
            <Select
              value={changeType}
              onChange={(e) => setChangeType(e.target.value)}
            >
              <MenuItem value="add_class">Add Class</MenuItem>
              <MenuItem value="add_property">Add Property</MenuItem>
              <MenuItem value="modify_class">Modify Class</MenuItem>
            </Select>
          </FormControl>

          <TextField
            label="Class URI"
            fullWidth
            value={classUri}
            onChange={(e) => setClassUri(e.target.value)}
            placeholder="http://gng-energy.com/ontology/core#NewClass"
          />

          <TextField
            label="Class Label"
            fullWidth
            value={classLabel}
            onChange={(e) => setClassLabel(e.target.value)}
          />
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSubmit} variant="contained" color="primary">
          Submit Proposal
        </Button>
      </DialogActions>
    </Dialog>
  );
};

// Main App Component
const App: React.FC = () => {
  const { user, token, login, logout } = useAuth();
  const { isConnected, messages, sendMessage } = useWebSocket(WS_URL);

  const [drawerOpen, setDrawerOpen] = useState(false);
  const [currentTab, setCurrentTab] = useState(0);
  const [classes, setClasses] = useState<OntologyClass[]>([]);
  const [proposals, setProposals] = useState<OntologyChange[]>([]);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' as any });

  // Login form state
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  useEffect(() => {
    if (token) {
      fetchOntologyClasses();
      fetchProposals();
    }
  }, [token]);

  useEffect(() => {
    // Handle WebSocket messages
    messages.forEach((msg) => {
      if (msg.type === 'new_proposal') {
        setProposals((prev) => [msg.data, ...prev]);
        showSnackbar('New proposal received!', 'info');
      } else if (msg.type === 'proposal_reviewed') {
        setProposals((prev) =>
          prev.map((p) => (p.id === msg.data.id ? msg.data : p))
        );
        showSnackbar('Proposal reviewed!', 'success');
      }
    });
  }, [messages]);

  const fetchOntologyClasses = async () => {
    const response = await fetch(`${API_BASE_URL}/ontology/classes`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    if (response.ok) {
      const data = await response.json();
      setClasses(data);
    }
  };

  const fetchProposals = async () => {
    const response = await fetch(`${API_BASE_URL}/ontology/proposals`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    if (response.ok) {
      const data = await response.json();
      setProposals(data);
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    const success = await login(username, password);
    if (success) {
      showSnackbar('Login successful!', 'success');
    } else {
      showSnackbar('Login failed!', 'error');
    }
  };

  const handleCreateProposal = async (proposal: any) => {
    const response = await fetch(`${API_BASE_URL}/ontology/proposals`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(proposal),
    });

    if (response.ok) {
      const data = await response.json();
      setProposals((prev) => [data, ...prev]);
      showSnackbar('Proposal created successfully!', 'success');
    }
  };

  const handleReviewProposal = async (id: string, approved: boolean) => {
    const response = await fetch(
      `${API_BASE_URL}/ontology/proposals/${id}/review`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          approved,
          comment: approved ? 'Approved' : 'Rejected',
        }),
      }
    );

    if (response.ok) {
      fetchProposals();
      showSnackbar(
        `Proposal ${approved ? 'approved' : 'rejected'}!`,
        'success'
      );
    }
  };

  const showSnackbar = (message: string, severity: any) => {
    setSnackbar({ open: true, message, severity });
  };

  // Login screen
  if (!user) {
    return (
      <Container maxWidth="sm" sx={{ mt: 8 }}>
        <Paper sx={{ p: 4 }}>
          <Typography variant="h4" sx={{ mb: 4 }}>
            Collaborative Energy Ontology Platform
          </Typography>
          <form onSubmit={handleLogin}>
            <TextField
              label="Username"
              fullWidth
              sx={{ mb: 2 }}
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
            <TextField
              label="Password"
              type="password"
              fullWidth
              sx={{ mb: 3 }}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <Button type="submit" variant="contained" fullWidth size="large">
              Login
            </Button>
          </form>
        </Paper>
      </Container>
    );
  }

  // Main app interface
  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar position="fixed">
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={() => setDrawerOpen(!drawerOpen)}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Collaborative Energy Ontology
          </Typography>
          <Badge badgeContent={4} color="error" sx={{ mr: 2 }}>
            <NotificationsIcon />
          </Badge>
          <Avatar sx={{ bgcolor: 'secondary.main' }}>
            {user.full_name.charAt(0)}
          </Avatar>
          <Button color="inherit" onClick={logout} sx={{ ml: 2 }}>
            Logout
          </Button>
        </Toolbar>
      </AppBar>

      <Drawer
        anchor="left"
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
      >
        <Box sx={{ width: 250, pt: 8 }}>
          <List>
            <ListItem button onClick={() => setCurrentTab(0)}>
              <ListItemIcon>
                <HomeIcon />
              </ListItemIcon>
              <ListItemText primary="Dashboard" />
            </ListItem>
            <ListItem button onClick={() => setCurrentTab(1)}>
              <ListItemIcon>
                <OntologyIcon />
              </ListItemIcon>
              <ListItemText primary="Ontology" />
            </ListItem>
            <ListItem button onClick={() => setCurrentTab(2)}>
              <ListItemIcon>
                <EditIcon />
              </ListItemIcon>
              <ListItemText primary="Proposals" />
            </ListItem>
            <ListItem button onClick={() => setCurrentTab(3)}>
              <ListItemIcon>
                <PeopleIcon />
              </ListItemIcon>
              <ListItemText primary="Collaborators" />
            </ListItem>
            <Divider sx={{ my: 2 }} />
            <ListItem button>
              <ListItemIcon>
                <SettingsIcon />
              </ListItemIcon>
              <ListItemText primary="Settings" />
            </ListItem>
          </List>
        </Box>
      </Drawer>

      <Box component="main" sx={{ flexGrow: 1, p: 3, mt: 8 }}>
        <Container maxWidth="xl">
          {currentTab === 0 && (
            <Box>
              <Typography variant="h4" sx={{ mb: 3 }}>
                Welcome, {user.full_name}
              </Typography>
              <Grid container spacing={3}>
                <Grid item xs={12} md={4}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6">Total Classes</Typography>
                      <Typography variant="h3">{classes.length}</Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6">Active Proposals</Typography>
                      <Typography variant="h3">
                        {proposals.filter((p) => p.status === 'proposed').length}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6">WebSocket Status</Typography>
                      <Chip
                        label={isConnected ? 'Connected' : 'Disconnected'}
                        color={isConnected ? 'success' : 'error'}
                      />
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            </Box>
          )}

          {currentTab === 1 && (
            <Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
                <Typography variant="h4">Ontology Graph</Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => setCreateDialogOpen(true)}
                >
                  Propose Change
                </Button>
              </Box>
              <OntologyGraph
                classes={classes}
                onNodeClick={(node) => console.log('Node clicked:', node)}
              />
            </Box>
          )}

          {currentTab === 2 && (
            <Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
                <Typography variant="h4">Change Proposals</Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => setCreateDialogOpen(true)}
                >
                  New Proposal
                </Button>
              </Box>
              {proposals.map((proposal) => (
                <ChangeProposalCard
                  key={proposal.id}
                  change={proposal}
                  onReview={handleReviewProposal}
                  currentUser={user}
                />
              ))}
            </Box>
          )}

          {currentTab === 3 && (
            <Box>
              <Typography variant="h4" sx={{ mb: 3 }}>
                Collaborators
              </Typography>
              <Typography>Collaborator management coming soon...</Typography>
            </Box>
          )}
        </Container>
      </Box>

      <CreateProposalDialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        onSubmit={handleCreateProposal}
      />

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert severity={snackbar.severity}>{snackbar.message}</Alert>
      </Snackbar>
    </Box>
  );
};

export default App;
