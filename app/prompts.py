"""Prompt templates for local model with AI intelligence."""

def build_local_prompt(user_query: str) -> str:
    """
    Builds an adaptive prompt that uses AI intelligence to:
    1. Understand the query type (factual, analytical, creative, etc.)
    2. Provide short or detailed answers based on complexity
    3. Use reasoning for complex questions
    """
    word_count = len(user_query.split())
    
    # --- Check for question type ---
    query_lower = user_query.lower()
    
    # Analytical/Reasoning questions → Detailed answer
    reasoning_keywords = ['explain', 'describe', 'analyze', 'compare', 'contrast', 
                          'why', 'how', 'derive', 'prove', 'evaluate', 'discuss',
                          'difference between', 'benefits', 'advantages', 'disadvantages']
    
    # Creative questions → Detailed answer
    creative_keywords = ['write', 'compose', 'poem', 'story', 'essay', 'creative', 
                         'suggest', 'recommend', 'ideas', 'brainstorm']
    
    # Math/Coding questions → Medium answer with steps
    math_keywords = ['calculate', 'solve', 'compute', 'function', 'code', 'program', 
                     'algorithm', 'debug', 'fix', 'syntax']
    
    is_reasoning = any(keyword in query_lower for keyword in reasoning_keywords)
    is_creative = any(keyword in query_lower for keyword in creative_keywords)
    is_math = any(keyword in query_lower for keyword in math_keywords)
    
    # --- Build intelligent prompt based on query type ---
    
    # SHORT: Simple factual questions (1-5 words, no reasoning keywords)
    if word_count <= 5 and not is_reasoning and not is_creative and not is_math:
        prompt = f"""You are an intelligent AI assistant. Use your knowledge to answer the following question in the SHORTEST possible way.
Give ONLY the direct, accurate answer. No explanations, no extra text, no fluff.
If it's a name → give ONLY the name.
If it's a number → give ONLY the number.
If it's a fact → give ONLY the fact in 1-2 words.

Use your intelligence to understand what the user wants and give exactly that.

Question: {user_query}

Answer:"""
    
    # MEDIUM: Math/Coding/Calculation questions
    elif is_math:
        prompt = f"""You are an intelligent AI assistant. Solve the following problem step by step.
Show your reasoning briefly, then give the final answer clearly.

Use your intelligence to understand the problem and provide an accurate solution.

Question: {user_query}

Solution:"""
    
    # MEDIUM-LONG: Reasoning/Explain questions
    elif is_reasoning:
        prompt = f"""You are an intelligent AI assistant. Use your reasoning abilities to answer the following question.
Provide a clear, well-structured explanation with relevant details.
Use your intelligence to identify the key points and explain them logically.

Question: {user_query}

Explanation:"""
    
    # LONG: Creative/Write/Generate questions
    elif is_creative:
        prompt = f"""You are an intelligent AI assistant. Use your creativity and knowledge to fulfill the following request.
Be engaging, thoughtful, and provide value. Use your intelligence to understand the context and deliver appropriately.

Question: {user_query}

Response:"""
    
    # DEFAULT: Medium length (6-10 words, general questions)
    else:
        prompt = f"""You are an intelligent AI assistant. Use your knowledge and reasoning to answer the following question.
Give a clear, concise answer that directly addresses the query.
Use your intelligence to understand exactly what the user needs.

Question: {user_query}

Answer:"""
    
    return prompt