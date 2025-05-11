"""FastAPI web dashboard for BuildWise CLI."""

import os
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn

from buildwise.core.concrete import ConcreteCalculator
from buildwise.core.lumber import LumberCalculator
from buildwise.core.steel import SteelCalculator
from buildwise.services.ai_prediction import AIPredictionService
from buildwise.storage.project import MaterialType, ProjectMaterial, ProjectStorage

# Initialize FastAPI app
app = FastAPI(
    title="BuildWise Dashboard",
    description="Web dashboard for BuildWise construction calculator suite",
    version="0.1.0",
)

# Set up templates
templates_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
templates = Jinja2Templates(directory=templates_path)

# Set up static files
static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

# Define Pydantic models for API requests/responses

class ConcreteRequest(BaseModel):
    """Request model for concrete calculation."""
    
    length: float
    width: float
    depth: float
    unit: str = "feet"
    price_per_unit: Optional[float] = None


class LumberRequest(BaseModel):
    """Request model for lumber calculation."""
    
    width: float
    thickness: float
    length: float
    quantity: int = 1
    length_unit: str = "feet"
    lumber_type: str = "pine"
    grade: str = "no.2"
    price: Optional[float] = None


class SteelRequest(BaseModel):
    """Request model for steel calculation."""
    
    steel_type: str
    dimensions: Dict[str, float]
    length: float
    length_unit: str = "feet"
    quantity: int = 1
    grade: Optional[str] = None
    price_per_pound: Optional[float] = None


class MaterialCostEstimationRequest(BaseModel):
    """Request model for material cost estimation."""
    
    material_type: str
    quantity: float
    unit: str
    location: str = "United States"


class ProjectRequest(BaseModel):
    """Request model for creating a project."""
    
    name: str
    description: Optional[str] = None
    location: Optional[str] = None


class MaterialRequest(BaseModel):
    """Request model for adding a material to a project."""
    
    material_type: str
    name: str
    quantity: float
    unit: str
    details: Optional[Dict] = None
    cost: Optional[float] = None
    notes: Optional[str] = None


class ProjectSummary(BaseModel):
    """Summary model for projects."""
    
    name: str
    description: Optional[str] = None
    location: Optional[str] = None
    created_at: str
    updated_at: str
    material_count: int
    total_cost: Optional[float] = None


# Define web routes

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Root endpoint to render the dashboard."""
    storage = ProjectStorage()
    projects = storage.list_projects()[:5]  # Get the 5 most recent projects
    
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "projects": projects}
    )


@app.get("/calculators/concrete", response_class=HTMLResponse)
async def concrete_calculator(request: Request):
    """Render concrete calculator page."""
    return templates.TemplateResponse(
        "calculators/concrete.html",
        {"request": request}
    )


# API routes

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/api/v1/calculators/concrete")
async def calculate_concrete(request: ConcreteRequest):
    """Calculate concrete volume and cost."""
    calculator = ConcreteCalculator()
    
    # Calculate volume
    volume = calculator.calculate_volume(
        length=request.length,
        width=request.width,
        depth=request.depth,
        unit=request.unit
    )
    
    # Calculate cost if price is provided
    cost = None
    if request.price_per_unit is not None:
        cost = calculator.calculate_cost(volume, request.price_per_unit)
    
    # Build HTML response for HTMX
    html_response = f"""
    <div class="alert alert-success">
        <h5>Calculation Results</h5>
        <p><strong>Dimensions:</strong> {request.length} x {request.width} x {request.depth} {request.unit}</p>
        <p><strong>Cubic Yards:</strong> {volume["cubic_yards"]}</p>
        <p><strong>Cubic Meters:</strong> {volume["cubic_meters"]}</p>
    """
    
    if cost is not None:
        html_response += f"<p><strong>Cost:</strong> ${cost:.2f}</p>"
    
    html_response += "</div>"
    
    return HTMLResponse(content=html_response)


@app.post("/api/v1/calculators/lumber")
async def calculate_lumber(request: LumberRequest):
    """Calculate lumber board feet and cost."""
    calculator = LumberCalculator()
    
    # Calculate board feet
    result = calculator.calculate_board_feet(
        nominal_width=request.width,
        nominal_thickness=request.thickness,
        length=request.length,
        quantity=request.quantity,
        length_unit=request.length_unit
    )
    
    # Calculate cost
    cost = calculator.calculate_cost(
        board_feet=result,
        lumber_type=request.lumber_type,
        grade=request.grade,
        price_per_board_foot=request.price
    )
    
    # Return result
    return {
        "board_feet": result,
        "cost": cost
    }


@app.post("/api/v1/calculators/steel")
async def calculate_steel(request: SteelRequest):
    """Calculate steel weight and cost."""
    calculator = SteelCalculator()
    
    # Calculate weight
    result = calculator.calculate_weight(
        steel_type=request.steel_type,
        dimensions=request.dimensions,
        length=request.length,
        quantity=request.quantity,
        length_unit=request.length_unit
    )
    
    # Calculate cost
    cost = calculator.calculate_cost(
        weight=result,
        steel_type=request.steel_type,
        grade=request.grade,
        price_per_pound=request.price_per_pound
    )
    
    # Return result
    return {
        "weight": result,
        "cost": cost
    }


@app.post("/api/v1/estimations/material-cost")
async def estimate_material_cost(request: MaterialCostEstimationRequest):
    """Generate AI-powered material cost estimate."""
    # Initialize AI service
    ai_service = AIPredictionService()
    
    # Prepare quantity object based on unit
    if request.unit in ["cubic_yard", "cubic_yards"]:
        quantity_obj = {"cubic_yards": request.quantity}
    elif request.unit in ["board_foot", "board_feet"]:
        quantity_obj = {"board_feet": request.quantity}
    else:
        quantity_obj = request.quantity
    
    # Get prediction
    prediction = ai_service.predict_material_cost(
        material_type=request.material_type,
        quantity=quantity_obj,
        location=request.location
    )
    
    return prediction


@app.get("/api/v1/projects", response_model=List[ProjectSummary])
async def list_projects():
    """List all projects."""
    storage = ProjectStorage()
    projects = storage.list_projects()
    return projects


@app.post("/api/v1/projects")
async def create_project(request: ProjectRequest):
    """Create a new project."""
    storage = ProjectStorage()
    project = storage.create_project(
        name=request.name,
        description=request.description,
        location=request.location
    )
    return {"name": project.name, "created": True}


@app.get("/api/v1/projects/{name}")
async def get_project(name: str):
    """Get a project by name."""
    storage = ProjectStorage()
    project = storage.load_project(name)
    
    if not project:
        raise HTTPException(status_code=404, detail=f"Project '{name}' not found")
    
    return project.to_dict()


@app.post("/api/v1/projects/{name}/materials")
async def add_material(name: str, request: MaterialRequest):
    """Add a material to a project."""
    storage = ProjectStorage()
    project = storage.load_project(name)
    
    if not project:
        raise HTTPException(status_code=404, detail=f"Project '{name}' not found")
    
    # Create material
    material = ProjectMaterial(
        material_type=request.material_type,
        name=request.name,
        quantity=request.quantity,
        unit=request.unit,
        details=request.details or {},
        cost=request.cost,
        notes=request.notes
    )
    
    # Add to project
    project.add_material(material)
    
    # Save project
    storage.save_project(project)
    
    return {"added": True}


@app.delete("/api/v1/projects/{name}")
async def delete_project(name: str):
    """Delete a project by name."""
    storage = ProjectStorage()
    success = storage.delete_project(name)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Project '{name}' not found")
    
    return {"name": name, "deleted": True}


def run_dashboard(host: str = "127.0.0.1", port: int = 8000):
    """Run the FastAPI dashboard."""
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_dashboard()
