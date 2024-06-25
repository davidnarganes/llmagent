import logging
from typing import Any, Optional, Dict, Tuple
import re
from llmagent.agent.tools import (
    Neo4jTool,
    EntityNormalizationTool,
    PythonTool,
    InternetSearchTool
)
from llmagent.agent.aiquery import AIQueryClient
from llmagent.agent.prompts import (
    get_structured_prompt,
    get_final_prompt
)

# DONE: nature style with URLs as output
# TODO: check the API calls to the internet
# TODO: track performance
# DONE: use openai or anthropic
# TODO: Add opentargets tractability
# DONE: score as a float

class TargetDiscoveryAgent:
    def __init__(self, provider: str, model_name: str, max_iterations: int, verbose: bool = True):
        self.llm = AIQueryClient(provider)
        self.model_name = model_name
        self.max_tokens = 2048
        self.tools = self._initialize_tools()
        self.max_iterations = max_iterations
        self.verbose = verbose
        self.schema = self._fetch_db_schema()
        self.history = []

    def _initialize_tools(self) -> Dict[str, Dict[str, Any]]:
        return {
            "neo4j_app": {"instance": Neo4jTool(), "description": "Tool to interact with Neo4j"},
            "entity_normalization_tool": {"instance": EntityNormalizationTool(), "description": "Tool to normalize bio entities"},
            "python_executor": {"instance": PythonTool(), "description": "Tool to execute Python code for calculations"},
            "internet_search_tool": {"instance": InternetSearchTool(), "description": "Tool to search the internet for RAG"}
        }

    def _fetch_db_schema(self) -> str:
        if not hasattr(self, '_cached_schema'):
            try:
                self._cached_schema = self.tools["neo4j_app"]["instance"].get_db_schema()
                self._log(f"Database schema retrieved: {self._cached_schema}")
            except Exception as e:
                self._log(f"Error retrieving database schema: {e}", level=logging.ERROR)
                raise e
        return self._cached_schema

    def run(self, prompt: str) -> str:
        self._log(f"Received prompt: {prompt}")
        for iteration in range(self.max_iterations):
            self._log(f"Iteration: {iteration + 1}")
            thought_action_response = self._generate_thought_action(prompt)
            if not thought_action_response:
                return "Error generating thought-action sequence"
            self._log(f"Thought-action response: {thought_action_response}")
            self._perform_action(thought_action_response, iteration)

            self._log(f"###HISTORY###:\n{self.history}")

        return self._final_summary(prompt) or "Max iterations reached without finding a final answer."

    def _generate_thought_action(self, prompt: str) -> Optional[str]:
        structured_prompt = get_structured_prompt(prompt, self.schema, self.history)
        try:
            response = self.llm.query(self.model_name, structured_prompt, self.max_tokens)
            self._log(f"Generated thought-action: {response}")
            return response
        except Exception as e:
            self._log(f"Error generating thought-action: {e}", level=logging.ERROR)
            return None

    def _final_summary(self, prompt: str) -> Optional[str]:
        final_prompt = get_final_prompt(prompt, self.history)
        try:
            final_response = self.llm.query(self.model_name, final_prompt, self.max_tokens)
            self._log(f"Final response from last call: {final_response}")
            return self._extract_tag_content("FinalAnswer", final_response)
        except Exception as e:
            self._log(f"Error in final call with results: {e}", level=logging.ERROR)
            return None

    def _perform_action(self, thought_action_response: str, iteration: int):
        result, error = None, None

        # Check for specific action input tags and perform the respective actions
        cypher_query = self._extract_tag_content("cypher", thought_action_response)
        if cypher_query:
            result = self._execute_cypher_query(cypher_query)
        
        entity_type = self._extract_tag_content("entityType", thought_action_response)
        entity_name = self._extract_tag_content("entityName", thought_action_response)
        if entity_type and entity_name:
            result = self._normalize_entity(entity_type, entity_name)
        
        search_query = self._extract_tag_content("query", thought_action_response)
        if search_query:
            result = self._perform_internet_search(search_query)
        
        python_code = self._extract_tag_content("code", thought_action_response)
        if python_code:
            result = self._execute_python_code(python_code)

        self.history.append({
            "iteration": iteration + 1,
            "thought_action_response": thought_action_response,
            "result": result,
            "error": error,
        })

    def _execute_cypher_query(self, cypher_query: str) -> Dict[str, Any]:
        if not cypher_query:
            self._log("Error extracting Cypher query", level=logging.ERROR)
            return {"error": "Error extracting Cypher query"}
        self._log(f"Executing Cypher query: {cypher_query}")
        return self.run_query(cypher_query)

    def _execute_python_code(self, code: str) -> Dict[str, Any]:
        self._log(f"Executing Python code: {code}")
        return self.tools["python_executor"]["instance"].execute_code(code)

    def _normalize_entity(self, entity_type: str, entity_name: str) -> Dict[str, Any]:
        self._log(f"Normalizing entity: {entity_name} of type {entity_type}")
        return self.tools["entity_normalization_tool"]["instance"].normalize_entity(entity_name, entity_type)

    def run_query(self, query: str) -> Dict[str, Any]:
        self._log(f"Running Cypher query: {query}")
        query_result = self.tools["neo4j_app"]["instance"].run(query)
        self._log(f"Query result: {query_result}")
        return query_result

    def _perform_internet_search(self, query: str) -> Dict[str, Any]:
        self._log(f"Performing internet search: {query}")
        return self.tools["internet_search_tool"]["instance"].search(query)

    def _extract_tag_content(self, tag: str, text: str) -> Optional[str]:
        pattern = re.compile(rf"<{tag}>(.*?)</{tag}>", re.DOTALL)
        match = pattern.search(text)
        content = match.group(1).strip() if match else None
        self._log(f"Extracted content for tag '{tag}': {content}")
        return content

    def _log(self, message: str, level: int = logging.INFO):
        if self.verbose:
            logging.log(level, message)