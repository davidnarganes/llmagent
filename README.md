# LLM Agent Project

Welcome to the LLM Agent project repository! This project aims to facilitate data processing, and provide an application interface for target discovery in biomedical research. The project integrates various tools and resources to support large language model (LLM) interactions, focusing on enabling efficient and accurate therapeutic target identification.

Day 1: Sunday for the preprocessing.
Day 2: Monday for the agent based LLM.
Day 3: Tuesday for the analysis and optimisation of the prompts.

## Introduction

The LLM Agent project leverages advanced language models to aid in the discovery of therapeutic targets. By integrating various data sources and utilizing sophisticated data processing techniques, this project aims to streamline the identification and analysis of potential drug targets. The project is structured to handle data ingestion, processing, and querying, providing a robust platform for biomedical research.

## Directory Structure

The project is organized into several directories, each serving a specific purpose:

- **data/**: Contains various data sources and processed data.
  - **external/**: External datasets and assessment information.
  - **interim/**: Intermediate data transformations.
  - **processed/**: Final processed data.
  - **raw/**: Raw, unprocessed data.
  - **tmp/**: Temporary files and intermediate results.

- **decisions/**: Documentation of decision records related to project development.

- **logs/**: Log files for tracking script execution and application runs.

- **models/**: Directory for storing trained models.

- **reports/**: Generated reports and documentation.

- **src/**: Source code for the project.
  - **app/**: Streamlit application interface code.
  - **llmagent/**: Core LLM Agent functionalities.
  - **collect/**: Data collection scripts.
  - **neo4j/**: Neo4j database import scripts.
  - **utils.py**: Utility functions.

- **tests/**: Test scripts for validating functionalities.

## Setup Instructions

### Poetry Environment Setup

1. **Install Dependencies:**
   ```sh
   poetry install
   ```

2. **Activate the Virtual Environment:**
   ```sh
   poetry shell
   ```

### Loading Credentials

The project uses credentials stored in a `.env` file for secure access to APIs and databases. Ensure you have a `.env` file in the root directory with the necessary credentials:

```
SERAPI_KEY=your_serapi_key
OPENAI_API_KEY=your_openai_api_key
NEO4J_URI=your_neo4j_uri
NEO4J_USER=your_neo4j_user
NEO4J_PASSWORD=your_neo4j_password
```

## Usage

### Streamlit Application

The Streamlit application provides an interactive interface to interact with the LLM Agent. It includes model selection, pre-defined prompts, and a conversation history.

**To run the Streamlit application:**
```sh
streamlit run src/app/ui.py
```

## Components Overview

### Streamlit Application

The Streamlit application serves as the primary user interface, allowing users to interact with the LLM Agent. It supports the selection of different models, provides pre-defined prompts for common queries, and maintains a conversation history for reference.

### Target Discovery Agent

The `TargetDiscoveryAgent` class is the core component responsible for managing interactions with the LLM, executing prompts, and processing results. It integrates various tools for specific tasks such as querying databases, normalizing entities, executing Python code, and performing internet searches.

### Tools

Various tools are integrated into the agent for specific tasks:
- **Neo4jTool**: Interacts with the Neo4j database.
- **EntityNormalizationTool**: Normalizes biological entities.
- **PythonTool**: Executes Python code for calculations.
- **InternetSearchTool**: Performs internet searches for retrieval-augmented generation (RAG).

## Data Processing

The project processes various datasets to build a comprehensive knowledge graph (KG) that is imported into a Neo4j database. Each dataset contributes specific types of nodes and relationships, aiding in understanding gene-disease associations and biological interactions.

### Datasets, Nodes, and Relationships

1. **KEGG Pathways**:
   - **Nodes**: Miscellaneous Nodes
   - **Relationships**: Various interactions such as protein-protein interactions, gene expression interactions, etc.
   - **Source**: KEGG data files.

2. **Gene Ontology (GO) Data**:
   - **Nodes**: Gene Functions
   - **Relationships**: Hierarchical relationships (e.g., "is_a" relationships)
   - **Source**: Gene Ontology data.

3. **MONDO Disease Ontology**:
   - **Nodes**: Diseases
   - **Relationships**: Disease hierarchy and cross-references (e.g., "is_a" relationships, xrefs)
   - **Source**: MONDO ontology data.

4. **Open Targets Data**:
   - **Nodes**: Genes, Diseases
   - **Relationships**: Gene-Disease Associations
   - **Source**: Open Targets platform.

5. **Pathways Data**:
   - **Nodes**: Pathways
   - **Relationships**: Pathway-gene relationships.
   - **Source**: Various pathway databases.

6. **GOA (Gene Ontology Annotations) Data**:
   - **Nodes**: Genes
   - **Relationships**: Gene-GO term annotations.
   - **Source**: GOA data files.

### High-Level Preprocessing Steps

1. **Data Loading**:
   - Load datasets from various sources using appropriate file formats (CSV, OBO, JSON).

2. **Data Parsing and Transformation**:
   - Extract relevant entities and relationships from raw data.
   - Standardize entity names and relationship types.
   - Map identifiers to ensure consistency across datasets.

3. **Data Cleaning**:
   - Remove duplicates and irrelevant entries.
   - Handle missing values and normalize data formats.

4. **Data Saving**:
   - Save processed nodes and relationships into CSV files.
   - Ensure compatibility with Neo4j import requirements.

### Node and Relationship Files

- **Node Files**:
  - `GO_NODES_DATA`: Gene functions from Gene Ontology.
  - `MISC_NODES_DATA`: Miscellaneous nodes from KEGG pathways.
  - `GENE_NODES_DATA`: Genes from gene mapping.
  - `PATHWAY_NODES_DATA`: Pathways from various pathway databases.
  - `MONDO_NODES_DATA`: Diseases from MONDO ontology.

- **Relationship Files**:
  - `PATHWAYS_DATA`: Pathway-gene relationships.
  - `GO_DATA`: Hierarchical relationships from Gene Ontology.
  - `GOA_DATA`: Gene-GO term annotations.
  - `OT_DATA`: Gene-disease associations from Open Targets.
  - `MONDO_DATA`: Disease relationships from MONDO ontology.
  - `KEGG_DATA`: Various interactions from KEGG pathways.

### Importing Data to Neo4j

The processed data is imported into the Neo4j database using:
```
src/llmagent/neo4j/import.sh
```

By integrating these datasets and preprocessing them appropriately, the project builds a knowledge graph that supports queries and analyses in the Neo4j database. This enables detailed exploration of gene-disease associations, biological functions, and potential therapeutic targets.