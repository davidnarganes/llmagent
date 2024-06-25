import requests
import pandas as pd
import logging

def parse_go_edges(go_data):
    edges = []
    current_id = None
    alt_ids = []
    
    for line in go_data.splitlines():
        if line.startswith("[Term]") or line.startswith("[Typedef]"):
            current_id = None
            alt_ids = []
        elif line.startswith("id:") and "GO:" in line:
            current_id = line.split()[1]
        elif line.startswith("alt_id:") and "GO:" in line:
            alt_id = line.split()[1]
            alt_ids.append(alt_id)
        elif line.startswith("is_a:") and current_id:
            parent_id = line.split()[1]
            if "GO:" in parent_id:
                edges.append((current_id, parent_id))
                for alt_id in alt_ids:
                    edges.append((alt_id, parent_id))
    return edges

def parse_go_nodes(go_data):
    nodes = []
    current_id = None
    name = None
    
    for line in go_data.splitlines():
        if line.startswith("[Term]") or line.startswith("[Typedef]"):
            if current_id and name:
                nodes.append((current_id, name))
            current_id = None
            name = None
        elif line.startswith("id:") and "GO:" in line:
            current_id = line.split()[1]
        elif line.startswith("name:") and current_id:
            name = line.split("name: ")[1]
    if current_id and name:
        nodes.append((current_id, name))
    
    return nodes

def download_file(url, local_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(local_path, 'wb') as outfile:
            outfile.write(response.content)
        print(f"File downloaded and saved as '{local_path}'")
    else:
        print(f"Failed to download the file. Status code: {response.status_code}")

def save_edges(edges, file_path):
    df = pd.DataFrame(edges, columns=[':START_ID(GO)', ':END_ID(GO)'])
    df.insert(1, ':TYPE', 'is_a')
    logging.info(f'There are {df.duplicated().sum()} duplicates')
    df.to_csv(file_path, sep='\t', compression='gzip', index=False)

def save_nodes(nodes, file_path):
    df = pd.DataFrame(nodes, columns=[':ID(GO)', 'name']).drop_duplicates()
    df[':LABEL'] = 'GO'
    df.to_csv(file_path, compression='gzip', sep='\t', index=False)

def main():
    go_url = 'https://current.geneontology.org/ontology/go.obo'
    local_go_path = 'data/external/go.obo'
    
    download_file(go_url, local_go_path)
    
    with open(local_go_path, 'r') as file:
        go_data = file.read()
    
    edges = parse_go_edges(go_data)
    save_edges(edges, 'data/processed/go.tsv.gz')
    
    nodes = parse_go_nodes(go_data)
    save_nodes(nodes, 'data/processed/go_nodes.tsv.gz')

if __name__ == "__main__":
    main()