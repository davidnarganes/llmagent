import xml.etree.ElementTree as ET
import pandas as pd
import re

def clean_string(s):
    return re.sub(r'\s+', '_', s)

def extract_first_symbol(graphics_name):
    return graphics_name.split(',')[0].strip()

def parse_xml_to_csv(file_path, include_multiple_entries=False, include_no_link=False):
    tree = ET.parse(file_path)
    root = tree.getroot()

    entries = []
    relations = []

    # Define the mapping for relation types
    relation_type_mapping = {
        'PPrel': 'Protein_Protein_Interaction',
        'GErel': 'Gene_Expression_Interaction',
        'PCrel': 'Protein_Compound_Interaction'
    }

    # Extract entries
    for entry in root.findall('entry'):
        entry_id = entry.get('id')
        entry_names = entry.get('name').split()
        link = entry.get('link')
        
        if not include_multiple_entries and len(entry_names) > 1:
            continue
        if not include_no_link and not link:
            continue
        
        entry_name = entry.get('name')
        entry_type = entry.get('type')
        graphics = entry.find('graphics')
        graphics_name = graphics.get('name') if graphics is not None else ""
        primary_name = extract_first_symbol(graphics_name)

        entries.append([entry_id, entry_name, entry_type, link, primary_name])

    # Extract relations
    for relation in root.findall('relation'):
        entry1 = relation.get('entry1')
        entry2 = relation.get('entry2')
        relation_type = relation_type_mapping.get(relation.get('type'), relation.get('type'))
        subtypes = relation.findall('subtype')
        for subtype in subtypes:
            subtype_name = clean_string(subtype.get('name'))
            subtype_value = clean_string(subtype.get('value'))
            relation_combined_type = f"{relation_type}_{subtype_name}_{subtype_value}".strip('_')
            relations.append([entry1, entry2, relation_combined_type])

    # Convert to DataFrames
    entries_df = pd.DataFrame(entries, columns=['entry_id', 'entry_name', 'entry_type', 'link', 'primary_name'])
    relations_df = pd.DataFrame(relations, columns=['entry1', 'entry2', ':TYPE'])

    # Save to CSV
    entries_csv_path = file_path.replace('.xml', '_entries.csv')
    relations_csv_path = file_path.replace('.xml', '_relations.csv')
    entries_df.to_csv(entries_csv_path, index=False)
    relations_df.to_csv(relations_csv_path, index=False)

    return entries_csv_path, relations_csv_path

# Process each file
indir = 'data/external/ML Research Engineer Technical Assessment/KEGG_data/KGML'
file_paths = [
    f'{indir}/hsa05210.xml',
    f'{indir}/hsa04930.xml',
    f'{indir}/hsa05012.xml',
    f'{indir}/hsa05010.xml'
]

for file_path in file_paths:
    entries_csv, relations_csv = parse_xml_to_csv(file_path, include_multiple_entries=False, include_no_link=False)
    print(f"Processed {file_path}:")
    print(f"  Entries CSV: {entries_csv}")
    print(f"  Relations CSV: {relations_csv}")
