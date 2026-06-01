from agents.customer_feedback_agent import CustomerFeedbackAgent
from agents.sales_analysis_agent import SalesAnalysisAgent
from agents.competitor_analysis_agent import CompetitorAnalysisAgent
from agents.swot_analysis_agent import SWOTAnalysisAgent
from agents.feature_prioritization_agent import FeaturePrioritizationAgent
from agents.executive_report_agent import ExecutiveReportAgent


class AgentOrchestrator:
    """Manages the multi-agent analysis pipeline with sequential collaboration."""

    def __init__(self):
        self.customer_agent = CustomerFeedbackAgent()
        self.sales_agent = SalesAnalysisAgent()
        self.competitor_agent = CompetitorAnalysisAgent()
        self.swot_agent = SWOTAnalysisAgent()
        self.feature_agent = FeaturePrioritizationAgent()
        self.executive_agent = ExecutiveReportAgent()

    def run(self, processed_data: dict, progress_callback=None) -> dict:
        results = {}
        summary = processed_data.get("summary", "")
        csv_analysis = processed_data.get("csv_analysis", summary)

        def _step(label: str, fn, *args):
            if progress_callback:
                progress_callback(label)
            return fn(*args)

        # Step 1: Customer Feedback Analysis
        results["customer_feedback"] = _step(
            "Running Customer Feedback Agent...",
            self.customer_agent.analyze,
            summary,
        )

        # Step 2: Sales Performance Analysis
        results["sales_analysis"] = _step(
            "Running Sales Analysis Agent...",
            self.sales_agent.analyze,
            csv_analysis,
        )

        # Step 3: Competitor & Market Analysis (receives prior agent insights)
        results["competitor_analysis"] = _step(
            "Running Competitor Analysis Agent...",
            self.competitor_agent.analyze,
            summary,
            results["customer_feedback"],
            results["sales_analysis"],
        )

        # Step 4: SWOT Synthesis (receives all prior insights)
        results["swot_analysis"] = _step(
            "Running SWOT Analysis Agent...",
            self.swot_agent.analyze,
            results["customer_feedback"],
            results["sales_analysis"],
            results["competitor_analysis"],
        )

        # Step 5: Feature Prioritization
        results["feature_prioritization"] = _step(
            "Running Feature Prioritization Agent...",
            self.feature_agent.analyze,
            results["customer_feedback"],
            results["sales_analysis"],
            results["swot_analysis"],
        )

        # Step 6: Executive Report (synthesizes all)
        results["executive_report"] = _step(
            "Running Executive Report Agent...",
            self.executive_agent.analyze,
            results,
        )

        return results
