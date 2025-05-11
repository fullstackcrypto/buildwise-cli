"""Project storage module for BuildWise CLI."""

import json
import os
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

# Default project directory
DEFAULT_PROJECT_DIR = os.path.expanduser("~/.buildwise/projects")


class MaterialType(str, Enum):
    """Material types supported in projects."""
    
    CONCRETE = "concrete"
    LUMBER = "lumber"
    STEEL = "steel"
    MIXED = "mixed"


@dataclass
class ProjectMaterial:
    """Material information stored in a project."""
    
    material_type: str
    name: str
    quantity: float
    unit: str
    details: Dict[str, Any] = field(default_factory=dict)
    cost: Optional[float] = None
    notes: Optional[str] = None


@dataclass
class Project:
    """Construction project information."""
    
    name: str
    description: Optional[str] = None
    location: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    materials: List[ProjectMaterial] = field(default_factory=list)
    total_cost: Optional[float] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def add_material(self, material: ProjectMaterial) -> None:
        """Add a material to the project."""
        self.materials.append(material)
        self.updated_at = datetime.now().isoformat()
        
        # Update total cost if material has a cost
        if material.cost is not None:
            if self.total_cost is None:
                self.total_cost = 0
            self.total_cost += material.cost
    
    def remove_material(self, index: int) -> Optional[ProjectMaterial]:
        """Remove a material from the project by index."""
        if 0 <= index < len(self.materials):
            material = self.materials.pop(index)
            self.updated_at = datetime.now().isoformat()
            
            # Update total cost if material had a cost
            if material.cost is not None and self.total_cost is not None:
                self.total_cost -= material.cost
            
            return material
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert project to dictionary."""
        project_dict = asdict(self)
        
        # Convert materials to dictionaries
        project_dict["materials"] = [
            asdict(material) if isinstance(material, ProjectMaterial) else material
            for material in self.materials
        ]
        
        return project_dict


class ProjectStorage:
    """Storage for construction projects."""
    
    def __init__(self, storage_dir: Optional[str] = None):
        """Initialize project storage.
        
        Args:
            storage_dir: Directory to store projects
        """
        self.storage_dir = storage_dir or DEFAULT_PROJECT_DIR
        
        # Ensure storage directory exists
        os.makedirs(self.storage_dir, exist_ok=True)
    
    def create_project(
        self,
        name: str,
        description: Optional[str] = None,
        location: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
    ) -> Project:
        """Create a new project.
        
        Args:
            name: Project name
            description: Project description
            location: Project location
            properties: Additional project properties
            
        Returns:
            New project instance
        """
        # Create project
        project = Project(
            name=name,
            description=description,
            location=location,
            properties=properties or {},
        )
        
        # Save project
        self.save_project(project)
        
        return project
    
    def save_project(self, project: Project) -> None:
        """Save a project to storage.
        
        Args:
            project: Project to save
        """
        # Convert to dictionary
        project_dict = project.to_dict()
        
        # Generate filename
        filename = self._get_project_filename(project.name)
        
        # Save to file
        with open(filename, "w") as f:
            json.dump(project_dict, f, indent=2)
    
    def load_project(self, name: str) -> Optional[Project]:
        """Load a project from storage.
        
        Args:
            name: Project name
            
        Returns:
            Project instance, or None if not found
        """
        # Generate filename
        filename = self._get_project_filename(name)
        
        # Check if file exists
        if not os.path.exists(filename):
            return None
        
        # Load from file
        try:
            with open(filename, "r") as f:
                project_dict = json.load(f)
            
            # Create Project instance
            project = Project(
                name=project_dict["name"],
                description=project_dict.get("description"),
                location=project_dict.get("location"),
                created_at=project_dict.get("created_at", datetime.now().isoformat()),
                updated_at=project_dict.get("updated_at", datetime.now().isoformat()),
                total_cost=project_dict.get("total_cost"),
                properties=project_dict.get("properties", {}),
            )
            
            # Add materials
            for material_dict in project_dict.get("materials", []):
                material = ProjectMaterial(
                    material_type=material_dict["material_type"],
                    name=material_dict["name"],
                    quantity=material_dict["quantity"],
                    unit=material_dict["unit"],
                    details=material_dict.get("details", {}),
                    cost=material_dict.get("cost"),
                    notes=material_dict.get("notes"),
                )
                # Add without updating cost (already in total)
                project.materials.append(material)
            
            return project
        except Exception as e:
            print(f"Error loading project {name}: {e}")
            return None
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """List all projects in storage.
        
        Returns:
            List of project summaries
        """
        projects = []
        
        # Check all files in storage directory
        for filename in os.listdir(self.storage_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(self.storage_dir, filename), "r") as f:
                        project_dict = json.load(f)
                    
                    # Create summary
                    projects.append({
                        "name": project_dict["name"],
                        "description": project_dict.get("description", ""),
                        "location": project_dict.get("location", ""),
                        "created_at": project_dict.get("created_at", ""),
                        "updated_at": project_dict.get("updated_at", ""),
                        "material_count": len(project_dict.get("materials", [])),
                        "total_cost": project_dict.get("total_cost"),
                    })
                except Exception as e:
                    print(f"Error loading project from {filename}: {e}")
        
        # Sort by most recently updated
        projects.sort(key=lambda p: p.get("updated_at", ""), reverse=True)
        
        return projects
    
    def delete_project(self, name: str) -> bool:
        """Delete a project from storage.
        
        Args:
            name: Project name
            
        Returns:
            True if project was deleted, False otherwise
        """
        # Generate filename
        filename = self._get_project_filename(name)
        
        # Check if file exists
        if not os.path.exists(filename):
            return False
        
        # Delete file
        os.remove(filename)
        return True
    
    def _get_project_filename(self, name: str) -> str:
        """Get filename for a project.
        
        Args:
            name: Project name
            
        Returns:
            Filename
        """
        # Convert name to filename-safe string
        safe_name = "".join(c if c.isalnum() else "_" for c in name).lower()
        
        # Add timestamp to ensure uniqueness but keep name recognizable
        timestamp = int(time.time())
        
        # Return full path
        return os.path.join(self.storage_dir, f"{safe_name}_{timestamp}.json")
