from pathlib import Path
from phoenix.context import ContextFile
from phoenix.token_budget import TokenBudget
from phoenix.java_reader import read_java_file
from phoenix.java_method_extractor import extract_method
from phoenix.summarizer import summarize_code

class ContextExpander:
    def __init__(self, budget: TokenBudget):
        self.budget = budget

    def expand(self, context_file: ContextFile, line_number: int | None = None):
        path = Path(context_file.path)
        lines = read_java_file(path)

        if line_number:
            relevant = extract_method(lines, line_number)
        else:
            relevant = lines[:50]  # fallback

        estimated_tokens = len(relevant) * 3  # rough heuristic

        if not self.budget.can_spend(estimated_tokens):
            context_file.summary = "Token budget too low to expand further."
            return context_file

        self.budget.spend(estimated_tokens)

        context_file.content = "".join(relevant)
        context_file.summary = summarize_code(relevant)

        return context_file
