"""
Collaborative Energy Ontology Platform - Backend
FastAPI application with role-based access control
"""

from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import jwt
import bcrypt
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL
import json
import asyncio

# Configuration
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Initialize FastAPI
app = FastAPI(
    title="Collaborative Energy Ontology API",
    description="Palantir-style collaborative ontology platform for energy sector",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Enums
class UserRole(str, Enum):
    END_USER = "end_user"
    ENERGY_PROVIDER = "energy_provider"
    DEVICE_OPERATOR = "device_operator"
    ENERGY_EXPERT = "energy_expert"
    SYSTEM_ADMIN = "system_admin"

class ChangeStatus(str, Enum):
    DRAFT = "draft"
    PROPOSED = "proposed"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    MERGED = "merged"

class OntologyChangeType(str, Enum):
    ADD_CLASS = "add_class"
    ADD_PROPERTY = "add_property"
    ADD_INDIVIDUAL = "add_individual"
    MODIFY_CLASS = "modify_class"
    MODIFY_PROPERTY = "modify_property"
    DELETE_CLASS = "delete_class"
    DELETE_PROPERTY = "delete_property"

# Pydantic Models
class User(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    role: UserRole
    organization: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

class OntologyClass(BaseModel):
    uri: str
    label: str
    description: Optional[str] = None
    parent_classes: List[str] = []
    properties: List[str] = []

class OntologyProperty(BaseModel):
    uri: str
    label: str
    description: Optional[str] = None
    domain: Optional[str] = None
    range: Optional[str] = None
    property_type: str  # "ObjectProperty" or "DatatypeProperty"

class OntologyIndividual(BaseModel):
    uri: str
    label: str
    class_type: str
    properties: Dict[str, Any] = {}

class OntologyChange(BaseModel):
    id: Optional[str] = None
    change_type: OntologyChangeType
    author: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: ChangeStatus = ChangeStatus.DRAFT
    title: str
    description: str
    data: Dict[str, Any]
    reviewers: List[str] = []
    comments: List[Dict[str, Any]] = []

class ChangeProposal(BaseModel):
    title: str
    description: str
    change_type: OntologyChangeType
    data: Dict[str, Any]
    target_reviewers: Optional[List[str]] = None

class Comment(BaseModel):
    author: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class SearchQuery(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = None
    limit: int = 50

# In-memory storage (Replace with actual database in production)
fake_users_db = {
    "admin": {
        "username": "admin",
        "email": "admin@gng-energy.com",
        "full_name": "System Administrator",
        "role": UserRole.SYSTEM_ADMIN,
        "organization": "GnG International",
        "hashed_password": bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode(),
        "is_active": True,
        "created_at": datetime.utcnow()
    },
    "expert1": {
        "username": "expert1",
        "email": "expert@gng-energy.com",
        "full_name": "Energy Expert",
        "role": UserRole.ENERGY_EXPERT,
        "organization": "GnG International",
        "hashed_password": bcrypt.hashpw("expert123".encode(), bcrypt.gensalt()).decode(),
        "is_active": True,
        "created_at": datetime.utcnow()
    }
}

ontology_changes: List[Dict] = []
active_websockets: List[WebSocket] = []

# Initialize RDF Graph
energy_graph = Graph()
ENERGY = Namespace("http://gng-energy.com/ontology/core#")
energy_graph.bind("energy", ENERGY)
energy_graph.bind("owl", OWL)

# Helper Functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user(username: str) -> Optional[UserInDB]:
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return UserInDB(**user_dict)
    return None

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = get_user(username)
    if user is None:
        raise credentials_exception
    return User(**user.dict())

def check_permission(user: User, required_roles: List[UserRole]) -> bool:
    return user.role in required_roles

# WebSocket Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

# API Endpoints

@app.get("/")
async def root():
    return {
        "message": "Collaborative Energy Ontology Platform API",
        "version": "1.0.0",
        "documentation": "/docs"
    }

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    user_response = User(**user.dict())
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_response
    }

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.get("/ontology/classes", response_model=List[OntologyClass])
async def get_ontology_classes(
    current_user: User = Depends(get_current_user)
):
    """Get all ontology classes"""
    classes = []
    for s, p, o in energy_graph.triples((None, RDF.type, OWL.Class)):
        class_uri = str(s)
        label = str(energy_graph.value(s, RDFS.label, default=class_uri))
        description = str(energy_graph.value(s, RDFS.comment, default=""))
        
        classes.append(OntologyClass(
            uri=class_uri,
            label=label,
            description=description if description else None
        ))
    
    return classes

@app.get("/ontology/properties", response_model=List[OntologyProperty])
async def get_ontology_properties(
    current_user: User = Depends(get_current_user)
):
    """Get all ontology properties"""
    properties = []
    
    for prop_type in [OWL.ObjectProperty, OWL.DatatypeProperty]:
        for s, p, o in energy_graph.triples((None, RDF.type, prop_type)):
            prop_uri = str(s)
            label = str(energy_graph.value(s, RDFS.label, default=prop_uri))
            description = str(energy_graph.value(s, RDFS.comment, default=""))
            domain = energy_graph.value(s, RDFS.domain)
            range_val = energy_graph.value(s, RDFS.range)
            
            properties.append(OntologyProperty(
                uri=prop_uri,
                label=label,
                description=description if description else None,
                domain=str(domain) if domain else None,
                range=str(range_val) if range_val else None,
                property_type="ObjectProperty" if prop_type == OWL.ObjectProperty else "DatatypeProperty"
            ))
    
    return properties

@app.post("/ontology/proposals", response_model=OntologyChange)
async def create_change_proposal(
    proposal: ChangeProposal,
    current_user: User = Depends(get_current_user)
):
    """Create a new ontology change proposal"""
    
    # Check if user has permission to propose changes
    allowed_roles = [
        UserRole.ENERGY_PROVIDER,
        UserRole.DEVICE_OPERATOR,
        UserRole.ENERGY_EXPERT,
        UserRole.SYSTEM_ADMIN
    ]
    
    if not check_permission(current_user, allowed_roles):
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to propose changes"
        )
    
    change = OntologyChange(
        id=f"change_{len(ontology_changes) + 1}",
        change_type=proposal.change_type,
        author=current_user.username,
        status=ChangeStatus.PROPOSED,
        title=proposal.title,
        description=proposal.description,
        data=proposal.data,
        reviewers=proposal.target_reviewers or []
    )
    
    ontology_changes.append(change.dict())
    
    # Broadcast to all connected clients
    await manager.broadcast({
        "type": "new_proposal",
        "data": change.dict()
    })
    
    return change

@app.get("/ontology/proposals", response_model=List[OntologyChange])
async def get_change_proposals(
    status: Optional[ChangeStatus] = None,
    current_user: User = Depends(get_current_user)
):
    """Get all change proposals, optionally filtered by status"""
    if status:
        filtered_changes = [
            OntologyChange(**change) for change in ontology_changes 
            if change["status"] == status
        ]
        return filtered_changes
    
    return [OntologyChange(**change) for change in ontology_changes]

@app.post("/ontology/proposals/{proposal_id}/review")
async def review_proposal(
    proposal_id: str,
    approved: bool,
    comment: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Review and approve/reject a proposal"""
    
    # Only experts and admins can review
    allowed_roles = [UserRole.ENERGY_EXPERT, UserRole.SYSTEM_ADMIN]
    if not check_permission(current_user, allowed_roles):
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to review proposals"
        )
    
    # Find the proposal
    proposal = None
    for change in ontology_changes:
        if change["id"] == proposal_id:
            proposal = change
            break
    
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    # Add comment
    if comment:
        proposal["comments"].append({
            "author": current_user.username,
            "content": comment,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    # Update status
    if approved:
        proposal["status"] = ChangeStatus.APPROVED
        # Apply changes to ontology
        await apply_ontology_change(proposal)
    else:
        proposal["status"] = ChangeStatus.REJECTED
    
    # Broadcast update
    await manager.broadcast({
        "type": "proposal_reviewed",
        "data": proposal
    })
    
    return {"message": "Proposal reviewed successfully", "proposal": proposal}

async def apply_ontology_change(change: Dict):
    """Apply approved changes to the ontology"""
    change_type = change["change_type"]
    data = change["data"]
    
    if change_type == OntologyChangeType.ADD_CLASS:
        class_uri = URIRef(data["uri"])
        energy_graph.add((class_uri, RDF.type, OWL.Class))
        if "label" in data:
            energy_graph.add((class_uri, RDFS.label, Literal(data["label"])))
        if "description" in data:
            energy_graph.add((class_uri, RDFS.comment, Literal(data["description"])))
    
    elif change_type == OntologyChangeType.ADD_PROPERTY:
        prop_uri = URIRef(data["uri"])
        prop_type = OWL.ObjectProperty if data.get("property_type") == "ObjectProperty" else OWL.DatatypeProperty
        energy_graph.add((prop_uri, RDF.type, prop_type))
        if "label" in data:
            energy_graph.add((prop_uri, RDFS.label, Literal(data["label"])))
    
    change["status"] = ChangeStatus.MERGED

@app.get("/ontology/export")
async def export_ontology(
    format: str = "turtle",
    current_user: User = Depends(get_current_user)
):
    """Export the ontology in various formats"""
    
    formats_map = {
        "turtle": "turtle",
        "xml": "xml",
        "json-ld": "json-ld",
        "n3": "n3"
    }
    
    if format not in formats_map:
        raise HTTPException(status_code=400, detail="Invalid format")
    
    serialized = energy_graph.serialize(format=formats_map[format])
    
    return {
        "format": format,
        "content": serialized
    }

@app.post("/ontology/search", response_model=List[Dict])
async def search_ontology(
    query: SearchQuery,
    current_user: User = Depends(get_current_user)
):
    """Search the ontology using SPARQL"""
    
    # Simple search implementation - enhance with full SPARQL in production
    results = []
    search_term = query.query.lower()
    
    for s, p, o in energy_graph:
        if search_term in str(s).lower() or search_term in str(o).lower():
            results.append({
                "subject": str(s),
                "predicate": str(p),
                "object": str(o)
            })
    
    return results[:query.limit]

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time collaboration"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            
            # Handle different message types
            if data["type"] == "edit":
                # Broadcast edit to all other clients
                await manager.broadcast({
                    "type": "ontology_update",
                    "data": data["data"]
                })
            
            elif data["type"] == "cursor_position":
                # Share cursor positions for collaborative editing
                await manager.broadcast({
                    "type": "cursor_update",
                    "user": data["user"],
                    "position": data["position"]
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "active_connections": len(manager.active_connections),
        "total_changes": len(ontology_changes)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
