import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, Image,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT


class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_styles()

    def _setup_styles(self):
        self.title_style = ParagraphStyle(
            "CustomTitle",
            parent=self.styles["Title"],
            fontSize=26,
            textColor=colors.white,
            spaceAfter=8,
            alignment=TA_CENTER,
        )
        self.subtitle_style = ParagraphStyle(
            "CustomSubtitle",
            parent=self.styles["Normal"],
            fontSize=12,
            textColor=colors.HexColor("#bbdefb"),
            alignment=TA_CENTER,
            spaceAfter=4,
        )
        self.slide_header_style = ParagraphStyle(
            "SlideHeader",
            parent=self.styles["Heading1"],
            fontSize=15,
            textColor=colors.white,
            spaceBefore=0,
            spaceAfter=0,
        )
        self.h2_style = ParagraphStyle(
            "CustomH2",
            parent=self.styles["Heading2"],
            fontSize=12,
            textColor=colors.HexColor("#1a237e"),
            spaceBefore=10,
            spaceAfter=5,
        )
        self.body_style = ParagraphStyle(
            "CustomBody",
            parent=self.styles["Normal"],
            fontSize=9.5,
            leading=14,
            spaceAfter=5,
        )

    def _slide_header(self, title: str, bg: str = "#1a237e") -> Table:
        cell = Paragraph(title, self.slide_header_style)
        t = Table([[cell]], colWidths=[7.0 * inch])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(bg)),
            ("TOPPADDING",    (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING",   (0, 0), (-1, -1), 14),
            ("ROUNDEDCORNERS", [6]),
        ]))
        return t

    def _metrics_table(self, df: pd.DataFrame) -> Table:
        total_rev  = f"${df['Revenue_USD'].sum():,.0f}" if "Revenue_USD" in df.columns else "N/A"
        total_prof = f"${df['Profit_USD'].sum():,.0f}"  if "Profit_USD"  in df.columns else "N/A"
        avg_rating = f"{df['Customer_Rating'].mean():.2f}" if "Customer_Rating" in df.columns else "N/A"
        total_units = f"{df['Units_Sold'].sum():,}" if "Units_Sold" in df.columns else "N/A"
        return_rate = "N/A"
        if "Returns" in df.columns and "Units_Sold" in df.columns:
            rr = df["Returns"].sum() / max(df["Units_Sold"].sum(), 1) * 100
            return_rate = f"{rr:.1f}%"
        mktg = f"${df['Marketing_Spend_USD'].sum():,.0f}" if "Marketing_Spend_USD" in df.columns else "N/A"

        data = [
            ["Metric", "Value", "Metric", "Value"],
            ["Total Revenue",    total_rev,   "Total Profit",      total_prof],
            ["Units Sold",       total_units, "Return Rate",       return_rate],
            ["Avg. Rating",      avg_rating,  "Marketing Spend",   mktg],
        ]
        t = Table(data, colWidths=[1.6 * inch, 1.8 * inch, 1.6 * inch, 1.8 * inch])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a237e")),
            ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
            ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",   (0, 0), (-1, 0), 10),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#e8eaf6")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#e8eaf6"), colors.white]),
            ("FONTNAME",   (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE",   (0, 1), (-1, -1), 10),
            ("FONTNAME",   (0, 1), (0, -1), "Helvetica-Bold"),
            ("FONTNAME",   (2, 1), (2, -1), "Helvetica-Bold"),
            ("ALIGN",      (1, 0), (1, -1), "CENTER"),
            ("ALIGN",      (3, 0), (3, -1), "CENTER"),
            ("GRID",       (0, 0), (-1, -1), 0.5, colors.HexColor("#9fa8da")),
            ("TOPPADDING",    (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        return t

    def _bar_chart_image(self, labels, values, title, color="#1a237e", width=6, height=2.8):
        fig, ax = plt.subplots(figsize=(width, height))
        bars = ax.barh(labels, values, color=color, edgecolor="white")
        ax.set_title(title, fontsize=11, fontweight="bold", color="#1a237e", pad=8)
        ax.set_xlabel("USD", fontsize=8)
        ax.tick_params(axis="y", labelsize=8)
        ax.tick_params(axis="x", labelsize=7)
        for bar, val in zip(bars, values):
            ax.text(bar.get_width() * 1.01, bar.get_y() + bar.get_height() / 2,
                    f"${val:,.0f}", va="center", fontsize=7, color="#333")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        fig.tight_layout()
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=120, bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        return buf

    def generate(self, results: dict, dataframe=None) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch,
        )
        story = []

        # ── Cover Page ──────────────────────────────────────────────────────
        cover_data = [[Paragraph("AI-Powered Product Strategy Report", self.title_style)]]
        cover_table = Table(cover_data, colWidths=[7.0 * inch])
        cover_table.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#1a237e")),
            ("TOPPADDING",    (0, 0), (-1, -1), 60),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 60),
            ("LEFTPADDING",   (0, 0), (-1, -1), 20),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 20),
        ]))
        story.append(cover_table)
        story.append(Spacer(1, 0.3 * inch))

        sub_items = [
            ["Generated by", "AI Product Strategy Assistant"],
            ["Model",        "gpt-4o-mini via Arshniv Labs Gateway"],
            ["Agents",       "6 Specialized AI Agents"],
        ]
        sub_table = Table(sub_items, colWidths=[1.8 * inch, 5.2 * inch])
        sub_table.setStyle(TableStyle([
            ("FONTNAME",  (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME",  (1, 0), (1, -1), "Helvetica"),
            ("FONTSIZE",  (0, 0), (-1, -1), 10),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#37474f")),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(sub_table)
        story.append(PageBreak())

        # ── Key Metrics at a Glance ─────────────────────────────────────────
        if dataframe is not None:
            story.append(self._slide_header("📊  Key Metrics at a Glance", "#283593"))
            story.append(Spacer(1, 0.15 * inch))
            story.append(self._metrics_table(dataframe))
            story.append(Spacer(1, 0.3 * inch))

            # Revenue by Product bar chart
            if "Product_Name" in dataframe.columns and "Revenue_USD" in dataframe.columns:
                prod = dataframe.groupby("Product_Name")["Revenue_USD"].sum().sort_values()
                buf = self._bar_chart_image(
                    prod.index.tolist(), prod.values.tolist(),
                    "Revenue by Product (USD)", color="#3949ab"
                )
                story.append(Image(buf, width=6.5 * inch, height=2.8 * inch))

            story.append(PageBreak())

        # ── AI Analysis Sections ─────────────────────────────────────────────
        section_colors = {
            "executive_report":       "#1a237e",
            "customer_feedback":      "#1b5e20",
            "sales_analysis":         "#0d47a1",
            "competitor_analysis":    "#4a148c",
            "swot_analysis":          "#b71c1c",
            "feature_prioritization": "#e65100",
        }
        sections = [
            ("📋  Executive Summary",                   "executive_report"),
            ("👥  Customer Insights Report",             "customer_feedback"),
            ("📈  Sales Analysis",                       "sales_analysis"),
            ("🔍  Competitor & Market Analysis",         "competitor_analysis"),
            ("⚖️   SWOT Analysis",                       "swot_analysis"),
            ("🎯  Feature Prioritization & Roadmap",     "feature_prioritization"),
        ]

        for title, key in sections:
            content = results.get(key, "")
            if not content:
                continue
            bg = section_colors.get(key, "#1a237e")
            story.append(self._slide_header(title, bg))
            story.append(Spacer(1, 0.12 * inch))
            self._add_markdown_content(story, content)
            story.append(PageBreak())

        doc.build(story)
        buffer.seek(0)
        return buffer.read()

    def _add_markdown_content(self, story, text: str):
        for line in text.split("\n"):
            stripped = line.strip()
            if not stripped:
                story.append(Spacer(1, 0.04 * inch))
                continue
            if stripped.startswith("## "):
                story.append(Paragraph(stripped[3:], self.h2_style))
            elif stripped.startswith("### "):
                story.append(Paragraph(f"<b>{stripped[4:]}</b>", self.body_style))
            elif stripped.startswith("**") and stripped.endswith("**"):
                story.append(Paragraph(f"<b>{stripped[2:-2]}</b>", self.body_style))
            elif stripped.startswith("- ") or stripped.startswith("• "):
                bullet_text = stripped[2:].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                story.append(Paragraph(f"&bull;&nbsp;&nbsp;{bullet_text}", self.body_style))
            elif stripped.startswith("#"):
                story.append(Paragraph(stripped.lstrip("# "), self.h2_style))
            else:
                safe = stripped.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                story.append(Paragraph(safe, self.body_style))
