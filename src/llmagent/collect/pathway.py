import hashlib
import logging
import re

import pandas as pd

from llmagent.utils import get_gene_map

logging.basicConfig(level=logging.INFO)

def remove_parentheses(text):
    return re.sub(r'\(.*?\)', '', text).strip()

def read_data(source_name, data_source_template):
    url = data_source_template.format(source=source_name)
    return pd.read_csv(url, sep='\t', compression='gzip', encoding='latin1', skiprows=1).assign(source=source_name)

def preprocess_data(df, use_columns):
    df = df[[col for col in df.columns if col in use_columns]]
    df.rename(columns={'GeneSym': ':START_ID(Gene)', 'Pathway(Organism)': 'Pathway'}, inplace=True)
    df['Pathway'] = df['Pathway'].str.lower().apply(remove_parentheses)
    df = add_custom_pathway_id(df)
    df[':TYPE'] = 'part_of'
    return df

def save_data(df, path):
    df.to_csv(path, index=False, compression='gzip', sep='\t')
    logging.info(f'Saved data to {path}')

def filter_data(data, min_links, max_links):
    link_counts = data[':END_ID(Pathway)'].value_counts()
    filtered_indexes = link_counts[(link_counts >= min_links) & (link_counts <= max_links)].index
    return data[data[':END_ID(Pathway)'].isin(filtered_indexes)], filtered_indexes

def add_custom_pathway_id(data, id_prefix='PW'):
    data[':END_ID(Pathway)'] = data['Pathway'].apply(lambda x: f'{id_prefix}_{hashlib.md5(x.encode()).hexdigest()[:8]}')
    return data

def main():
    data_source_template = 'https://maayanlab.cloud/static/hdfs/harmonizome/data/{source}/gene_attribute_edges.txt.gz'
    data_sources = ['humancyc', 'reactome', 'kegg', 'biocarta', 'pid', 'wikipathways', 'panther']
    use_columns = ['GeneSym', 'Pathway', 'Pathway(Organism)', 'source']
    output_dir = 'data/processed/'
    output_file_name = 'pathways.tsv.gz'
    max_gene_links = 19200 / 20
    min_gene_links = 4

    dataframes = [preprocess_data(read_data(source, data_source_template), use_columns) for source in data_sources]
    merged_df = pd.concat(dataframes, ignore_index=True)
    
    grouped_df = merged_df.groupby([':START_ID(Gene)', ':TYPE', ':END_ID(Pathway)']).agg(lambda x: ';'.join(set(x))).reset_index()
    data, removed_entities = filter_data(grouped_df, min_gene_links, max_gene_links)
    logging.info(f'Removed entities: {removed_entities}')

    gene_map = get_gene_map()
    is_protein = data[':START_ID(Gene)'].isin(set(gene_map.values()))
    data = data.loc[is_protein]
    logging.info(f'Percentage discarded genes: {1 - is_protein.mean()}')

    save_data(data, f'{output_dir}{output_file_name}')

    vocab_df = data[[':END_ID(Pathway)', 'Pathway']].drop_duplicates()
    vocab_df.columns = [':ID(Pathway)', 'name']
    vocab_df[':LABEL'] = 'Pathway'
    save_data(vocab_df, 'data/processed/pathway_node.tsv.gz')

    logging.info(f'Gene counts:\n{data[":START_ID(Gene)"].value_counts()}')
    logging.info(f'Pathway counts:\n{data[":END_ID(Pathway)"].value_counts()}')
    logging.info(f'Source counts:\n{data["source"].value_counts()}')

if __name__ == '__main__':
    main()
