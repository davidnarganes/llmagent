import ftplib
import os
import re
import json
import logging
import pandas as pd
from llmagent.utils import get_gene_map

# Constants
FTP_SERVER = "ftp.ebi.ac.uk"
REMOTE_DIR = "/pub/databases/opentargets/platform/latest/output/etl/json/associationByDatatypeDirect/"
LOCAL_DIR = "data/tmp/"
FILE_PATTERN = r"part-\d{5}-[a-f0-9\-]+-c000\.json"
OUTPUT_FILE = "data/processed/opentargets_associations.tsv.gz"
MAX_LINES = 1000000000

# Ensure local directory exists
os.makedirs(LOCAL_DIR, exist_ok=True)

def download_files():
    with ftplib.FTP(FTP_SERVER) as ftp:
        ftp.login()
        ftp.cwd(REMOTE_DIR)
        filenames = ftp.nlst()
        for filename in filenames:
            if re.match(FILE_PATTERN, filename):
                local_filepath = os.path.join(LOCAL_DIR, filename)
                if not os.path.exists(local_filepath):
                    with open(local_filepath, "wb") as f:
                        ftp.retrbinary(f"RETR {filename}", f.write)
                    logging.info(f"Downloaded: {filename}")

def parse_json_files_to_df():
    data = []
    for filename in os.listdir(LOCAL_DIR):
        if re.match(FILE_PATTERN, filename):
            filepath = os.path.join(LOCAL_DIR, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    entry = json.loads(line)
                    data.append(entry)
                    if len(data) >= MAX_LINES:
                        break
            if len(data) >= MAX_LINES:
                break

    return pd.DataFrame(data)

def main():
    download_files()
    df = parse_json_files_to_df()
    gene_map = get_gene_map()
    df[':START_ID(Gene)'] = df['targetId'].map(gene_map)

    mondo_xref_df = pd.read_csv('data/processed/mondo_xref.tsv.gz', compression='gzip', sep='\t')
    any_to_mondo = {k.replace(':','_'):v for k,v in mondo_xref_df.iloc[:,[1,0]].values}
    df[':END_ID(Disease)'] = df['diseaseId'].map(lambda x: any_to_mondo[x] if x in any_to_mondo else x.replace('_',':'))
    df.rename(columns={
        'datatypeId':':TYPE',
        'score':'score:float', # To be casted
    }, inplace=True)
    logging.info(f"Data missing {df.isna().mean()}")
    usecols = [':START_ID(Gene)',':TYPE',':END_ID(Disease)','score:float']
    df_filtered = df.dropna(how='any')
    relation_name_map = {
        "literature": "Is_Reported_In_Literature_For",
        "animal_model": "Has_Animal_Model_Evidence_For",
        "genetic_association": "Has_Genetic_Association_With",
        "rna_expression": "Is_Differentially_Expressed_In",
        "somatic_mutation": "Has_Somatic_Mutation_In",
        "known_drug": "Has_Known_Drug_For",
        "affected_pathway": "Affects_Pathway_In"
    }

    # To rename the ':TYPE' column in your DataFrame
    df_filtered[':TYPE'] = df_filtered[':TYPE'].map(relation_name_map)
    df_filtered[usecols].round(3).to_csv(OUTPUT_FILE, sep='\t', compression='gzip', index=False)
    logging.info(f"Data saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
