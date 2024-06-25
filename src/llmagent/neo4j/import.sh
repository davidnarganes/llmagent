#!/bin/bash

# Full paths to data files
GO_NODES_DATA="llmagent/data/processed/go_nodes.tsv.gz"
MISC_NODES_DATA="llmagent/data/processed/miscelaneous_nodes.tsv.gz"
GENE_NODES_DATA="llmagent/data/processed/gene_node.tsv.gz"
PATHWAY_NODES_DATA="llmagent/data/processed/pathway_node.tsv.gz"
PATHWAYS_DATA="llmagent/data/processed/pathways.tsv.gz"
GO_DATA="llmagent/data/processed/go.tsv.gz"
GOA_DATA="llmagent/data/processed/goa.tsv.gz"
OT_DATA="llmagent/data/processed/opentargets_associations.tsv.gz"
MONDO_DATA="llmagent/data/processed/mondo.tsv.gz"
MONDO_NODES_DATA="llmagent/data/processed/mondo_node.tsv.gz"
KEGG_DATA="llmagent/data/processed/relationships.tsv.gz"

# Full path to the neo4j-admin executable
NEO4J_ADMIN="/Library/Application Support/Neo4j Desktop/Application/relate-data/dbmss/dbms-1fdf7359-be7d-40a0-9559-ba9c37181080/bin/neo4j-admin"

# Database name
DATABASE_NAME="neo4j"

# Import command
"$NEO4J_ADMIN" import --database=$DATABASE_NAME \
--nodes=$GO_NODES_DATA \
--nodes=$MISC_NODES_DATA \
--nodes=$GENE_NODES_DATA \
--nodes=$PATHWAY_NODES_DATA \
--nodes=$MONDO_NODES_DATA \
--relationships=$PATHWAYS_DATA \
--relationships=$GO_DATA \
--relationships=$GOA_DATA \
--relationships=$OT_DATA \
--relationships=$MONDO_DATA \
--relationships=$KEGG_DATA \
--delimiter='\t' \
--skip-bad-relationships=true \
--skip-duplicate-nodes=true \
--force