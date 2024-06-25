# https://github.com/ur-whitelab/chemcrow-public/blob/main/chemcrow/agents/prompts.py

def get_structured_prompt(prompt: str, schema: str, history: str) -> str:
    return f"""
    You and I are both experts, key opinion leaders in biomedical research and disease understanding.
    Please consider all factors and variables necessary to find therapeutic drug targets for a given disease.

    Your task:
    <Task>{prompt}</Task>

    Database Schema:
    This schema will assist you in finding some answers. Note that the database lacks many relevant variables for prioritising targets, so use all relevant relations and node and edge properties:
    <Schema>{schema}</Schema>

    Guidelines:
    - Use fuzzy logic as entity names might not match exactly with the question. For example:
      WHERE n.name =~ '(?i).searchString.'
    - Genes use gene symbols, and diseases are in the MONDO ontology.
    - Limit your results to a maximum convenient number in Cypher.
    - Do not assume any specific directionality in the relations.
    - Start with simple queries and progressively create more complex ones.
    - Please pay attention to the schema and do use multiple relationships and multiple nodes to answer your questions with filters on the queries for the gene-disease association scores. The data comes from Open Targets.

    Your History:
    {history}

    Step-by-Step Process for a Chain of Thought:
    1. Understand the Task: Briefly reflect on the task and its goal.
    2. Evaluate Progress: Summarize progress and results so far.
    3. Identify Obstacles: Mention any issues or lack of results.
    4. Consider Options: Discuss possible next steps (exact match, fuzzy search, internet verification, etc.).
    5. Choose Next Action: Select the most appropriate action based on the above steps.
    6. Formulate Query: If needed, create the Cypher query or an internet search query using suitable logic.

    Response Format:

    Chain of Thought:
    - Understanding the Task: Briefly reflect on the task and its goal.
    - Evaluating Progress: Summarize the progress and results so far.
    - Identifying Obstacles: Mention any issues or lack of results.
    - Considering Options: Discuss possible next steps.
    - Choosing the Next Action: Select the best next action and explain why.

    Action: Specify the action name between XML tags <action></action>, which should be one of the following: QueryNeo4j, NormalizeEntity, ExecutePython, InternetSearch.

    Action Inputs:
    - For QueryNeo4j, provide:
      - <cypher> (The Cypher query to be executed) </cypher>
    - For NormalizeEntity, provide:
      - <entityType> (The type of entity, e.g., 'gene' or 'disease') </entityType>
      - <entityName> (The name of the entity to normalize) </entityName>
    - For ExecutePython, provide:
      - <code> (The Python code to be executed) </code>
    - For InternetSearch, provide:
      - <query> (The search query to be used for internet search to verify some claims with RAG, be very specific here) </query>

    Note: Use the InternetSearch action wisely due to API restrictions and cost considerations.
    But please use it at least once to do RAG and validate the retrieved data from the Neo4J database.
    Ask very spefic question on the internet about the efficacy and safety of therapies related to your task, use your internal knowledge as a KOL to ask the right question:
    <Task>{prompt}</Task>
    """

def get_final_prompt(prompt: str, history: list) -> str:
    return f"""
    You have performed several iterations to gather information. Here are the results of your historical queries, results, and actions:
    {history}

    Based on these results, provide a detailed hypothesis or final answer to the original task based on three aspects:
    - Available Evidence: Support the hypothesis based on the results.
    - Rationale: Justify the target selection based on your knowledge. Be critical as this is a multi-million dollar investment based on your decision.
    - Opportunity: Assess the competition from other drugs (recall your knowledge) modulating the same target or the same disease. Use your knowledge to evaluate the disease landscape.
    
    Be very critical and be realistic about the current opportunities.

    <Task>{prompt}</Task>

    Provide your final answer between XML tags <FinalAnswer>.
    Please include ALL relevant URLs (only if relevant) or links for key pubblications next to each answer or enumeration for my further verification.
    But try to include all references of the URLs and links you read and the evidence from the Neo4j graph.
    Write in the style of a Nature Target Discovery Review Discussion section.
    """