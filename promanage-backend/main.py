# main.py - ProManage Backend con FastAPI
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
import jwt
import bcrypt
from datetime import datetime, timedelta
import uuid

# Configuración
app = FastAPI(title="ProManage API", version="1.0.0")
SECRET_KEY = "tu-clave-secreta-super-segura"
ALGORITHM = "HS256"

# CORS para desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Modelos Pydantic
class User(BaseModel):
    id: str
    username: str
    email: str
    name: str
    role: str
    created_at: datetime

class UserCreate(BaseModel):
    username: str
    email: str
    name: str
    password: str
    role: str = "user"

class UserLogin(BaseModel):
    username: str
    password: str

class Project(BaseModel):
    id: str
    name: str
    description: str
    budget: float
    start_date: datetime
    end_date: Optional[datetime] = None
    status: str = "active"
    created_by: str
    created_at: datetime
    updated_at: datetime

class ProjectCreate(BaseModel):
    name: str
    description: str
    budget: float
    start_date: datetime
    end_date: Optional[datetime] = None
    status: str = "active"

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    budget: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[str] = None

# Base de datos en memoria (para el MVP)
users_db = {}
projects_db = {}

# Usuarios de prueba
def init_demo_users():
    demo_users = [
        {
            "username": "admin",
            "email": "admin@promanage.com",
            "name": "Administrador",
            "password": "admin123",
            "role": "admin"
        },
        {
            "username": "manager",
            "email": "manager@promanage.com", 
            "name": "Gerente de Proyectos",
            "password": "manager123",
            "role": "manager"
        },
        {
            "username": "user",
            "email": "user@promanage.com",
            "name": "Usuario Regular",
            "password": "user123", 
            "role": "user"
        }
    ]
    
    for user_data in demo_users:
        user_id = str(uuid.uuid4())
        password_hash = bcrypt.hashpw(user_data["password"].encode(), bcrypt.gensalt())
        
        users_db[user_id] = {
            "id": user_id,
            "username": user_data["username"],
            "email": user_data["email"],
            "name": user_data["name"],
            "password_hash": password_hash,
            "role": user_data["role"],
            "created_at": datetime.now()
        }

# Inicializar datos de prueba
init_demo_users()

# Utilidades
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

def get_current_user(user_id: str = Depends(verify_token)):
    user = users_db.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

def verify_password(plain_password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password)

def get_user_by_username(username: str):
    for user in users_db.values():
        if user["username"] == username:
            return user
    return None

# Endpoints de Autenticación
@app.post("/auth/login")
async def login(user_login: UserLogin):
    user = get_user_by_username(user_login.username)
    if not user or not verify_password(user_login.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    access_token = create_access_token(data={"sub": user["id"]})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "name": user["name"],
            "role": user["role"]
        }
    }

@app.post("/auth/register", response_model=User)
async def register(user_create: UserCreate):
    # Verificar si el usuario ya existe
    if get_user_by_username(user_create.username):
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    
    # Crear nuevo usuario
    user_id = str(uuid.uuid4())
    password_hash = bcrypt.hashpw(user_create.password.encode(), bcrypt.gensalt())
    
    new_user = {
        "id": user_id,
        "username": user_create.username,
        "email": user_create.email,
        "name": user_create.name,
        "password_hash": password_hash,
        "role": user_create.role,
        "created_at": datetime.now()
    }
    
    users_db[user_id] = new_user
    
    return User(
        id=new_user["id"],
        username=new_user["username"],
        email=new_user["email"],
        name=new_user["name"],
        role=new_user["role"],
        created_at=new_user["created_at"]
    )

@app.get("/auth/me", response_model=User)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return User(
        id=current_user["id"],
        username=current_user["username"],
        email=current_user["email"],
        name=current_user["name"],
        role=current_user["role"],
        created_at=current_user["created_at"]
    )

# Endpoints de Proyectos
@app.get("/projects", response_model=List[Project])
async def get_projects(current_user: dict = Depends(get_current_user)):
    user_projects = []
    
    for project in projects_db.values():
        # Admins ven todos los proyectos, otros solo los suyos
        if current_user["role"] == "admin" or project["created_by"] == current_user["id"]:
            user_projects.append(Project(**project))
    
    return user_projects

@app.post("/projects", response_model=Project)
async def create_project(project_create: ProjectCreate, current_user: dict = Depends(get_current_user)):
    project_id = str(uuid.uuid4())
    now = datetime.now()
    
    new_project = {
        "id": project_id,
        "name": project_create.name,
        "description": project_create.description,
        "budget": project_create.budget,
        "start_date": project_create.start_date,
        "end_date": project_create.end_date,
        "status": project_create.status,
        "created_by": current_user["id"],
        "created_at": now,
        "updated_at": now
    }
    
    projects_db[project_id] = new_project
    return Project(**new_project)

@app.get("/projects/{project_id}", response_model=Project)
async def get_project(project_id: str, current_user: dict = Depends(get_current_user)):
    project = projects_db.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    # Verificar permisos
    if current_user["role"] != "admin" and project["created_by"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Sin permisos para ver este proyecto")
    
    return Project(**project)

@app.put("/projects/{project_id}", response_model=Project)
async def update_project(project_id: str, project_update: ProjectUpdate, current_user: dict = Depends(get_current_user)):
    project = projects_db.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    # Verificar permisos de edición
    if current_user["role"] != "admin" and project["created_by"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Sin permisos para editar este proyecto")
    
    # Actualizar campos proporcionados
    update_data = project_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        project[field] = value
    
    project["updated_at"] = datetime.now()
    projects_db[project_id] = project
    
    return Project(**project)

@app.delete("/projects/{project_id}")
async def delete_project(project_id: str, current_user: dict = Depends(get_current_user)):
    project = projects_db.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    # Verificar permisos de eliminación
    if current_user["role"] != "admin" and project["created_by"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Sin permisos para eliminar este proyecto")
    
    del projects_db[project_id]
    return {"message": "Proyecto eliminado exitosamente"}

# Endpoints de Dashboard
@app.get("/dashboard/stats")
async def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    user_projects = []
    
    for project in projects_db.values():
        if current_user["role"] == "admin" or project["created_by"] == current_user["id"]:
            user_projects.append(project)
    
    total_projects = len(user_projects)
    total_budget = sum(project["budget"] for project in user_projects)
    
    status_count = {"active": 0, "completed": 0, "paused": 0}
    for project in user_projects:
        status = project.get("status", "active")
        if status in status_count:
            status_count[status] += 1
    
    return {
        "total_projects": total_projects,
        "total_budget": total_budget,
        "status_count": status_count,
        "recent_projects": user_projects[-5:] if user_projects else []
    }

# Endpoint de salud
@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.now(),
        "version": "1.0.0",
        "users_count": len(users_db),
        "projects_count": len(projects_db)
    }

# Endpoint de información de la API
@app.get("/")
async def root():
    return {
        "message": "ProManage API - Sistema de Gestión de Proyectos",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)