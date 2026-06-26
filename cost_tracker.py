from config import INPUT_COST_PER_1K, OUTPUT_COST_PER_1K, USD_TO_INR

class CostTracker: # class implimentation
    def __init__(self):
        self.total_input_tokens  = 0
        self.total_output_tokens = 0
        self.total_calls         = 0

    def record(self, usage):
        """Pass in response.usage from Groq response — same as OpenAI format."""
        self.total_input_tokens  += usage.prompt_tokens
        self.total_output_tokens += usage.completion_tokens
        self.total_calls         += 1

    def total_cost_usd(self):
        input_cost  = (self.total_input_tokens  / 1000) * INPUT_COST_PER_1K
        output_cost = (self.total_output_tokens / 1000) * OUTPUT_COST_PER_1K
        return input_cost + output_cost

    def total_cost_inr(self):
        return self.total_cost_usd() * USD_TO_INR

    def summary(self):
        return (
            f"\n Session Stats\n"
            f"{'─'*30}\n"
            f"  API calls       : {self.total_calls}\n"
            f"  Input tokens    : {self.total_input_tokens}\n"
            f"  Output tokens   : {self.total_output_tokens}\n"
            f"  Total tokens    : {self.total_input_tokens + self.total_output_tokens}\n"
            f"  Cost            : 0 (grok free)\n"
            f"{'─'*30}"
        )