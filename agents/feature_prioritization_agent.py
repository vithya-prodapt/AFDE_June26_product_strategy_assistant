import os
import openai


SYSTEM_PROMPT = """You are a Feature Prioritization Agent using frameworks like RICE (Reach, Impact,
Confidence, Effort) and MoSCoW (Must-have, Should-have, Could-have, Won't-have) to prioritize
product improvements and new features.

Your analysis must always include:
1. Must-Have Improvements (critical fixes based on customer pain points and returns)
2. High-Priority Feature Recommendations (high reach × high impact)
3. Product Roadmap Suggestions (Q1-Q4 phased plan)
4. Product Opportunity Scoring (which products need most investment)
5. Quick Wins (low effort, high customer satisfaction impact)
6. Long-term Strategic Features

For each feature/improvement:
- State the customer need it addresses
- Estimate relative priority score (High/Medium/Low)
- Suggest success metrics

Format in clear markdown with headers, tables where helpful, and bullet points."""


class FeaturePrioritizationAgent:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY", "learner042"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://keygateway.arshnivlabs.com"),
            timeout=60.0,
        )

    def analyze(self, customer_insights: str, sales_insights: str, swot: str) -> str:
        user_content = f"""Based on the following insights, create a Feature Prioritization Recommendation:

=== Customer Feedback Insights ===
{customer_insights[:2500]}

=== Sales Performance Insights ===
{sales_insights[:2500]}

=== SWOT Analysis ===
{swot[:2000]}

Prioritize features and product improvements that will maximize customer satisfaction, reduce returns, and drive revenue growth. Include a phased product roadmap."""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=2048,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
        )
        return response.choices[0].message.content
