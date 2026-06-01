import os
import openai


SYSTEM_PROMPT = """You are an Executive Report Agent that synthesizes complex multi-agent analysis
into a concise, high-impact executive summary for senior leadership (C-suite, Board, VP-level).

Your report must follow this structure:

## Executive Summary
[3-4 sentence overview of the business situation]

## Key Findings
[5-7 most critical data-backed findings with specific numbers]

## Strategic Opportunities
[Top 3-5 opportunities ranked by potential impact]

## Critical Risks & Issues
[Top 3-4 risks that require immediate attention]

## Strategic Recommendations
[5-7 specific, actionable recommendations with expected outcomes]

## Proposed Action Plan
[30-60-90 day action items with owners and success metrics]

Write in executive language: concise, data-driven, action-oriented. No fluff. Every claim backed by data."""


class ExecutiveReportAgent:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://keygateway.arshnivlabs.com"),
        )

    def analyze(self, all_results: dict) -> str:
        customer = all_results.get("customer_feedback", "")
        sales = all_results.get("sales_analysis", "")
        competitor = all_results.get("competitor_analysis", "")
        swot = all_results.get("swot_analysis", "")
        features = all_results.get("feature_prioritization", "")

        user_content = f"""Synthesize the following multi-agent analysis into a compelling Executive Report:

=== Customer Insights ===
{customer[:1500]}

=== Sales Analysis ===
{sales[:1500]}

=== Competitor Analysis ===
{competitor[:1200]}

=== SWOT Analysis ===
{swot[:1200]}

=== Feature Priorities ===
{features[:1200]}

Create a concise, board-ready executive report that captures the most important insights and drives strategic decision-making. Be specific with numbers and timelines."""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=2048,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
        )
        return response.choices[0].message.content
