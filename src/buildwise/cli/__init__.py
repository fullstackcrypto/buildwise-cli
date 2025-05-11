"""BuildWise CLI - Command line interface."""

import csv
from typing import List, Optional, Tuple

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from buildwise.core.concrete import ConcreteCalculator

# Initialize Typer app
app = typer.Typer(
    name="buildwise",
    help="BuildWise CLI - Intelligent construction calculator suite",
    add_completion=True,
)

# Initialize console for rich output
console = Console()


@app.command()
def concrete(
    length: float = typer.Option(..., help="Length of the area"),
    width: float = typer.Option(..., help="Width of the area"),
    depth: float = typer.Option(..., help="Depth of the concrete"),
    unit: str = typer.Option("feet", help="Unit of measurement (feet, meters, etc.)"),
    price_per_unit: float = typer.Option(None, help="Price per cubic yard/meter"),
    bag_size: float = typer.Option(None, help="Bag size (80lb, 60lb, 50kg, etc.)"),
    bag_unit: str = typer.Option("lb", help="Bag unit (lb, kg)"),
    output: str = typer.Option(None, help="Output file for results (CSV)"),
    detail: bool = typer.Option(False, help="Show detailed information"),
):
    """Calculate concrete volume, cost, and materials needed."""
    calculator = ConcreteCalculator()
    volume = calculator.calculate_volume(length, width, depth, unit)
    
    # Create results table
    table = Table(title="Concrete Calculation Results")
    table.add_column("Measurement")
    table.add_column("Value")
    
    # Add basic information
    table.add_row("Length", f"{length} {unit}")
    table.add_row("Width", f"{width} {unit}")
    table.add_row("Depth", f"{depth} {unit}")
    table.add_row("Volume (cubic yards)", str(volume["cubic_yards"]))
    table.add_row("Volume (cubic meters)", str(volume["cubic_meters"]))
    
    # Add cost if price is provided
    if price_per_unit is not None:
        cost = calculator.calculate_cost(volume, price_per_unit)
        table.add_row("Cost", f"${cost:.2f}")
    
    # Calculate bags if size is provided
    if bag_size is not None:
        bags = calculator.bags_needed(volume, bag_size, bag_unit)
        table.add_row(f"Bags needed ({bag_size}{bag_unit})", str(bags))
    
    # Print the table
    console.print(table)
    
    # Show detailed information if requested
    if detail:
        console.print("\n[bold]Detailed Information:[/bold]")
        console.print(f"Volume in cubic feet: {volume['raw_volume'].to('foot**3').magnitude:.2f}")
        console.print(f"Volume in cubic inches: {volume['raw_volume'].to('inch**3').magnitude:.2f}")
        
        if price_per_unit is not None:
            cost_per_cuft = calculator.calculate_cost(volume['raw_volume'].to('foot**3'), price_per_unit / 27)
            console.print(f"Cost per cubic foot: ${cost_per_cuft:.2f}")
    
    # Save to CSV if output file is specified
    if output:
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
                writer.writerow([f"Bags needed ({bag_size}{bag_unit})", bags])
        
        console.print(f"Results saved to [bold]{output}[/bold]")


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
    output: str = typer.Option(None, help="Output file for results (CSV)"),
    detail: bool = typer.Option(False, help="Show detailed information"),
):
    """Calculate lumber board feet and cost."""
    from buildwise.core.lumber import LumberCalculator
    
    calculator = LumberCalculator()
    
    # Calculate board feet
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
    
    # Create results table
    table = Table(title=f"Lumber Calculation Results ({quantity} piece{'s' if quantity > 1 else ''})")
    table.add_column("Measurement")
    table.add_column("Value")
    
    # Add basic information
    table.add_row("Nominal Size", f"{thickness}\"×{width}\"×{length} {length_unit}")
    table.add_row("Actual Size", f"{result['actual_thickness']}\"×{result['actual_width']}\"×{length} {length_unit}")
    table.add_row("Board Feet", str(result["board_feet"]))
    table.add_row("Lumber Type", lumber_type.capitalize())
    table.add_row("Grade", grade.upper() if grade.startswith("no.") else grade.capitalize())
    table.add_row("Cost", f"${cost:.2f}")
    
    # Print the table
    console.print(table)
    
    # Show detailed information if requested
    if detail:
        console.print("\n[bold]Detailed Information:[/bold]")
        bf_per_piece = result["board_feet"] / quantity if quantity > 0 else 0
        console.print(f"Board feet per piece: {bf_per_piece:.2f}")
        
        # Display volume
        console.print(f"Volume in cubic feet: {result['volume'].to('foot**3').magnitude:.2f}")
    
    # Save to CSV if output file is specified
    if output:
        with open(output, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Measurement", "Value"])
            writer.writerow(["Nominal Size", f"{thickness}\"×{width}\"×{length} {length_unit}"])
            writer.writerow(["Actual Size", f"{result['actual_thickness']}\"×{result['actual_width']}\"×{length} {length_unit}"])
            writer.writerow(["Board Feet", str(result["board_feet"])])
            writer.writerow(["Lumber Type", lumber_type.capitalize()])
            writer.writerow(["Grade", grade.upper() if grade.startswith("no.") else grade.capitalize()])
            writer.writerow(["Cost", f"${cost:.2f}"])
        
        console.print(f"Results saved to [bold]{output}[/bold]")


@app.command(name="lumber-project")
def lumber_project(
    lumber_type: str = typer.Option("pine", help="Type of lumber"),
    grade: str = typer.Option("no.2", help="Grade of lumber"),
    length_unit: str = typer.Option("feet", help="Unit for length measurements"),
    waste_factor: float = typer.Option(0.1, help="Waste factor (0.1 = 10%)"),
    interactive: bool = typer.Option(False, help="Interactive mode to enter multiple pieces"),
    output: str = typer.Option(None, help="Output file for results (CSV)"),
):
    """Calculate lumber requirements for a project with multiple pieces."""
    from buildwise.core.lumber import LumberCalculator
    
    calculator = LumberCalculator()
    dimensions = []
    
    if interactive:
        console.print(Panel.fit("Interactive Lumber Project Calculator", 
                               title="BuildWise CLI", 
                               subtitle="Enter lumber dimensions"))
        
        # Show standard sizes for reference
        standard_sizes = calculator.get_standard_sizes()
        size_table = Table(title="Common Lumber Sizes")
        size_table.add_column("Description")
        size_table.add_column("Nominal Size")
        
        for size in standard_sizes["dimensional_lumber"]:
            size_table.add_row(
                size["description"],
                f"{size['thickness']}\" × {size['width']}\""
            )
        
        console.print(size_table)
        console.print("\nStandard lengths (feet): " + ", ".join(str(l) for l in standard_sizes["standard_lengths"]))
        
        # Enter dimensions interactively
        while True:
            console.print("\nEnter lumber piece details (or 'done' to finish):")
            
            # Check if user wants to exit
            thickness_input = typer.prompt("Thickness (inches)")
            if thickness_input.lower() == 'done':
                break
                
            try:
                thickness = float(thickness_input)
                width = float(typer.prompt("Width (inches)"))
                length = float(typer.prompt("Length (feet)"))
                quantity = int(typer.prompt("Quantity", default="1"))
                
                dimensions.append((width, thickness, length, quantity))
                
                console.print(f"Added: {thickness}\"×{width}\"×{length}' × {quantity}")
            except ValueError:
                console.print("[red]Invalid input. Please enter numeric values.[/red]")
    else:
        # Example for demonstration when not in interactive mode
        console.print("[yellow]No dimensions provided. Using example project.[/yellow]")
        dimensions = [
            (4, 2, 8, 10),    # 10 pieces of 2x4x8'
            (6, 2, 10, 6),    # 6 pieces of 2x6x10'
            (12, 2, 16, 2),   # 2 pieces of 2x12x16'
        ]
    
    if not dimensions:
        console.print("[red]No lumber specified. Exiting.[/red]")
        return
    
    # Calculate project
    result = calculator.calculate_project(
        dimensions=dimensions,
        lumber_type=lumber_type,
        grade=grade,
        length_unit=length_unit,
        waste_factor=waste_factor
    )
    
    # Create summary table
    table = Table(title="Lumber Project Summary")
    table.add_column("Item")
    table.add_column("Value")
    
    table.add_row("Total Board Feet", str(result["board_feet"]))
    table.add_row("Waste Factor", f"{waste_factor * 100:.0f}%")
    table.add_row("Board Feet with Waste", str(result["board_feet_with_waste"]))
    table.add_row("Lumber Type", lumber_type.capitalize())
    table.add_row("Grade", grade.upper() if grade.startswith("no.") else grade.capitalize())
    table.add_row("Total Cost", f"${result['cost']:.2f}")
    
    console.print(table)
    
    # Show detailed breakdown
    details_table = Table(title="Detailed Breakdown")
    details_table.add_column("Size")
    details_table.add_column("Quantity")
    details_table.add_column("Board Feet")
    
    for i, (width, thickness, length, quantity) in enumerate(dimensions):
        calc = result["calculations"][i]
        details_table.add_row(
            f"{thickness}\"×{width}\"×{length}'",
            str(quantity),
            str(calc["board_feet"])
        )
    
    console.print(details_table)
    
    # Save to CSV if output file is specified
    if output:
        with open(output, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Item", "Value"])
            writer.writerow(["Total Board Feet", str(result["board_feet"])])
            writer.writerow(["Waste Factor", f"{waste_factor * 100:.0f}%"])
            writer.writerow(["Board Feet with Waste", str(result["board_feet_with_waste"])])
            writer.writerow(["Lumber Type", lumber_type.capitalize()])
            writer.writerow(["Grade", grade.upper() if grade.startswith("no.") else grade.capitalize()])
            writer.writerow(["Total Cost", f"${result['cost']:.2f}"])
            
            writer.writerow([])
            writer.writerow(["Size", "Quantity", "Board Feet"])
            
            for i, (width, thickness, length, quantity) in enumerate(dimensions):
                calc = result["calculations"][i]
                writer.writerow([
                    f"{thickness}\"×{width}\"×{length}'",
                    str(quantity),
                    str(calc["board_feet"])
                ])
        
        console.print(f"Results saved to [bold]{output}[/bold]")


@app.command(name="ai-estimate")
def ai_estimate(
    material_type: str = typer.Option(..., help="Type of material (concrete, lumber, etc.)"),
    quantity: float = typer.Option(..., help="Amount of material"),
    unit: str = typer.Option("cubic_yard", help="Unit of measurement"),
    location: str = typer.Option("United States", help="Geographic location for pricing"),
    api_key: Optional[str] = typer.Option(None, help="OpenAI API key (or set OPENAI_API_KEY env var)"),
):
    """Generate AI-powered material cost estimates."""
    from buildwise.services.ai_prediction import AIPredictionService
    
    # Create AI service
    ai_service = AIPredictionService(api_key=api_key)
    
    if not ai_service.is_available():
        console.print("[yellow]Warning: OpenAI API is not available. Using fallback estimates.[/yellow]")
        console.print("[yellow]To use AI-powered estimates, install the OpenAI package and set your API key.[/yellow]")
    
    # Prepare quantity with appropriate unit
    if unit == "cubic_yard" or unit == "cubic_yards":
        quantity_obj = {"cubic_yards": quantity}
    elif unit == "board_foot" or unit == "board_feet":
        quantity_obj = {"board_feet": quantity}
    else:
        quantity_obj = quantity
    
    # Get prediction
    prediction = ai_service.predict_material_cost(
        material_type=material_type,
        quantity=quantity_obj,
        location=location
    )
    
    # Create results table
    table = Table(title=f"AI Cost Estimation for {material_type.capitalize()}")
    table.add_column("Item")
    table.add_column("Value")
    
    # Add results
    table.add_row("Material", material_type.capitalize())
    table.add_row("Quantity", f"{quantity} {unit}")
    table.add_row("Location", location)
    table.add_row("Estimated Cost", f"${prediction['estimated_cost']:.2f}")
    table.add_row("Cost Range", f"${prediction['min_cost']:.2f} - ${prediction['max_cost']:.2f}")
    table.add_row("Confidence Level", prediction["confidence_level"].capitalize())
    table.add_row("Source", prediction["source"].capitalize())
    
    # Print the table
    console.print(table)
    
    # Show factors
    console.print("\n[bold]Factors Affecting Price:[/bold]")
    for factor in prediction["factors"]:
        console.print(f"• {factor}")
    
    if prediction["source"] == "fallback":
        console.print("\n[yellow]Note: This is a fallback estimate. For more accurate results, use OpenAI API.[/yellow]")


@app.command()
def steel():
    """Calculate steel requirements (Coming soon)."""
    console.print("[yellow]Steel calculator coming soon in a future update![/yellow]")


@app.command()
def estimate():
    """Generate AI-powered cost estimates (Coming soon)."""
    console.print("[yellow]AI-powered estimation coming soon in a future update![/yellow]")


@app.command()
def project():
    """Manage construction projects (Coming soon)."""
    console.print("[yellow]Project management coming soon in a future update![/yellow]")


@app.command()
def version():
    """Display the version of BuildWise CLI."""
    from buildwise import __version__
    console.print(f"BuildWise CLI v{__version__}")


@app.command()
def steel(
    steel_type: str = typer.Option("rebar", help="Type of steel"),
    length: float = typer.Option(..., help="Length of the steel"),
    length_unit: str = typer.Option("feet", help="Unit for length (feet, meters)"),
    quantity: int = typer.Option(1, help="Number of pieces"),
    grade: str = typer.Option(None, help="Grade of steel"),
    price_per_pound: float = typer.Option(None, help="Custom price per pound"),
    output: str = typer.Option(None, help="Output file for results (CSV)"),
    detail: bool = typer.Option(False, help="Show detailed information"),
):
    """Calculate steel weight and cost."""
    from buildwise.core.steel import SteelCalculator, SteelType
    
    calculator = SteelCalculator()
    
    # Set up dimensions based on steel type
    dimensions = {}
    
    # Check if steel type is a standard type
    steel_type_lower = steel_type.lower().replace(" ", "_")
    if steel_type_lower == "rebar":
        # Prompt for bar number
        bar_number = typer.prompt("Bar number (3-11)", default="4")
        try:
            bar_number = int(bar_number)
            dimensions["bar_number"] = bar_number
        except ValueError:
            console.print("[red]Invalid bar number. Using #4 as default.[/red]")
            dimensions["bar_number"] = 4
    
    elif steel_type_lower in ["angle", "angle_iron", "l_shape"]:
        width = typer.prompt("Width (inches)", default="3")
        height = typer.prompt("Height (inches)", default="3")
        thickness = typer.prompt("Thickness (inches)", default="0.25")
        try:
            dimensions["width"] = float(width)
            dimensions["height"] = float(height)
            dimensions["thickness"] = float(thickness)
        except ValueError:
            console.print("[red]Invalid dimensions. Using 3×3×1/4 as default.[/red]")
            dimensions["width"] = 3
            dimensions["height"] = 3
            dimensions["thickness"] = 0.25
    
    elif steel_type_lower in ["hss_round", "pipe", "round_tube", "tube", "tubing"]:
        diameter = typer.prompt("Diameter (inches)", default="4")
        wall_thickness = typer.prompt("Wall thickness (inches)", default="0.25")
        try:
            dimensions["diameter"] = float(diameter)
            dimensions["wall_thickness"] = float(wall_thickness)
        except ValueError:
            console.print("[red]Invalid dimensions. Using 4\" diameter, 0.25\" wall as default.[/red]")
            dimensions["diameter"] = 4
            dimensions["wall_thickness"] = 0.25
    
    elif steel_type_lower in ["channel", "c_shape"]:
        width = typer.prompt("Width (inches)", default="3")
        height = typer.prompt("Height (inches)", default="5")
        thickness = typer.prompt("Thickness (inches)", default="0.25")
        try:
            dimensions["width"] = float(width)
            dimensions["height"] = float(height)
            dimensions["thickness"] = float(thickness)
        except ValueError:
            console.print("[red]Invalid dimensions. Using 3×5×0.25 as default.[/red]")
            dimensions["width"] = 3
            dimensions["height"] = 5
            dimensions["thickness"] = 0.25
    
    elif steel_type_lower in ["wide_flange", "i_beam", "beam"]:
        flange_width = typer.prompt("Flange width (inches)", default="6")
        web_height = typer.prompt("Web height (inches)", default="8")
        flange_thickness = typer.prompt("Flange thickness (inches)", default="0.5")
        web_thickness = typer.prompt("Web thickness (inches)", default="0.25")
        try:
            dimensions["flange_width"] = float(flange_width)
            dimensions["web_height"] = float(web_height)
            dimensions["flange_thickness"] = float(flange_thickness)
            dimensions["web_thickness"] = float(web_thickness)
        except ValueError:
            console.print("[red]Invalid dimensions. Using W6×8 as default.[/red]")
            dimensions["flange_width"] = 6
            dimensions["web_height"] = 8
            dimensions["flange_thickness"] = 0.5
            dimensions["web_thickness"] = 0.25
    
    else:
        console.print(f"[yellow]Unknown steel type: {steel_type}. Using rebar as default.[/yellow]")
        steel_type = "rebar"
        dimensions["bar_number"] = 4
    
    # Calculate weight
    result = calculator.calculate_weight(
        steel_type=steel_type,
        dimensions=dimensions,
        length=length,
        quantity=quantity,
        length_unit=length_unit
    )
    
    # Calculate cost
    cost = calculator.calculate_cost(
        weight=result,
        steel_type=steel_type,
        grade=grade,
        price_per_pound=price_per_pound
    )
    
    # Create results table
    table = Table(title=f"Steel Calculation Results ({quantity} piece{'s' if quantity > 1 else ''})")
    table.add_column("Measurement")
    table.add_column("Value")
    
    # Add basic information
    table.add_row("Steel Type", steel_type.capitalize())
    if grade:
        table.add_row("Grade", grade.upper())
    
    # Add dimensions based on steel type
    if steel_type_lower == "rebar":
        table.add_row("Bar Number", f"#{dimensions['bar_number']}")
        props = calculator.get_rebar_properties(dimensions["bar_number"])
        table.add_row("Diameter", f"{props['diameter']:.3f} inches")
    elif "diameter" in dimensions:
        table.add_row("Diameter", f"{dimensions['diameter']} inches")
        if "wall_thickness" in dimensions:
            table.add_row("Wall Thickness", f"{dimensions['wall_thickness']} inches")
    elif "width" in dimensions and "height" in dimensions:
        if "thickness" in dimensions:
            table.add_row("Dimensions", f"{dimensions['width']}\"×{dimensions['height']}\"×{dimensions['thickness']}\"")
        else:
            table.add_row("Width", f"{dimensions['width']} inches")
            table.add_row("Height", f"{dimensions['height']} inches")
    
    # Add length information
    table.add_row("Length", f"{length} {length_unit}")
    table.add_row("Weight per Piece", f"{result['weight_per_foot']:.2f} lb/ft")
    table.add_row("Total Weight", f"{result['weight_pounds']:.2f} lb")
    table.add_row("Cost", f"${cost:.2f}")
    
    # Print the table
    console.print(table)
    
    # Show detailed information if requested
    if detail:
        console.print("\n[bold]Detailed Information:[/bold]")
        console.print(f"Cross-sectional area: {result['area_sq_inches']:.4f} square inches")
        
        if price_per_pound is not None:
            console.print(f"Price per pound: ${price_per_pound:.2f}")
        
        # Additional info based on steel type
        if steel_type_lower == "rebar":
            props = calculator.get_rebar_properties(dimensions["bar_number"])
            console.print(f"Standard weight per foot: {props['weight_per_foot']:.3f} lb/ft")
            console.print(f"Cross-sectional area: {props['area_sq_inches']:.2f} square inches")
    
    # Save to CSV if output file is specified
    if output:
        with open(output, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Measurement", "Value"])
            writer.writerow(["Steel Type", steel_type.capitalize()])
            if grade:
                writer.writerow(["Grade", grade.upper()])
            
            # Add dimensions
            for key, value in dimensions.items():
                writer.writerow([key.replace("_", " ").title(), str(value)])
            
            writer.writerow(["Length", f"{length} {length_unit}"])
            writer.writerow(["Weight per Piece", f"{result['weight_per_foot']:.2f} lb/ft"])
            writer.writerow(["Total Weight", f"{result['weight_pounds']:.2f} lb"])
            writer.writerow(["Cost", f"${cost:.2f}"])
        
        console.print(f"Results saved to [bold]{output}[/bold]")


@app.command()
def project(
    list: bool = typer.Option(False, "--list", help="List all projects"),
    create: bool = typer.Option(False, "--create", help="Create a new project"),
    view: str = typer.Option(None, "--view", help="View a project by name"),
    delete: str = typer.Option(None, "--delete", help="Delete a project by name"),
    add_material: str = typer.Option(None, "--add-material", help="Add material to a project"),
    export: str = typer.Option(None, "--export", help="Export project to CSV"),
):
    """Manage construction projects."""
    from buildwise.storage.project import ProjectStorage, Project, ProjectMaterial, MaterialType
    
    # Initialize storage
    storage = ProjectStorage()
    
    # List projects
    if list:
        projects = storage.list_projects()
        
        if not projects:
            console.print("[yellow]No projects found.[/yellow]")
            return
        
        # Create table
        table = Table(title="Construction Projects")
        table.add_column("Name")
        table.add_column("Description")
        table.add_column("Location")
        table.add_column("Materials")
        table.add_column("Total Cost")
        table.add_column("Last Updated")
        
        for project in projects:
            table.add_row(
                project["name"],
                project.get("description", ""),
                project.get("location", ""),
                str(project.get("material_count", 0)),
                f"${project.get('total_cost', 0):.2f}" if project.get("total_cost") else "N/A",
                project.get("updated_at", "").split("T")[0]  # Just the date
            )
        
        console.print(table)
        return
    
    # Create a new project
    if create:
        name = typer.prompt("Project name")
        description = typer.prompt("Description", default="")
        location = typer.prompt("Location", default="")
        
        project = storage.create_project(
            name=name,
            description=description,
            location=location
        )
        
        console.print(f"[green]Project '{name}' created successfully.[/green]")
        return
    
    # View a project
    if view:
        project = storage.load_project(view)
        
        if not project:
            console.print(f"[red]Project '{view}' not found.[/red]")
            return
        
        # Create summary table
        table = Table(title=f"Project: {project.name}")
        table.add_column("Property")
        table.add_column("Value")
        
        table.add_row("Description", project.description or "")
        table.add_row("Location", project.location or "")
        table.add_row("Created", project.created_at.split("T")[0])  # Just the date
        table.add_row("Updated", project.updated_at.split("T")[0])  # Just the date
        table.add_row("Materials", str(len(project.materials)))
        table.add_row("Total Cost", f"${project.total_cost:.2f}" if project.total_cost else "N/A")
        
        console.print(table)
        
        # Show materials if any
        if project.materials:
            materials_table = Table(title="Materials")
            materials_table.add_column("Type")
            materials_table.add_column("Name")
            materials_table.add_column("Quantity")
            materials_table.add_column("Unit")
            materials_table.add_column("Cost")
            materials_table.add_column("Notes")
            
            for material in project.materials:
                materials_table.add_row(
                    material.material_type.capitalize(),
                    material.name,
                    str(material.quantity),
                    material.unit,
                    f"${material.cost:.2f}" if material.cost else "N/A",
                    material.notes or ""
                )
            
            console.print(materials_table)
        else:
            console.print("[yellow]No materials in this project yet.[/yellow]")
        
        return
    
    # Delete a project
    if delete:
        if typer.confirm(f"Are you sure you want to delete project '{delete}'?"):
            success = storage.delete_project(delete)
            
            if success:
                console.print(f"[green]Project '{delete}' deleted.[/green]")
            else:
                console.print(f"[red]Project '{delete}' not found.[/red]")
        return
    
    # Add material to a project
    if add_material:
        project = storage.load_project(add_material)
        
        if not project:
            console.print(f"[red]Project '{add_material}' not found.[/red]")
            return
        
        # Get material details
        material_type = typer.prompt(
            "Material type",
            default="concrete",
            type=click.Choice(["concrete", "lumber", "steel", "other"])
        )
        name = typer.prompt("Name/Description")
        quantity = typer.prompt("Quantity", type=float)
        unit = typer.prompt("Unit")
        cost = typer.prompt("Cost (optional)", default="")
        notes = typer.prompt("Notes (optional)", default="")
        
        # Create material
        material = ProjectMaterial(
            material_type=material_type,
            name=name,
            quantity=quantity,
            unit=unit,
            cost=float(cost) if cost else None,
            notes=notes or None
        )
        
        # Add to project
        project.add_material(material)
        
        # Save project
        storage.save_project(project)
        
        console.print(f"[green]Material added to project '{add_material}'.[/green]")
        return
    
    # Export project to CSV
    if export:
        project = storage.load_project(export)
        
        if not project:
            console.print(f"[red]Project '{export}' not found.[/red]")
            return
        
        # Prompt for output file
        output_file = typer.prompt("Output file", default=f"{export.lower().replace(' ', '_')}.csv")
        
        with open(output_file, "w", newline="") as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow(["Project", project.name])
            writer.writerow(["Description", project.description or ""])
            writer.writerow(["Location", project.location or ""])
            writer.writerow(["Created", project.created_at])
            writer.writerow(["Updated", project.updated_at])
            writer.writerow(["Total Cost", project.total_cost or ""])
            writer.writerow([])
            
            # Write materials header
            writer.writerow(["Material Type", "Name", "Quantity", "Unit", "Cost", "Notes"])
            
            # Write materials
            for material in project.materials:
                writer.writerow([
                    material.material_type,
                    material.name,
                    material.quantity,
                    material.unit,
                    material.cost or "",
                    material.notes or ""
                ])
        
        console.print(f"[green]Project exported to {output_file}[/green]")
        return
    
    # If no specific command was given, show help
    console.print("Use one of the following options:")
    console.print("  --list: List all projects")
    console.print("  --create: Create a new project")
    console.print("  --view NAME: View a project by name")
    console.print("  --delete NAME: Delete a project by name")
    console.print("  --add-material NAME: Add material to a project")
    console.print("  --export NAME: Export project to CSV")


@app.command()
def dashboard(
    host: str = typer.Option("127.0.0.1", help="Host to bind to"),
    port: int = typer.Option(8000, help="Port to bind to"),
):
    """Launch the web dashboard."""
    try:
        from buildwise.api.main import run_dashboard
        
        console.print(f"[green]Starting BuildWise dashboard on http://{host}:{port}[/green]")
        console.print("Press Ctrl+C to stop the server")
        
        run_dashboard(host=host, port=port)
    except ImportError:
        console.print("[red]Error: FastAPI or Uvicorn not installed.[/red]")
        console.print("Please install additional dependencies:")
        console.print("  pip install fastapi uvicorn jinja2")


@app.command()
def settings(
    list: bool = typer.Option(False, "--list", "-l", help="List current settings"),
    openai_key: str = typer.Option(None, "--openai-key", help="Set OpenAI API key"),
    project_dir: str = typer.Option(None, "--project-dir", help="Set project directory"),
    default_location: str = typer.Option(None, "--location", help="Set default location"),
    price_concrete: float = typer.Option(None, "--price-concrete", help="Set default concrete price per cubic yard"),
    price_lumber: float = typer.Option(None, "--price-lumber", help="Set default lumber price per board foot"),
    price_steel: float = typer.Option(None, "--price-steel", help="Set default steel price per pound"),
):
    """View or modify application settings."""
    from buildwise.config.settings import settings as app_settings
    
    # List current settings
    if list or (not any([openai_key, project_dir, default_location, price_concrete, price_lumber, price_steel])):
        console.print("[bold]Current Settings:[/bold]")
        console.print(f"OpenAI API Key: {'*' * 10 if app_settings.openai_api_key else 'Not set'}")
        console.print(f"Project Directory: {app_settings.project_dir}")
        console.print(f"Default Location: {app_settings.default_location}")
        console.print("[bold]Default Material Prices:[/bold]")
        console.print(f"Concrete (per cubic yard): ${app_settings.material_prices.get('concrete_per_yard', 150)}")
        console.print(f"Lumber - Pine (per board foot): ${app_settings.material_prices.get('lumber_pine_per_bf', 3.0)}")
        console.print(f"Steel (per pound): ${app_settings.material_prices.get('steel_per_pound', 0.85)}")
        return
    
    # Update settings
    if openai_key:
        app_settings.openai_api_key = openai_key
        console.print("[green]OpenAI API key updated.[/green]")
    
    if project_dir:
        app_settings.project_dir = project_dir
        console.print(f"[green]Project directory set to: {project_dir}[/green]")
    
    if default_location:
        app_settings.default_location = default_location
        console.print(f"[green]Default location set to: {default_location}[/green]")
    
    if price_concrete is not None:
        app_settings.update_material_price("concrete_per_yard", price_concrete)
        console.print(f"[green]Default concrete price set to: ${price_concrete} per cubic yard[/green]")
    
    if price_lumber is not None:
        app_settings.update_material_price("lumber_pine_per_bf", price_lumber)
        console.print(f"[green]Default lumber price set to: ${price_lumber} per board foot[/green]")
    
    if price_steel is not None:
        app_settings.update_material_price("steel_per_pound", price_steel)
        console.print(f"[green]Default steel price set to: ${price_steel} per pound[/green]")
