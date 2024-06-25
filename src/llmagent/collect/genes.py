import pandas as pd

gene_map_url = 'http://ftp.ebi.ac.uk/pub/databases/genenames/hgnc/tsv/hgnc_complete_set.txt'

usecols = [
    'symbol', 'name', 'locus_group', 'status',
    ]

df = pd.read_csv(
    gene_map_url, 
    sep="\t",
    usecols=usecols
)
# Filter
df = df[df["locus_group"] == "protein-coding gene"]
df = df[df['status'] == 'Approved']
df['name'] = df['symbol']

df.rename(columns={
    'symbol':':ID(Gene)',
}, inplace=True)
df[':LABEL'] = 'Gene'
df.to_csv('data/processed/gene_node.tsv.gz', compression='gzip', sep='\t', index=False)