import logging
import asyncio
from neo4j import  GraphDatabase
import anthropic
from llmagent.agent.tools import Neo4jApp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler('query_log.txt'),
        logging.StreamHandler()
    ]
)

class Neo4jApp:

    def __init__(self, uri, user, password, database=None):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database

    async def close(self):
        await self.driver.close()

    async def query_neo4j(self, query, parameters=None):
        async with self.driver.session(database=self.database) as session:
            try:
                result = await session.run(query, parameters)
                return [record.data() for record in await result.records()]
            except Exception as e:
                logging.error(f"Error querying Neo4j: {e}")
                return []

    async def create_relationship(self, entity1, entity2, relationship_type):
        query = (
            "MATCH (a {name: $entity1}), (b {name: $entity2}) "
            "CREATE (a)-[r:" + relationship_type + "]->(b) "
            "RETURN a, b, r"
        )
        parameters = {"entity1": entity1, "entity2": entity2}
        return await self.query_neo4j(query, parameters)

    async def find_entity(self, entity_name):
        query = (
            "MATCH (e) "
            "WHERE e.name = $entity_name "
            "RETURN e"
        )
        parameters = {"entity_name": entity_name}
        return await self.query_neo4j(query, parameters)

async def query_bedrock(claude_client, model, max_tokens, messages, stop_sequences=["```\n"], temperature=0, top_k=1):
    try:
        response = await claude_client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=messages,
            stop_sequences=stop_sequences,
            temperature=temperature,
            top_k=top_k,
        )
        logging.info(f"Received messages: {response.content}")
        return response.content[0].text.strip()
    except Exception as e:
        logging.error(f"Error querying bedrock for messages: {e}")
        return None

async def main():
    neo4j_uri = "neo4j://localhost:7687"
    neo4j_user = "neo4j"
    neo4j_password = "agenticdb"
    model_name = "anthropic.claude-3-sonnet-20240229-v1:0"
    max_tokens = 2048

    # Initialize Claude client
    claude_client = anthropic.AsyncAnthropicBedrock()

    # Initialize Neo4j driver
    neo4j_driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

    # Example query to Neo4j
    neo4j_query = "MATCH (n) RETURN n LIMIT 5"
    neo4j_result = neo4j_driver.execute_query(neo4j_query)

    # Prepare input text for Claude
    input_text = f"Here is the data from Neo4j:\n{neo4j_result}"
    logging.info(f"Querying Claude with input: {input_text}")

    # Query Claude with the result from Neo4j
    claude_response = await query_bedrock(claude_client, model_name, max_tokens, input_text)

    logging.info(f"Claude's response: {claude_response}")

    neo4j_driver.close()

if __name__ == '__main__':
    asyncio.run(main())