import pandas as pd
import io
from typing import List


class DataProcessor:
    def process_files(self, uploaded_files) -> dict:
        all_text_parts = []
        csv_analysis = ""
        documents = []

        for file in uploaded_files:
            name = file.name if hasattr(file, "name") else str(file)
            if name.endswith(".csv"):
                df = pd.read_csv(io.BytesIO(file.read()) if hasattr(file, "read") else file)
                summary = self._analyze_csv(df)
                all_text_parts.append(f"=== Sales/Product Data ===\n{summary}")
                csv_analysis = summary
                if "Review" in df.columns:
                    reviews = df["Review"].dropna().astype(str).tolist()
                    documents.extend(reviews)
                documents.extend(self._chunk_text(summary))
            elif name.endswith(".pdf"):
                text = self._extract_pdf(file)
                all_text_parts.append(f"=== Document: {name} ===\n{text}")
                documents.extend(self._chunk_text(text))
            elif name.endswith(".txt"):
                raw = file.read()
                text = raw.decode("utf-8", errors="replace") if isinstance(raw, bytes) else raw
                all_text_parts.append(f"=== Document: {name} ===\n{text}")
                documents.extend(self._chunk_text(text))

        summary = "\n\n".join(all_text_parts)

        return {
            "summary": summary,
            "csv_analysis": csv_analysis if csv_analysis else summary,
            "documents": documents if documents else self._chunk_text(summary),
        }

    def _analyze_csv(self, df: pd.DataFrame) -> str:
        lines = []
        lines.append(f"Dataset: {len(df)} records, {len(df.columns)} columns")
        lines.append(f"Columns: {', '.join(df.columns.tolist())}")

        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        if numeric_cols:
            stats = df[numeric_cols].describe().round(2)
            lines.append("\n--- Key Statistics ---")
            lines.append(stats.to_string())

        if "Product_Name" in df.columns:
            grp_cols = [c for c in ["Revenue_USD", "Profit_USD", "Units_Sold", "Customer_Rating", "Returns"] if c in df.columns]
            if grp_cols:
                product_perf = df.groupby("Product_Name")[grp_cols].sum().round(2)
                if "Customer_Rating" in grp_cols:
                    product_perf["Customer_Rating"] = df.groupby("Product_Name")["Customer_Rating"].mean().round(2)
                lines.append("\n--- Product Performance ---")
                lines.append(product_perf.to_string())

        if "Region" in df.columns and "Revenue_USD" in df.columns:
            region_perf = df.groupby("Region")[["Revenue_USD", "Profit_USD", "Units_Sold"]].sum().round(2)
            lines.append("\n--- Regional Performance ---")
            lines.append(region_perf.to_string())

        if "Category" in df.columns and "Revenue_USD" in df.columns:
            cat_perf = df.groupby("Category")[["Revenue_USD", "Units_Sold"]].sum().round(2)
            lines.append("\n--- Category Performance ---")
            lines.append(cat_perf.to_string())

        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            if "Revenue_USD" in df.columns:
                df["Month"] = df["Date"].dt.to_period("M")
                monthly = df.groupby("Month")["Revenue_USD"].sum().round(2)
                lines.append("\n--- Monthly Revenue Trend ---")
                lines.append(monthly.to_string())

        if "Customer_Rating" in df.columns:
            rating_dist = df["Customer_Rating"].value_counts().sort_index()
            lines.append(f"\n--- Rating Distribution ---\n{rating_dist.to_string()}")
            lines.append(f"Average Rating: {df['Customer_Rating'].mean():.2f}")

        if "Returns" in df.columns and "Units_Sold" in df.columns:
            total_sold = df["Units_Sold"].sum()
            total_returns = df["Returns"].sum()
            return_rate = (total_returns / total_sold * 100) if total_sold > 0 else 0
            lines.append(f"\n--- Return Rate ---\nTotal Units Sold: {total_sold:,} | Returns: {total_returns:,} | Return Rate: {return_rate:.1f}%")

        if "Review" in df.columns:
            reviews = df["Review"].dropna().tolist()
            lines.append(f"\n--- Customer Reviews Sample ({len(reviews)} total) ---")
            for r in reviews[:30]:
                lines.append(f"• {r}")

        return "\n".join(lines)

    def _extract_pdf(self, file) -> str:
        try:
            from pypdf import PdfReader
            raw = file.read() if hasattr(file, "read") else open(file, "rb").read()
            reader = PdfReader(io.BytesIO(raw))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as e:
            return f"[PDF extraction error: {e}]"

    def _chunk_text(self, text: str, chunk_size: int = 600) -> List[str]:
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        chunks, current = [], ""
        for para in paragraphs:
            if len(current) + len(para) < chunk_size:
                current += (" " if current else "") + para
            else:
                if current:
                    chunks.append(current)
                current = para
        if current:
            chunks.append(current)
        return chunks if chunks else [text[:chunk_size]]
