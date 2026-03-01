from flask import Flask, render_template, request, send_file, session, redirect, url_for
from db import init_db, run_query
from llm_engine import generate_sql
from explain_engine import generate_explanation
from chart_engine import generate_chart
from security import validate_sql

import io
import os
import markdown

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import utils

app = Flask(__name__)
app.secret_key = "insightx_secret_key"

init_db()


@app.route("/", methods=["GET", "POST"])
def index():
    error = None

    if request.method == "POST":
        question = request.form.get("question")

        if not question:
            error = "Please enter a question."
        else:
            conversation = session.get("conversation", [])

            try:
                context = conversation[-1]["question"] if conversation else ""

                sql = generate_sql(question, context)

                # 🔥 Identity Responses
                if sql == "__IDENTITY_CREATED__":
                    answer_raw = "InsightX was created by Team Insi-250305: Niharika Sinha and Piyush Kumar."
                    chart_path = None

                elif sql == "__IDENTITY_SELF__":
                    answer_raw = """
I am InsightX — an AI-powered UPI transaction intelligence system.

I analyze UPI transaction data to provide:
- Fraud detection insights
- Merchant performance analytics
- User behavior intelligence
- Financial risk signals
- Strategic business recommendations
"""
                    chart_path = None

                elif sql == "__IRRELEVANT__":
                    answer_raw = "Kindly ask a question relevant to the UPI transactions dataset."
                    chart_path = None

                else:
                    if not validate_sql(sql):
                        error = "⚠️ Generated invalid SQL."
                        return render_template("index.html",
                                               conversation=conversation,
                                               error=error)

                    df = run_query(sql)

                    if df is None:
                        error = "Database query failed."
                        return render_template("index.html",
                                               conversation=conversation,
                                               error=error)

                    if df.empty:
                        answer_raw = "No data found for this query."
                        chart_path = None
                    else:
                        answer_raw = generate_explanation(df, question)
                        chart_path = generate_chart(df)

                formatted_answer = markdown.markdown(answer_raw)

                conversation.append({
                    "question": question,
                    "answer": formatted_answer,
                    "raw_answer": answer_raw,
                    "chart": chart_path
                })

                session["conversation"] = conversation
                session.modified = True

            except Exception as e:
                print("Processing error:", e)
                error = "⚠️ Internal server error."

    return render_template(
        "index.html",
        conversation=session.get("conversation", []),
        error=error
    )


@app.route("/clear")
def clear_chat():
    session.pop("conversation", None)
    return redirect(url_for("index"))


@app.route("/export")
def export_pdf():
    conversation = session.get("conversation", [])

    if not conversation:
        return redirect(url_for("index"))

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    elements = []

    styles = getSampleStyleSheet()

    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        alignment=4,
        spaceAfter=10,
    )

    elements.append(Paragraph("InsightX – UPI Intelligence Report", styles["Heading1"]))
    elements.append(Spacer(1, 0.4 * inch))

    for idx, chat in enumerate(conversation, 1):

        elements.append(Paragraph(f"<b>Question {idx}:</b>", styles["Heading2"]))
        elements.append(Spacer(1, 0.1 * inch))
        elements.append(Paragraph(chat["question"], body_style))
        elements.append(Spacer(1, 0.2 * inch))

        elements.append(Paragraph("<b>AI Analysis:</b>", styles["Heading3"]))
        elements.append(Spacer(1, 0.1 * inch))

        formatted_text = chat["raw_answer"].replace("\n", "<br/>")
        elements.append(Paragraph(formatted_text, body_style))
        elements.append(Spacer(1, 0.3 * inch))

        if chat.get("chart") and chat["chart"] and os.path.exists(chat["chart"]):
            img_reader = utils.ImageReader(chat["chart"])
            iw, ih = img_reader.getSize()
            aspect = ih / float(iw)

            elements.append(
                Image(
                    chat["chart"],
                    width=5 * inch,
                    height=(5 * inch * aspect)
                )
            )
            elements.append(Spacer(1, 0.4 * inch))

    doc.build(elements)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="InsightX_Report.pdf",
        mimetype="application/pdf"
    )


if __name__ == "__main__":
    app.run(debug=True)