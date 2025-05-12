"""Project storage for BuildWise CLI."""
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

from buildwise.config.settings import settings

class ProjectMaterial:
    """Represents a material in a project."""
    
    def __init__(
        self, 
        material_type: str, 
        name: str, 
        quantity: float, 
        unit: str,
        details: Optional[Dict[str, Any]] = None,
        cost: Optional[float] = None,
        notes: Optional[str] = None
    ):
        """Initialize material.
        
        Args:
            material_type: Material type (concrete, lumber, steel)
            name: Material name
            quantity: Material quantity
            unit: Unit of measurement
            details: Additional details
            cost: Material cost
            notes: Additional notes
        """
        self.id = str(uuid.uuid4())
        self.material_type = material_type
        self.name = name
        self.quantity = quantity
        self.unit = unit
        self.details = details or {}
        self.cost = cost
        self.notes = notes
        self.created_at = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert material to dictionary."""
        return {
            "id": self.id,
            "material_type": self.material_type,
            "name": self.name,
            "quantity": self.quantity,
            "unit": self.unit,
            "details": self.details,
            "cost": self.cost,
            "notes": self.notes,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectMaterial':
        """Create material from dictionary."""
        material = cls(
            material_type=data["material_type"],
            name=data["name"],
            quantity=data["quantity"],
            unit=data["unit"],
            details=data.get("details"),
            cost=data.get("cost"),
            notes=data.get("notes")
        )
        material.id = data.get("id", material.id)
        material.created_at = data.get("created_at", material.created_at)
        return material

class Project:
    """Represents a construction project."""
    
    def __init__(self, name: str, description: Optional[str] = None, location: Optional[str] = None):
        """Initialize project.
        
        Args:
            name: Project name
            description: Project description
            location: Project location
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.location = location
        self.materials = []
        self.created_at = datetime.utcnow().isoformat()
        self.updated_at = self.created_at
    
    def add_material(self, material: ProjectMaterial) -> None:
        """Add material to project."""
        self.materials.append(material)
        self.updated_at = datetime.utcnow().isoformat()
    
    def remove_material(self, material_id: str) -> bool:
        """Remove material from project."""
        for i, material in enumerate(self.materials):
            if material.id == material_id:
                del self.materials[i]
                self.updated_at = datetime.utcnow().isoformat()
                return True
        return False
    
    @property
    def total_cost(self) -> float:
        """Calculate total project cost."""
        return sum(m.cost or 0 for m in self.materials)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert project to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "location": self.location,
            "materials": [m.to_dict() for m in self.materials],
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Project':
        """Create project from dictionary."""
        project = cls(
            name=data["name"],
            description=data.get("description"),
            location=data.get("location")
        )
        project.id = data.get("id", project.id)
        project.created_at = data.get("created_at", project.created_at)
        project.updated_at = data.get("updated_at", project.updated_at)
        
        # Add materials
        for material_data in data.get("materials", []):
            material = ProjectMaterial.from_dict(material_data)
            project.materials.append(material)
        
        return project

class ProjectStorage:
    """Storage for projects."""
    
    def __init__(self, project_dir: Optional[str] = None):
        """Initialize storage.
        
        Args:
            project_dir: Project directory path
        """
        self.project_dir = Path(project_dir or settings.project_dir)
        self.project_dir.mkdir(parents=True, exist_ok=True)
    
    def create_project(self, name: str, description: Optional[str] = None, location: Optional[str] = None) -> Project:
        """Create a new project."""
        project = Project(name=name, description=description, location=location)
        self.save_project(project)
        return project
    
    def save_project(self, project: Project) -> None:
        """Save project to storage."""
        file_path = self.project_dir / f"{project.name.replace(' ', '_')}.json"
        with open(file_path, 'w') as f:
            json.dump(project.to_dict(), f, indent=2)
    
    def load_project(self, name: str) -> Optional[Project]:
        """Load project from storage."""
        file_path = self.project_dir / f"{name.replace(' ', '_')}.json"
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return Project.from_dict(data)
        except (json.JSONDecodeError, FileNotFoundError):
            return None
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """List all projects."""
        projects = []
        for file_path in self.project_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                projects.append({
                    "name": data.get("name", "Unknown"),
                    "description": data.get("description"),
                    "location": data.get("location"),
                    "created_at": data.get("created_at"),
                    "material_count": len(data.get("materials", []))
                })
            except (json.JSONDecodeError, FileNotFoundError):
                continue
        
        # Sort by created date, newest first
        return sorted(projects, key=lambda p: p.get("created_at", ""), reverse=True)
    
    def delete_project(self, name: str) -> bool:
        """Delete project from storage."""
        file_path = self.project_dir / f"{name.replace(' ', '_')}.json"
        if file_path.exists():
            file_path.unlink()
            return True
        return False
