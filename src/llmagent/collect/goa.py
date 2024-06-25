import pandas as pd
import logging
from llmagent.utils import get_gene_map

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
URL = 'https://release.geneontology.org/2024-06-10/annotations/goa_human.gaf.gz'
OUTPUT_FILE = 'data/processed/goa.tsv.gz'
CONTENT_NAMES = [
    'DB', 'DB_Object_ID', 'DB_Object_Symbol', 'Qualifier', 'GO_ID',
    'DB_Reference', 'Evidence_Code', 'With_From', 'Aspect',
    'DB_Object_Name', 'DB_Object_Synonym', 'DB_Object_Type',
    'Taxon', 'Date', 'Assigned_By', 'Annotation_Extension', 'Gene_Product_Form_ID'
]
USE_COLS = [
    ':START_ID(Gene)', ':TYPE', ':END_ID(GO)',
]

def main():
    # Download data
    df = pd.read_csv(URL, sep='\t', comment='!', header=None)
    df.columns = CONTENT_NAMES

    # Rename columns for Neo4j
    df.rename(columns={
        'DB_Object_Symbol': ':START_ID(Gene)',
        'GO_ID': ':END_ID(GO)',
        'DB:Reference (|DB:Reference)': 'DB_Reference',
        'Aspect': ':TYPE',
        'DB_Object_Type': 'DB_Object_Type'
    }, inplace=True)

    # Log value counts for each column
    for col in df.columns:
        logging.info(f'The column {col} contains the values:\n {df[col].value_counts()}')

    # Filter data
    gene_map = get_gene_map()
    is_human = df['Taxon'].str.contains('taxon:9606')
    is_protein = df[':START_ID(Gene)'].isin(set(gene_map.values()))
    df_filtered = df.loc[is_human & is_protein, USE_COLS]
    df_filtered[':TYPE'] = df_filtered[':TYPE'].map({
        'F':'has_molfunction',
        'C':'in_component',
        'P':'has_bioprocess',
        })

    # Log value counts for each filtered column
    for col in df_filtered.columns:
        logging.info(f'The column {col} contains the values:\n {df_filtered[col].value_counts()}')

    # Reduce data
    df_reduced = df_filtered.groupby([':START_ID(Gene)', ':TYPE', ':END_ID(GO)']).agg(lambda x: ';'.join(set(x))).reset_index()

    # Save to CSV
    df_reduced.to_csv(OUTPUT_FILE, sep='\t', compression='gzip', index=False)

if __name__ == '__main__':
    main()
