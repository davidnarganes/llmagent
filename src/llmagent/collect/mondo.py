import logging
import re
import pandas as pd
import requests

BIOPORTAL_API_KEY = "8b5b7825-538d-40e0-9e9e-5ab9274a9aeb"
MONDO_URL = f"https://data.bioontology.org/ontologies/MONDO/submissions/60/download?apikey={BIOPORTAL_API_KEY}"

def download_mondo_obo():
    try:
        response = requests.get(MONDO_URL)
        response.raise_for_status()
        return response.text
    except requests.HTTPError as e:
        logging.error(f"HTTP error occurred: {e}")
        return None
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return None

def extract_mondo_relations(obo_data):
    terms = obo_data.split("[Term]\n")[1:]
    is_a_relations = []
    xref_relations = []
    
    for term in terms:
        id_search = re.findall(r"id: (MONDO:\d+)", term)
        if id_search:
            mondo_id = id_search[0]
            parent_ids = re.findall(r"is_a: (MONDO:\d+)", term)
            xrefs = re.findall(r"xref: (\w+:\d+)", term)
            
            for parent_id in parent_ids:
                is_a_relations.append((mondo_id, parent_id))
            for xref in xrefs:
                xref_relations.append((mondo_id, xref))
    
    df_is_a = pd.DataFrame(is_a_relations, columns=[":START_ID(Disease)", ":END_ID(Disease)"])
    df_xref = pd.DataFrame(xref_relations, columns=[":START_ID(Disease)", ":END_ID(Disease)"])
    df_xref[':TYPE'] = 'xref'
    df_is_a[':TYPE'] = 'is_a'
    return df_is_a, df_xref

def extract_mondo_labels(obo_data):
    terms = obo_data.split("[Term]\n")[1:]
    labels = []
    
    for term in terms:
        id_search = re.search(r"id: (MONDO:\d+)", term)
        label_search = re.search(r"name: (.+)", term)
        if id_search and label_search:
            labels.append((id_search.group(1), label_search.group(1)))
    df = pd.DataFrame(labels, columns=[":ID(Disease)", "name"])
    df[':LABEL'] = 'Disease'
    return df

def main():
    obo_data = download_mondo_obo()
    if obo_data:
        df_is_a, df_xref = extract_mondo_relations(obo_data)
        labels_df = extract_mondo_labels(obo_data)
        
        df_is_a.to_csv("data/processed/mondo.tsv.gz", sep='\t', index=False, compression='gzip')
        df_xref.to_csv("data/processed/mondo_xref.tsv.gz", sep='\t', index=False, compression='gzip')
        labels_df.to_csv("data/processed/mondo_node.tsv.gz", sep='\t', index=False, compression='gzip')

if __name__ == "__main__":
    main()
