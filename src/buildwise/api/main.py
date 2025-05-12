import os
import csv
import json
import uuid
import pathlib
import tempfile
from typing import Dict, List, Optional

from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.background import BackgroundTasks
from pydantic import BaseModel

from buildwise.core.concrete import ConcreteCalculator
from buildwise.core.lumber import LumberCalculator, LumberType, LumberGrade
from buildwise.core.steel import SteelCalculator, SteelType, SteelGrade
from buildwise.config.settings import settings
from buildwise.storage.project import ProjectStorage, ProjectMaterial

# Initialize FastAPI app
app = FastAPI(
    title="BuildWise API", 
    version="0.1.0",
    description="Construction calculator API with material estimation",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Set up templates directory
current_dir = pathlib.Path(__file__).parent
templates_dir = current_dir.parent / "templates"
if not os.path.exists(templates_dir):
    os.makedirs(templates_dir)
templates = Jinja2Templates(directory=str(templates_dir))

# Set up static files directory 
static_dir = current_dir.parent / "static"
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
    css_dir = static_dir / "css"
    if not os.path.exists(css_dir):
        os.makedirs(css_dir)
    js_dir = static_dir / "js"
    if not os.path.exists(js_dir):
        os.makedirs(js_dir)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Initialize services
concrete_calculator = ConcreteCalculator()
lumber_calculator = LumberCalculator()
steel_calculator = SteelCalculator()
project_storage = ProjectStorage()

# Health check endpoints
@app.get("/health")  # Original endpoint
async def health_check():
    return {"status": "ok"}

@app.get("/api/v1/health")  # New API versioned endpoint
async def api_health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": "0.1.0"}

# Web Dashboard Routes
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Render dashboard page."""
    return templates.TemplateResponse("dashboard.html", {"request": request})

# Calculator Page Routes
@app.get("/calculators/concrete", response_class=HTMLResponse)
async def concrete_calculator_page(request: Request):
    """Render concrete calculator page."""
    return templates.TemplateResponse("calculators/concrete.html", {"request": request})

@app.get("/calculators/lumber", response_class=HTMLResponse)
async def lumber_calculator_page(request: Request):
    """Render lumber calculator page."""
    return templates.TemplateResponse("calculators/lumber.html", {"request": request})

@app.get("/calculators/steel", response_class=HTMLResponse)
async def steel_calculator_page(request: Request):
    """Render steel calculator page."""
    return templates.TemplateResponse("calculators/steel.html", {"request": request})

# API Calculator Routes
class ConcreteRequest(BaseModel):
    length: float
    width: float
    depth: float
    unit: str = "feet"
    price_per_unit: Optional[float] = None
    predict_cost: bool = False
    location: Optional[str] = None
    quality: Optional[str] = None

class ConcreteResponse(BaseModel):
    volume: Dict
    cost: Optional[float] = None
    cost_prediction: Optional[Dict] = None
    timestamp: Optional[str] = None

@app.post("/api/v1/calculators/concrete", response_model=ConcreteResponse)
async def calculate_concrete(data: ConcreteRequest):
    """Calculate concrete volume and cost."""
    # Perform calculation
    volume = concrete_calculator.calculate_volume(
        length=data.length,
        width=data.width, 
        depth=data.depth,
        unit=data.unit
    )
    
    cost = None
    if data.price_per_unit:
        cost = concrete_calculator.calculate_cost(
            volume=volume,
            price_per_unit=data.price_per_unit
        )
    
    return {
        "volume": volume,
        "cost": cost,
        "cost_prediction": None,
        "timestamp": None
    }

class LumberRequest(BaseModel):
    width: float
    thickness: float
    length: float
    quantity: int = 1
    length_unit: str = "feet"
    lumber_type: str = "pine"
    grade: str = "no.2"
    price: Optional[float] = None

class LumberResponse(BaseModel):
    board_feet: Dict
    cost: Optional[float] = None

@app.post("/api/v1/calculators/lumber", response_model=LumberResponse)
async def calculate_lumber(data: LumberRequest):
    """Calculate lumber board feet and cost."""
    # Perform calculation
    board_feet = lumber_calculator.calculate_board_feet(
        nominal_width=data.width,
        nominal_thickness=data.thickness,
        length=data.length,
        quantity=data.quantity,
        length_unit=data.length_unit
    )
    
    cost = lumber_calculator.calculate_cost(
        board_feet=board_feet,
        lumber_type=LumberType(data.lumber_type),
        grade=LumberGrade(data.grade),
        price_per_board_foot=data.price
    )
    
    return {
        "board_feet": board_feet,
        "cost": cost
    }

class SteelRequest(BaseModel):
    steel_type: str = "rebar"
    dimensions: Dict = {}
    length: float
    length_unit: str = "feet"
    quantity: int = 1
    grade: Optional[str] = None
    price_per_pound: Optional[float] = None

class SteelResponse(BaseModel):
    weight: Dict
    cost: Optional[float] = None

@app.post("/api/v1/calculators/steel", response_model=SteelResponse)
async def calculate_steel(data: SteelRequest):
    """Calculate steel weight and cost."""
    # Set default dimensions for rebar if not provided
    if data.steel_type == "rebar" and not data.dimensions:
        data.dimensions = {"bar_number": 4}  # Default to #4 rebar
        
    # Perform calculation
    weight = steel_calculator.calculate_weight(
        steel_type=SteelType(data.steel_type),
        dimensions=data.dimensions,
        length=data.length,
        quantity=data.quantity,
        length_unit=data.length_unit
    )
    
    cost = None
    if data.grade:
        cost = steel_calculator.calculate_cost(
            weight=weight,
            steel_type=SteelType(data.steel_type),
            grade=SteelGrade(data.grade),
            price_per_pound=data.price_per_pound
        )
    
    return {
        "weight": weight,
        "cost": cost
    }

# Project API Routes
@app.get("/api/v1/projects")
async def list_projects():
    """List all projects."""
    projects = project_storage.list_projects()
    return {"projects": projects}

class ProjectCreate(BaseModel):
    name: str
    description: str
    location: str

@app.post("/api/v1/projects")
async def create_project(data: ProjectCreate):
    """Create a new project."""
    project = project_storage.create_project(
        name=data.name,
        description=data.description,
        location=data.location
    )
    project_storage.save_project(project)
    return {"name": data.name, "created": True}

@app.get("/api/v1/projects/{name}")
async def get_project(name: str):
    """Get a project by name."""
    project = project_storage.load_project(name)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@app.delete("/api/v1/projects/{name}")
async def delete_project(name: str):
    """Delete a project."""
    success = project_storage.delete_project(name)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"deleted": True}

class MaterialCreate(BaseModel):
    material_type: str
    name: str
    quantity: float
    unit: str
    details: Optional[Dict] = None
    cost: Optional[float] = None
    notes: Optional[str] = None

@app.post("/api/v1/projects/{name}/materials")
async def add_material(name: str, data: MaterialCreate):
    """Add a material to a project."""
    project = project_storage.load_project(name)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    material = ProjectMaterial(
        material_type=data.material_type,
        name=data.name,
        quantity=data.quantity,
        unit=data.unit,
        details=data.details,
        cost=data.cost,
        notes=data.notes
    )
    
    project.add_material(material)
    project_storage.save_project(project)
    
    return {"added": True}

@app.get("/api/v1/projects/{name}/export", response_class=FileResponse)
async def export_project(name: str, background_tasks: BackgroundTasks):
    """Export project to CSV."""
    project = project_storage.load_project(name)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    with open(temp_file.name, "w", newline="") as file:
        writer = csv.writer(file)
        # Write project info
        writer.writerow(["Project Information"])
        writer.writerow(["Name", project.name])
        writer.writerow(["Location", project.location or ""])
        writer.writerow(["Description", project.description or ""])
        writer.writerow([])
        writer.writerow(["Materials"])
        writer.writerow(["Name", "Type", "Quantity", "Unit", "Cost"])
        # Write materials
        for material in project.materials:
            writer.writerow([
                material.name,
                material.material_type,
                material.quantity,
                material.unit,
                material.cost
            ])
        temp_filename = temp_file.name
    
    # Return the file and cleanup afterwards
    background_tasks.add_task(os.unlink, temp_filename)
    return FileResponse(
        path=temp_filename,
        filename=f"{name}_project.csv",
        media_type="text/csv"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("buildwise.api.main:app", host="127.0.0.1", port=8000, reload=True)
