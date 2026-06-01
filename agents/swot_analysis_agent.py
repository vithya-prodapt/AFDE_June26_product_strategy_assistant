import os
import openai


SYSTEM_PROMPT = """You are a SWOT Analysis Agent specializing in strategic business assessment.
You synthesize insights from customer feedback, sales data, and market analysis to produce
a comprehensive, evidence-based SWOT analysis.

Structure your response EXACTLY as follows (use these exact markdown headers):

## Strengths
[List 5-7 specific, data-backed strengths with evidence]

## Weaknesses
[List 4-6 specific, data-backed weaknesses with evidence]

## Opportunities
[List 5-7 specific market/product opportunities with rationale]

## Threats
[List 4-6 specific threats with context]

## Strategic Implications
[2-3 paragraphs on what the SWOT means for product strategy]

Each point must be specific, actionable, and supported by data from the provided insights."""


class SWOTAnalysisAgent:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY", "learner042"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://keygateway.arshnivlabs.com"),
            timeout=60.0,
        )

    def analyze(self, customer_insights: str, sales_insights: str, competitor_insights: str) -> str:
        user_content = f"""Synthesize the following agent insights into a comprehensive SWOT Analysis:

=== Customer Feedback Insights ===
{customer_insights[:2500]}

=== Sales Performance Insights ===
{sales_insights[:2500]}

=== Competitor & Market Insights ===
{competitor_insights[:2000]}

Create a rigorous, evidence-backed SWOT analysis. Every point must reference specific data or patterns from the insights above."""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=2048,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
        )
        return response.choices[0].message.content
