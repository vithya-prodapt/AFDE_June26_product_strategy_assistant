import os
import openai


SYSTEM_PROMPT = """You are a Sales Analysis Agent with deep expertise in revenue analytics,
product performance, and business growth patterns. You analyze structured sales data to uncover
trends, opportunities, and risks.

Your analysis must always include:
1. Revenue & Profit Overview (totals, trends, growth rates)
2. Top Performing Products (by revenue, profit margin, units sold)
3. Underperforming Products (low margin, high returns, poor ratings)
4. Regional Performance Analysis (best/worst regions, regional opportunities)
5. Marketing ROI Analysis (spend vs revenue by product/region)
6. Seasonal / Time-Based Trends
7. Strategic Sales Recommendations

Use specific numbers from the data. Format in clear markdown with headers and bullet points."""


class SalesAnalysisAgent:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://keygateway.arshnivlabs.com"),
        )

    def analyze(self, data: str) -> str:
        user_content = f"""Analyze the following sales and product performance data:

{data[:8000]}

Provide a comprehensive Sales Analysis Report with specific insights and strategic recommendations. Calculate ROI, profit margins, and growth trends where possible."""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=2048,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
        )
        return response.choices[0].message.content
