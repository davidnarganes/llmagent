import pandas as pd

def get_gene_map():
    gene_map_url = (
        "http://ftp.ebi.ac.uk/pub/databases/genenames/hgnc/tsv/hgnc_complete_set.txt"
    )
    df_symbol = pd.read_csv(
        gene_map_url, sep="\t", usecols=["symbol", "locus_group", "name", "ensembl_gene_id"]
    )
    df_symbol = df_symbol[df_symbol["locus_group"] == "protein-coding gene"]
    return {
        k: v
        for k, v in zip(df_symbol["ensembl_gene_id"], df_symbol["symbol"], strict=False)
        if not pd.isna(k)
    }