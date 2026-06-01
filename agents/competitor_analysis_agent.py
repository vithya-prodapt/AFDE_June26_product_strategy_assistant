import os
import openai


SYSTEM_PROMPT = """You are a Competitor & Market Analysis Agent with expertise in competitive
intelligence, market positioning, and strategic differentiation.

Your analysis must always include:
1. Market Positioning Assessment (based on product categories, pricing, performance)
2. Competitive Strengths vs Market Gaps
3. Category-Level Competitive Landscape (Electronics, Wearables, Smart Home, Audio, Accessories)
4. Pricing & Value Proposition Analysis
5. Market Opportunities (white spaces, underserved segments)
6. Competitive Threats & Risks
7. Differentiation Recommendations

Even without explicit competitor data, infer competitive positioning from product performance,
pricing, ratings, and market signals. Format in clear markdown with headers and bullet points."""


class CompetitorAnalysisAgent:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY", "learner042"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://keygateway.arshnivlabs.com"),
            timeout=60.0,
        )

    def analyze(self, raw_data: str, customer_insights: str, sales_insights: str) -> str:
        user_content = f"""Based on the following product data and prior agent insights, provide a Competitor & Market Analysis:

=== Raw Business Data ===
{raw_data[:4000]}

=== Customer Feedback Insights ===
{customer_insights[:2000]}

=== Sales Performance Insights ===
{sales_insights[:2000]}

Analyze competitive positioning, market gaps, and strategic differentiation opportunities. Infer competitive threats from performance data where explicit competitor information is not available."""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=2048,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
        )
        return response.choices[0].message.content
