# BuildWise CLI

Intelligent construction calculator suite with AI-powered estimation and SaaS capabilities.

![BuildWise CLI](https://via.placeholder.com/800x400?text=BuildWise+CLI)

## Features

- **Material Calculators**: Concrete, lumber, steel, and more
- **AI-Powered Estimation**: Leverage machine learning for cost and material predictions
- **Unit Conversion**: Seamlessly convert between imperial and metric units
- **Job Estimation**: Complete project cost breakdowns
- **Terminal UI**: Beautiful, responsive interface for desktop and mobile terminals
- **SaaS Integration**: Cloud-based storage and synchronization

## Installation

```bash
# From PyPI (Coming soon)
pip install buildwise-cli

# From source
git clone https://github.com/fullstackcrypto/buildwise-cli.git
cd buildwise-cli
pip install -e .
# Calculate concrete needed for a slab
buildwise concrete --length 10 --width 10 --depth 0.5 --unit feet

# Generate a cost estimate with AI
buildwise estimate --project-type residential --area 2000 --unit sqft

# Save a project to the cloud (requires account)
buildwise project save --name "Smith Residence" --location "Phoenix, AZ"
# Clone repository
git clone https://github.com/fullstackcrypto/buildwise-cli.git
cd buildwise-cli

# Set up environment 
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
poetry install

# Run tests
pytest

# Run linting
black src tests
isort src tests
License
MIT
Author
Ready-Set Solutions
support@charleysllc.com
