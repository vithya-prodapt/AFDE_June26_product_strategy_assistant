import os
import openai


SYSTEM_PROMPT = """You are a Customer Feedback Analysis Agent specializing in customer sentiment,
pain points, and satisfaction patterns. Your role is to analyze customer reviews, ratings, and
feedback data to extract actionable product insights.

Your analysis must always include:
1. Overall Sentiment Summary (positive/negative/neutral breakdown)
2. Top Customer Pain Points (ranked by frequency)
3. Top Customer Praises (what customers love most)
4. Rating Analysis by product/region if available
5. Return/Refund Patterns and what they signal
6. Actionable Recommendations for the Product team

Format your response in clear markdown with headers and bullet points."""


class CustomerFeedbackAgent:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY", "learner042"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://keygateway.arshnivlabs.com"),
            timeout=60.0,
        )

    def analyze(self, data: str) -> str:
        user_content = f"""Analyze the following customer data and provide a comprehensive Customer Insights Report:

{data[:8000]}

Focus on extracting patterns from reviews, ratings, and return data. Be specific with numbers and percentages where available."""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=2048,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
        )
        return response.choices[0].message.content
