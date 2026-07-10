"""Prompt templates for local model."""
def build_local_prompt(user_query: str) -> str:
    # Generic instruct prompt, adjust for your local model (Gemma)
    return f"<start_of_turn>user\n{user_query}<end_of_turn>\n<start_of_turn>model\n"