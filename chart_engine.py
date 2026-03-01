import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import uuid
import os


def generate_chart(df):
    try:
        if df is None or df.empty:
            return None

        if df.shape[1] < 2:
            return None

        os.makedirs("static", exist_ok=True)
        filename = f"static/chart_{uuid.uuid4().hex}.png"

        x_col = df.columns[0]
        y_cols = df.columns[1:]

        numeric_cols = df[y_cols].select_dtypes(include=["number"]).columns

        if len(numeric_cols) == 0:
            return None

        plt.figure(figsize=(10, 6))

        # ===============================
        # Single Metric (Smart Color)
        # ===============================
        if len(numeric_cols) == 1:

            y_col = numeric_cols[0]

            if "fraud" in y_col.lower():
                bar_color = "#F44336"
            elif "success" in y_col.lower():
                bar_color = "#4CAF50"
            elif "amount" in y_col.lower():
                bar_color = "#FF9800"
            elif "rate" in y_col.lower():
                bar_color = "#9C27B0"
            else:
                bar_color = "#1f77b4"

            plt.bar(
                df[x_col].astype(str),
                df[y_col],
                color=bar_color
            )

            plt.title(
                f"{y_col.replace('_', ' ').title()} by {x_col.replace('_', ' ').title()}",
                fontsize=14,
                fontweight="bold"
            )

            plt.xlabel(x_col.replace("_", " ").title(), fontsize=12)
            plt.ylabel(y_col.replace("_", " ").title(), fontsize=12)

            plt.xticks(rotation=45)
            plt.grid(axis='y', linestyle='--', alpha=0.6)
            plt.legend([y_col.replace("_", " ").title()])

        # ===============================
        # Multi Metric Comparison
        # ===============================
        else:

            colors = [
                "#4CAF50",
                "#FF9800",
                "#2196F3",
                "#9C27B0",
                "#F44336"
            ]

            bar_width = 0.8 / len(numeric_cols)
            x_positions = range(len(df))

            for i, col in enumerate(numeric_cols):
                plt.bar(
                    [p + i * bar_width for p in x_positions],
                    df[col],
                    width=bar_width,
                    label=col.replace("_", " ").title(),
                    color=colors[i % len(colors)]
                )

            plt.xticks(
                [p + bar_width * (len(numeric_cols) / 2) for p in x_positions],
                df[x_col].astype(str),
                rotation=45
            )

            plt.title(
                "Comparative Performance Analysis",
                fontsize=14,
                fontweight="bold"
            )

            plt.xlabel(x_col.replace("_", " ").title(), fontsize=12)
            plt.ylabel("Value", fontsize=12)

            plt.grid(axis='y', linestyle='--', alpha=0.6)
            plt.legend()

        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches="tight")
        plt.close()

        return filename

    except Exception as e:
        print("Chart error:", e)
        return None