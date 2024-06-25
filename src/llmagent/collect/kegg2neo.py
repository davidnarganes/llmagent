import pandas as pd

# Load the CSV files
indir = 'data/external/ML Research Engineer Technical Assessment/KEGG_data/KGML/'
outdir = 'data/processed/'
files = {
    'hsa05010_relations': f'{indir}hsa05010_relations.csv',
    'hsa05010_entries': f'{indir}hsa05010_entries.csv',
    'hsa05012_relations': f'{indir}hsa05012_relations.csv',
    'hsa05012_entries': f'{indir}hsa05012_entries.csv',
    'hsa04930_relations': f'{indir}hsa04930_relations.csv',
    'hsa04930_entries': f'{indir}hsa04930_entries.csv',
    'hsa05210_relations': f'{indir}hsa05210_relations.csv',
    'hsa05210_entries': f'{indir}hsa05210_entries.csv'
}

# Load the data into dataframes
dataframes = {name: pd.read_csv(path) for name, path in files.items()}

# Combine entries from all files
all_entries = pd.concat([
    dataframes['hsa05010_entries'],
    dataframes['hsa05012_entries'],
    dataframes['hsa04930_entries'],
    dataframes['hsa05210_entries']
]).drop_duplicates()

# Combine relations from all files
all_relations = pd.concat([
    dataframes['hsa05010_relations'],
    dataframes['hsa05012_relations'],
    dataframes['hsa04930_relations'],
    dataframes['hsa05210_relations']
]).drop_duplicates()

# Create Nodes DataFrame
nodes_df = all_entries.rename(columns={
    'entry_id': 'id:ID',
    'primary_name': 'name',
    'entry_type': ':LABEL',
})[['id:ID', 'name', ':LABEL']]
nodes_df[':LABEL'] = nodes_df[':LABEL'].str.title()
id_to_name = {k:v for k,v in zip(nodes_df['id:ID'], nodes_df['name'])}
nodes_df = nodes_df[nodes_df[':LABEL'] != 'GENE']
nodes_df['id:ID'] = nodes_df['name']
nodes_df.drop_duplicates(inplace=True)

# Create Relationships DataFrame
relationships_df = all_relations.rename(columns={
    'entry1': ':START_ID',
    'entry2': ':END_ID',
})

relationships_df[':START_ID'] = relationships_df[':START_ID'].map(id_to_name)
relationships_df[':END_ID'] = relationships_df[':END_ID'].map(id_to_name)
relationships_df.dropna(inplace=True)
relationships_df[':TYPE'].value_counts()

type_mapping = {
    'Protein_Protein_Interaction_activation_-->': 'activates_protein',
    'Protein_Compound_Interaction_activation_-->': 'activates_compound',
    'Gene_Expression_Interaction_expression_-->': 'expresses_gene',
    'Protein_Protein_Interaction_inhibition_--|': 'inhibits_protein',
    'Protein_Compound_Interaction_inhibition_--|': 'inhibits_compound',
    'Protein_Protein_Interaction_missing_interaction_-/-': 'missing_interaction',
    'Protein_Compound_Interaction_missing_interaction_-/-': 'missing_interaction',
    'Protein_Protein_Interaction_phosphorylation_+p': 'phosphorylates_protein',
    'Protein_Protein_Interaction_dephosphorylation_-p': 'dephosphorylates_protein',
    'Protein_Protein_Interaction_indirect_effect_..>': 'indirectly_affects',
    'Protein_Compound_Interaction_indirect_effect_..>': 'indirectly_affects',
    'Protein_Protein_Interaction_binding/association_---': 'binds_to_protein',
    'Protein_Protein_Interaction_compound_25': 'interacts_with_compound'
}
relationships_df[':TYPE'] = relationships_df[':TYPE'].map(type_mapping)
relationships_df[':TYPE'].value_counts()


# Save Nodes and Relationships DataFrames to CSV
nodes_output_path = f'{outdir}miscelaneous_nodes.tsv.gz'
relationships_output_path = f'{outdir}relationships.tsv.gz'
nodes_df.to_csv(nodes_output_path, sep='\t', index=False, compression='gzip')
relationships_df.to_csv(relationships_output_path, sep='\t', index=False, compression='gzip')