from neo4j import GraphDatabase
import logging
import requests
from dotenv import load_dotenv
import os

load_dotenv()

# TODO: maybe HunFlair2 as NER? https://github.com/flairNLP/flair/blob/master/resources/docs/HUNFLAIR2_TUTORIAL_1_TAGGING.md 
# DONE: internet search
# TODO: Tractability, genetics 
# DONE: python interpreter
# DONE: KEGG FILES INTO KG

class InternetSearchTool:
    def __init__(self):
        self.api_url = "https://serpapi.com/search"
        self.api_key = os.getenv('SERAPI_KEY')

    def search(self, query: str, num_results: int = 10):
        try:
            params = {
                'engine': 'duckduckgo',
                'q': query,
                'api_key': self.api_key,
                'num': num_results
            }
            response = requests.get(self.api_url, params=params)
            response.raise_for_status()
            data = response.json()
            results = data.get('organic_results', [])

            return [
                {
                    'title': result.get('title'),
                    'link': result.get('link'),
                    'snippet': result.get('snippet'),
                    'position': result.get('position')
                }
                for result in results[:num_results]
            ]

        except requests.exceptions.RequestException as e:
            logging.error(f"RequestException: {e}")
            return {"error": str(e)}
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return {"error": str(e)}
        
class PythonTool:
    def __init__(self):
        self.history = []
        self.exec_globals = {}

    def execute_code(self, code: str) -> dict:
        result = {"input": code, "output": None, "error": None}
        try:
            exec(code, self.exec_globals)
            result["output"] = {k: v for k, v in self.exec_globals.items() if not k.startswith('__')}
        except Exception as e:
            result["error"] = str(e)
        self.history.append(result)
        return result

    def get_history(self):
        formatted_history = []
        for i, record in enumerate(self.history):
            formatted_record = {
                f"In [{i}]": record["input"],
                f"Out [{i}]": record["output"] if record["error"] is None else f"Error: {record['error']}"
            }
            formatted_history.append(formatted_record)
        return formatted_history

class EntityNormalizationTool:
    def __init__(self):
        self.disease_api_url = "http://mydisease.info/v1/query"
        self.gene_api_url = "http://mygene.info/v3/query"

    def normalize_entity(self, entity_name, entity_type):
        if entity_type.lower() == 'disease':
            return self._normalize_disease(entity_name)
        elif entity_type.lower() == 'gene':
            return self._normalize_gene(entity_name)
        else:
            logging.error(f"Unknown entity type: {entity_type}")
            return []

    def _normalize_disease(self, disease_name):
        params = {
            "q": disease_name,
            "fields": "mondo",
            "size": 5
        }
        try:
            response = requests.get(self.disease_api_url, params=params)
            response.raise_for_status()
            data = response.json()
            return [(hit.get("_id", "N/A"), hit.get("mondo", {}).get("label", "N/A")) for hit in data.get("hits", [])]
        except requests.RequestException as e:
            logging.error(f"Error querying MyDisease.info: {e}")
            return []

    def _normalize_gene(self, gene_name):
        params = {
            "q": gene_name,
            "fields": "symbol,name,taxid,entrezgene",
            "size": 5
        }
        try:
            response = requests.get(self.gene_api_url, params=params)
            response.raise_for_status()
            data = response.json()
            return [
                (
                    hit.get("entrezgene", "N/A"),
                    hit.get("symbol", "N/A"),
                    hit.get("name", "N/A"),
                    hit.get("taxid", "N/A")
                ) 
                for hit in data.get("hits", [])
            ]
        except requests.RequestException as e:
            logging.error(f"Error querying MyGene.info: {e}")
            return []

class Neo4jTool:
    def __init__(self, neo4j_uri="neo4j://localhost:7687", neo4j_user="neo4j", neo4j_password="agenticdb"):
        if not neo4j_uri:
            raise ValueError("The neo4j_uri cannot be empty.")
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

    def close(self):
        self.driver.close()

    def run(self, query):
        try:
            with self.driver.session() as session:
                return [record for record in session.run(query)]
        except Exception as e:
            logging.error(f"Error querying Neo4j: {e}")
            return []

    def find_entity(self, entity_name):
        query = (
            "MATCH (e) "
            f"WHERE e.name = '{entity_name}' "
            "RETURN e"
        )
        return self.run(query)

    def find_related_nodes_and_relations(self, entity_name):
        query = (
            f"MATCH (e {{name: '{entity_name}' }})-[r]-(related) "
            "RETURN e, r, related"
        )
        return self.run(query)

    def get_node_labels(self):
        return self.run("CALL db.labels()")

    def get_relationship_types(self):
        query = """
        MATCH (a)-[r]->(b)
        RETURN DISTINCT type(r) as Relationship, labels(a) as From, labels(b) as To
        """
        return self.run(query)

    def get_node_properties(self):
        query = """
        MATCH (n)
        UNWIND labels(n) AS label
        WITH label, keys(n) AS keys, n
        UNWIND keys AS key
        RETURN label AS Label, collect(DISTINCT key) AS Properties
        """
        return self.run(query)

    def get_relationship_properties(self):
        query = """
        MATCH ()-[r]->()
        UNWIND type(r) AS relType
        WITH relType, keys(r) AS keys, r
        UNWIND keys AS key
        RETURN relType AS RelationshipType, collect(DISTINCT key) AS Properties
        """
        return self.run(query)

    def get_db_schema(self):
        node_labels = self.get_node_labels()
        relationship_types = self.get_relationship_types()
        node_properties = self.get_node_properties()
        relationship_properties = self.get_relationship_properties()

        return {
            "nodes": node_labels,
            "relationships": relationship_types,
            "node_properties": node_properties,
            "relationship_properties": relationship_properties
        }


if __name__ == '__main__':

    # Test
    entity = 'APP'
    app = Neo4jTool()
    query = "MATCH (e) " \
        f"WHERE e.name = '{entity}' " \
        "RETURN e"

    app.run(query)
    app.find_entity(entity)
    app.find_related_nodes_and_relations(entity)
    app.get_db_schema()

    query = """
    MATCH (g:Gene {name: 'APP'})
    OPTIONAL MATCH (g)-[:has_molfunction]->(mf:GO)
    OPTIONAL MATCH (g)-[:has_bioprocess]->(bp:GO)
    OPTIONAL MATCH (g)-[:genetic_association|:literature|:somatic_mutation|:affected_pathway|:rna_expression|:animal_model|:known_drug]->(d:Disease {name: 'Alzheimer Disease'})
    RETURN g.name, mf.name, bp.name, d.name
    """
    a = app.run(query)

    normalizer = EntityNormalizationTool()
    
    # Normalize a disease entity
    disease_results = normalizer.normalize_entity("type II diabetes mellitus", "disease")
    print("Disease Results:")
    for result in disease_results:
        print(result)

    # Normalize a gene entity
    gene_results = normalizer.normalize_entity("P53", "gene")
    print("\nGene Results:")
    for result in gene_results:
        print(result)

    # Python coder
    executor = PythonTool()
    executor.execute_code("a = 5")
    executor.execute_code("b = a * 2")
    executor.execute_code("print(a)")
    executor.execute_code("print(b)")
    executor.execute_code("c = a / 0")  # should be error
    for entry in executor.get_history():
        for key, value in entry.items():
            print(f"{key}: {value}")


    search_tool = InternetSearchTool()
    results = search_tool.search("example search")
    for result in results:
        print(f"Title: {result['title']}\nLink: {result['link']}\nSnippet: {result['snippet']}\nPosition: {result['position']}\n")