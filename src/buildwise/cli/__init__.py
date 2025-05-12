import typer
from rich.console import Console
from rich.table import Table
from typing import Optional

from buildwise.core.concrete import ConcreteCalculator
from buildwise.core.lumber import LumberCalculator, LumberType, LumberGrade
from buildwise.core.steel import SteelCalculator, SteelType, SteelGrade

app = typer.Typer(
    help="BuildWise CLI: A comprehensive construction calculator suite",
    add_completion=False,
)
console = Console()

# Concrete calculator command
@app.command()
def concrete(
    length: float = typer.Option(..., help="Length of the area"),
    width: float = typer.Option(..., help="Width of the area"),
    depth: float = typer.Option(..., help="Depth of the concrete"),
    unit: str = typer.Option("feet", help="Unit of measurement (feet, meters, etc.)"),
    price_per_unit: Optional[float] = typer.Option(None, help="Price per cubic yard/meter"),
    bag_size: Optional[float] = typer.Option(None, help="Bag size (80lb, 60lb, 50kg, etc.)"),
    bag_unit: str = typer.Option("lb", help="Bag unit (lb, kg)"),
    output: Optional[str] = typer.Option(None, help="Output file for results (CSV)"),
    detail: bool = typer.Option(False, help="Show detailed information"),
):
    """Calculate concrete volume and optionally cost."""
    calculator = ConcreteCalculator()
    volume = calculator.calculate_volume(length, width, depth, unit)
    
    table = Table(title="Concrete Calculation Results")
    table.add_column("Measurement")
    table.add_column("Value")
    
    table.add_row("Length", f"{length} {unit}")
    table.add_row("Width", f"{width} {unit}")
    table.add_row("Depth", f"{depth} {unit}")
    table.add_row("Volume (cubic yards)", str(volume["cubic_yards"]))
    table.add_row("Volume (cubic meters)", str(volume["cubic_meters"]))
    
    if price_per_unit is not None:
        cost = calculator.calculate_cost(volume, price_per_unit)
        table.add_row("Cost", f"${cost:.2f}")
    
    if bag_size is not None:
        bags = calculator.bags_needed(volume, bag_size, bag_unit)
        table.add_row(f"Bags needed ({bag_size} {bag_unit})", str(bags))
    
    console.print(table)
    
    if output:
        import csv
        with open(output, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Measurement", "Value"])
            writer.writerow(["Length", f"{length} {unit}"])
            writer.writerow(["Width", f"{width} {unit}"])
            writer.writerow(["Depth", f"{depth} {unit}"])
            writer.writerow(["Volume (cubic yards)", volume["cubic_yards"]])
            writer.writerow(["Volume (cubic meters)", volume["cubic_meters"]])
            if price_per_unit is not None:
                writer.writerow(["Cost", f"${cost:.2f}"])
            if bag_size is not None:
                writer.writerow([f"Bags needed ({bag_size} {bag_unit})", bags])
        console.print(f"Results saved to {output}")

# Lumber calculator command
@app.command()
def lumber(
    width: float = typer.Option(..., help="Nominal width in inches (e.g., 4 for a 2x4)"),
    thickness: float = typer.Option(..., help="Nominal thickness in inches (e.g., 2 for a 2x4)"),
    length: float = typer.Option(..., help="Length of the lumber"),
    quantity: int = typer.Option(1, help="Number of pieces"),
    length_unit: str = typer.Option("feet", help="Unit for length (feet, meters)"),
    lumber_type: str = typer.Option("pine", help="Type of lumber"),
    grade: str = typer.Option("no.2", help="Grade of lumber"),
    price: Optional[float] = typer.Option(None, help="Custom price per board foot"),
    output: Optional[str] = typer.Option(None, help="Output file for results (CSV)"),
    detail: bool = typer.Option(False, help="Show detailed information"),
):
    """Calculate lumber board feet and cost."""
    calculator = LumberCalculator()
    result = calculator.calculate_board_feet(
        nominal_width=width,
        nominal_thickness=thickness,
        length=length,
        quantity=quantity,
        length_unit=length_unit
    )
    
    # Calculate cost
    cost = calculator.calculate_cost(
        board_feet=result,
        lumber_type=lumber_type,
        grade=grade,
        price_per_board_foot=price
    )
    
    table = Table(title="Lumber Calculation Results")
    table.add_column("Measurement")
    table.add_column("Value")
    
    table.add_row(f"Nominal Size", f"{thickness}×{width}")
    table.add_row(f"Actual Size", f"{result['actual_thickness']}\"×{result['actual_width']}\"")
    table.add_row("Length", f"{length} {length_unit}")
    table.add_row("Quantity", str(quantity))
    table.add_row("Board Feet", str(result["board_feet"]))
    table.add_row("Cost", f"${cost:.2f}")
    
    console.print(table)
    
    if output:
        import csv
        with open(output, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Measurement", "Value"])
            writer.writerow(["Nominal Size", f"{thickness}×{width}"])
            writer.writerow(["Actual Size", f"{result['actual_thickness']}\"×{result['actual_width']}\""])
            writer.writerow(["Length", f"{length} {length_unit}"])
            writer.writerow(["Quantity", quantity])
            writer.writerow(["Board Feet", result["board_feet"]])
            writer.writerow(["Cost", f"${cost:.2f}"])
        console.print(f"Results saved to {output}")

# Steel calculator command
@app.command()
def steel(
    steel_type: str = typer.Option("rebar", help="Type of steel"),
    length: float = typer.Option(..., help="Length of the steel"),
    length_unit: str = typer.Option("feet", help="Unit for length (feet, meters)"),
    quantity: int = typer.Option(1, help="Number of pieces"),
    grade: Optional[str] = typer.Option(None, help="Grade of steel"),
    price_per_pound: Optional[float] = typer.Option(None, help="Custom price per pound"),
    output: Optional[str] = typer.Option(None, help="Output file for results (CSV)"),
    detail: bool = typer.Option(False, help="Show detailed information"),
    # Add bar_number directly to the function arguments so it's a top-level option
    bar_number: Optional[int] = typer.Option(None, help="Rebar size number (3-18)"),
    width: Optional[float] = typer.Option(None, help="Width dimension (inches)"),
    height: Optional[float] = typer.Option(None, help="Height dimension (inches)"),
    thickness: Optional[float] = typer.Option(None, help="Thickness dimension (inches)"),
    diameter: Optional[float] = typer.Option(None, help="Diameter (inches)"),
):
    """Calculate steel weight and cost."""
    calculator = SteelCalculator()
    
    # Prepare dimensions based on steel type
    dimensions = {}
    if steel_type.lower() == "rebar" and bar_number:
        dimensions = {"bar_number": bar_number}
    elif width and height and thickness:
        dimensions = {"width": width, "height": height, "thickness": thickness}
    elif diameter:
        dimensions = {"diameter": diameter}
    
    # Calculate weight
    result = calculator.calculate_weight(
        steel_type=steel_type,
        dimensions=dimensions,
        length=length,
        quantity=quantity,
        length_unit=length_unit
    )
    
    # Calculate cost if grade is provided
    cost = None
    if grade:
        cost = calculator.calculate_cost(
            weight=result,
            steel_type=steel_type,
            grade=grade,
            price_per_pound=price_per_pound
        )
    
    table = Table(title="Steel Calculation Results")
    table.add_column("Measurement")
    table.add_column("Value")
    
    table.add_row("Steel Type", steel_type)
    if bar_number:
        table.add_row("Bar Number", f"#{bar_number}")
    if width and height:
        table.add_row("Dimensions", f"{width}\"×{height}\"×{thickness}\"")
    if diameter:
        table.add_row("Diameter", f"{diameter}\"")
    table.add_row("Length", f"{length} {length_unit}")
    table.add_row("Quantity", str(quantity))
    table.add_row("Weight Per Foot", f"{result['weight_per_foot']} lb/ft")
    table.add_row("Total Weight", f"{result['weight']} {result['weight_unit']}")
    if cost:
        table.add_row("Cost", f"${cost:.2f}")
    
    console.print(table)
    
    if output:
        import csv
        with open(output, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Measurement", "Value"])
            writer.writerow(["Steel Type", steel_type])
            if bar_number:
                writer.writerow(["Bar Number", f"#{bar_number}"])
            if width and height:
                writer.writerow(["Dimensions", f"{width}\"×{height}\"×{thickness}\""])
            if diameter:
                writer.writerow(["Diameter", f"{diameter}\""])
            writer.writerow(["Length", f"{length} {length_unit}"])
            writer.writerow(["Quantity", quantity])
            writer.writerow(["Weight Per Foot", f"{result['weight_per_foot']} lb/ft"])
            writer.writerow(["Total Weight", f"{result['weight']} {result['weight_unit']}"])
            if cost:
                writer.writerow(["Cost", f"${cost:.2f}"])
        console.print(f"Results saved to {output}")

# Version command
@app.command()
def version():
    """Display the version of BuildWise CLI."""
    import buildwise
    version = getattr(buildwise, "__version__", "0.1.0")
    console.print(f"BuildWise CLI v{version}")

if __name__ == "__main__":
    app()

# Settings command
@app.command()
def settings(
    list: bool = typer.Option(False, "--list", help="List current settings"),
    openai_key: Optional[str] = typer.Option(None, "--openai-key", help="Set OpenAI API key"),
    project_dir: Optional[str] = typer.Option(None, "--project-dir", help="Set project directory"),
    location: Optional[str] = typer.Option(None, "--location", help="Set default location"),
    price_concrete: Optional[float] = typer.Option(None, "--price-concrete", help="Set default concrete price per cubic yard"),
    price_lumber: Optional[float] = typer.Option(None, "--price-lumber", help="Set default lumber price per board foot"),
    price_steel: Optional[float] = typer.Option(None, "--price-steel", help="Set default steel price per pound"),
):
    """View or modify application settings."""
    from buildwise.config.settings import settings
    
    # Update settings if provided
    if openai_key:
        settings.openai_api_key = openai_key
        console.print("[green]Updated OpenAI API key[/green]")
    
    if project_dir:
        settings.project_dir = project_dir
        console.print(f"[green]Updated project directory to: {project_dir}[/green]")
    
    if location:
        settings.default_location = location
        console.print(f"[green]Updated default location to: {location}[/green]")
    
    if price_concrete:
        settings.update_material_price("concrete_per_yard", price_concrete)
        console.print(f"[green]Updated concrete price to: ${price_concrete}/cubic yard[/green]")
    
    if price_lumber:
        settings.update_material_price("lumber_pine_per_bf", price_lumber)
        console.print(f"[green]Updated lumber price to: ${price_lumber}/board foot[/green]")
    
    if price_steel:
        settings.update_material_price("steel_per_pound", price_steel)
        console.print(f"[green]Updated steel price to: ${price_steel}/pound[/green]")
    
    # List current settings
    if list or not any([openai_key, project_dir, location, price_concrete, price_lumber, price_steel]):
        table = Table(title="Current Settings")
        table.add_column("Setting")
        table.add_column("Value")
        
        all_settings = settings.to_dict()
        
        # Format API key for display
        api_key = all_settings.get("openai_api_key", "")
        if api_key:
            display_key = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "****"
        else:
            display_key = "[not set]"
        
        table.add_row("OpenAI API Key", display_key)
        table.add_row("Project Directory", all_settings.get("project_dir", ""))
        table.add_row("Default Location", all_settings.get("default_location", ""))
        
        # Material prices
        material_prices = all_settings.get("material_prices", {})
        table.add_row("Concrete Price (per cubic yard)", f"${material_prices.get('concrete_per_yard', 0):.2f}")
        table.add_row("Lumber Price (pine, per board foot)", f"${material_prices.get('lumber_pine_per_bf', 0):.2f}")
        table.add_row("Steel Price (per pound)", f"${material_prices.get('steel_per_pound', 0):.2f}")
        
        console.print(table)

# Project command
@app.command()
def project(
    list: bool = typer.Option(False, "--list", help="List all projects"),
    create: bool = typer.Option(False, "--create", help="Create a new project"),
    view: Optional[str] = typer.Option(None, "--view", help="View a project by name"),
    delete: Optional[str] = typer.Option(None, "--delete", help="Delete a project by name"),
    add_material: Optional[str] = typer.Option(None, "--add-material", help="Add material to a project"),
    export: Optional[str] = typer.Option(None, "--export", help="Export project to CSV"),
):
    """Manage construction projects."""
    from buildwise.storage.project import ProjectStorage, ProjectMaterial
    
    storage = ProjectStorage()
    
    # Delete project
    if delete:
        if storage.delete_project(delete):
            console.print(f"[green]Deleted project: {delete}[/green]")
        else:
            console.print(f"[red]Project not found: {delete}[/red]")
        return
    
    # Create new project
    if create:
        name = typer.prompt("Project name")
        description = typer.prompt("Description (optional)", default="")
        location = typer.prompt("Location (optional)", default="")
        
        project = storage.create_project(name=name, description=description, location=location)
        console.print(f"[green]Created project: {project.name}[/green]")
        return
    
    # Add material to project
    if add_material:
        project = storage.load_project(add_material)
        if not project:
            console.print(f"[red]Project not found: {add_material}[/red]")
            return
        
        material_type = typer.prompt("Material type (concrete, lumber, steel)")
        name = typer.prompt("Material name")
        quantity = float(typer.prompt("Quantity"))
        unit = typer.prompt("Unit")
        cost = float(typer.prompt("Cost", default="0"))
        notes = typer.prompt("Notes (optional)", default="")
        
        material = ProjectMaterial(
            material_type=material_type,
            name=name,
            quantity=quantity,
            unit=unit,
            cost=cost,
            notes=notes
        )
        
        project.add_material(material)
        storage.save_project(project)
        
        console.print(f"[green]Added material to project: {project.name}[/green]")
        return
    
    # Export project to CSV
    if export:
        project = storage.load_project(export)
        if not project:
            console.print(f"[red]Project not found: {export}[/red]")
            return
        
        file_name = f"{project.name.replace(' ', '_')}_export.csv"
        
        import csv
        with open(file_name, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Project", project.name])
            writer.writerow(["Description", project.description or ""])
            writer.writerow(["Location", project.location or ""])
            writer.writerow(["Created", project.created_at])
            writer.writerow([])
            
            writer.writerow(["Materials"])
            writer.writerow(["Type", "Name", "Quantity", "Unit", "Cost", "Notes"])
            
            for material in project.materials:
                writer.writerow([
                    material.material_type,
                    material.name,
                    material.quantity,
                    material.unit,
                    material.cost or 0,
                    material.notes or ""
                ])
            
            writer.writerow([])
            writer.writerow(["Total Cost", project.total_cost])
        
        console.print(f"[green]Exported project to: {file_name}[/green]")
        return
    
    # View project
    if view:
        project = storage.load_project(view)
        if not project:
            console.print(f"[red]Project not found: {view}[/red]")
            return
        
        table = Table(title=f"Project: {project.name}")
        table.add_column("Property")
        table.add_column("Value")
        
        table.add_row("Description", project.description or "")
        table.add_row("Location", project.location or "")
        table.add_row("Created", project.created_at)
        table.add_row("Total Cost", f"${project.total_cost:.2f}")
        
        console.print(table)
        
        if project.materials:
            materials_table = Table(title="Materials")
            materials_table.add_column("Type")
            materials_table.add_column("Name")
            materials_table.add_column("Quantity")
            materials_table.add_column("Unit")
            materials_table.add_column("Cost")
            
            for material in project.materials:
                materials_table.add_row(
                    material.material_type,
                    material.name,
                    str(material.quantity),
                    material.unit,
                    f"${material.cost:.2f}" if material.cost else "N/A"
                )
            
            console.print(materials_table)
        else:
            console.print("[yellow]No materials added yet[/yellow]")
        
        return
    
    # List projects
    if list or not any([create, view, delete, add_material, export]):
        projects = storage.list_projects()
        
        if not projects:
            console.print("[yellow]No projects found[/yellow]")
            return
        
        table = Table(title="Projects")
        table.add_column("Name")
        table.add_column("Description")
        table.add_column("Location")
        table.add_column("Materials")
        
        for project in projects:
            table.add_row(
                project["name"],
                project.get("description", ""),
                project.get("location", ""),
                str(project.get("material_count", 0))
            )
        
        console.print(table)

# AI Estimate command
@app.command("ai-estimate")
def ai_estimate(
    material_type: str = typer.Option(..., help="Type of material (concrete, lumber, etc.)"),
    quantity: float = typer.Option(..., help="Amount of material"),
    unit: str = typer.Option("cubic_yard", help="Unit of measurement"),
    location: str = typer.Option("United States", help="Geographic location for pricing"),
    api_key: Optional[str] = typer.Option(None, help="OpenAI API key (or set OPENAI_API_KEY env var)"),
):
    """Generate AI-powered material cost estimates."""
    from buildwise.services.ai_prediction import AIPredictionService
    
    # Initialize service
    service = AIPredictionService(api_key=api_key)
    
    # Check if service is available
    if not service.is_available():
        console.print("[yellow]AI service is not available, using fallback predictions[/yellow]")
    
    # Make prediction
    prediction = service.predict_material_cost(
        material_type=material_type,
        quantity={unit: quantity},
        location=location
    )
    
    # Display results
    table = Table(title="AI Cost Estimation")
    table.add_column("Measurement")
    table.add_column("Value")
    
    table.add_row("Material Type", material_type)
    table.add_row("Quantity", f"{quantity} {unit}")
    table.add_row("Location", location)
    table.add_row("Estimated Cost", f"${prediction['estimated_cost']:.2f}")
    table.add_row("Price Range", f"${prediction['min_cost']:.2f} - ${prediction['max_cost']:.2f}")
    table.add_row("Confidence", f"{prediction['confidence'] * 100:.0f}%")
    table.add_row("Source", prediction['source'])
    
    console.print(table)

# Lumber Project command
@app.command("lumber-project")
def lumber_project(
    lumber_type: str = typer.Option("pine", help="Type of lumber"),
    grade: str = typer.Option("no.2", help="Grade of lumber"),
    length_unit: str = typer.Option("feet", help="Unit for length measurements"),
    waste_factor: float = typer.Option(0.1, help="Waste factor (0.1 = 10%)"),
    interactive: bool = typer.Option(False, help="Interactive mode to enter multiple pieces"),
    output: Optional[str] = typer.Option(None, help="Output file for results (CSV)"),
):
    """Calculate lumber requirements for a project with multiple pieces."""
    from buildwise.core.lumber import LumberCalculator
    
    calculator = LumberCalculator()
    dimensions = []
    
    if interactive:
        console.print("[bold]Enter lumber pieces (width, thickness, length, quantity)[/bold]")
        console.print("Enter 'done' when finished")
        
        while True:
            input_str = typer.prompt("Enter piece (e.g., 4 2 8 10 for 10 pieces of 2x4x8')")
            if input_str.lower() == 'done':
                break
            
            try:
                parts = input_str.split()
                if len(parts) != 4:
                    console.print("[red]Invalid format. Please enter 4 values: width thickness length quantity[/red]")
                    continue
                
                width = float(parts[0])
                thickness = float(parts[1])
                length = float(parts[2])
                quantity = int(parts[3])
                
                dimensions.append((width, thickness, length, quantity))
                console.print(f"Added: {quantity} pieces of {thickness}×{width}×{length}'")
            except ValueError:
                console.print("[red]Invalid input. Please enter numeric values.[/red]")
    else:
        console.print("[yellow]No dimensions provided. Use --interactive to enter pieces.[/yellow]")
        return
    
    if not dimensions:
        console.print("[yellow]No dimensions added. Exiting.[/yellow]")
        return
    
    # Calculate project
    result = calculator.calculate_project(
        dimensions=dimensions,
        lumber_type=lumber_type,
        grade=grade,
        waste_factor=waste_factor
    )
    
    # Display results
    table = Table(title="Lumber Project Calculation")
    table.add_column("Measurement")
    table.add_column("Value")
    
    table.add_row("Lumber Type", lumber_type)
    table.add_row("Grade", grade)
    table.add_row("Total Board Feet", str(result["total_board_feet"]))
    table.add_row("Waste Factor", f"{waste_factor * 100:.0f}%")
    table.add_row("Total with Waste", str(result["total_with_waste"]))
    table.add_row("Total Cost", f"${result['total_cost']:.2f}")
    
    console.print(table)
    
    # Display pieces
    pieces_table = Table(title="Lumber Pieces")
    pieces_table.add_column("Dimensions")
    pieces_table.add_column("Quantity")
    pieces_table.add_column("Board Feet")
    
    for piece in result["pieces"]:
        pieces_table.add_row(
            piece["dimensions"],
            str(piece["quantity"]),
            str(piece["board_feet"])
        )
    
    console.print(pieces_table)
    
    # Save to CSV if requested
    if output:
        import csv
        with open(output, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Lumber Project Calculation"])
            writer.writerow(["Lumber Type", lumber_type])
            writer.writerow(["Grade", grade])
            writer.writerow(["Total Board Feet", result["total_board_feet"]])
            writer.writerow(["Waste Factor", f"{waste_factor * 100:.0f}%"])
            writer.writerow(["Total with Waste", result["total_with_waste"]])
            writer.writerow(["Total Cost", f"${result['total_cost']:.2f}"])
            writer.writerow([])
            
            writer.writerow(["Pieces"])
            writer.writerow(["Dimensions", "Quantity", "Board Feet"])
            for piece in result["pieces"]:
                writer.writerow([
                    piece["dimensions"],
                    piece["quantity"],
                    piece["board_feet"]
                ])
        
        console.print(f"[green]Results saved to {output}[/green]")

# Dashboard command
@app.command()
def dashboard(
    host: str = typer.Option("127.0.0.1", help="Host to bind to"),
    port: int = typer.Option(8000, help="Port to bind to"),
):
    """Launch the web dashboard."""
    import uvicorn
    from buildwise.api.main import app as fastapi_app
    
    console.print(f"[green]Starting BuildWise dashboard at http://{host}:{port}[/green]")
    console.print("Press Ctrl+C to stop")
    
    try:
        uvicorn.run(fastapi_app, host=host, port=port)
    except KeyboardInterrupt:
        console.print("[yellow]Dashboard stopped[/yellow]")
