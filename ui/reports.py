"""
Reports – generate downloadable PDF summary reports
"""
import streamlit as st
import pandas as pd
import io
from core.database import get_incidents_df
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import plotly.express as px


def show_reports():
    st.markdown("## 📑 Report Generator")
    st.markdown("---")

    df = get_incidents_df(5000)
    if df.empty:
        st.info("No incident data available to generate reports.")
        return

    st.markdown("### Report Preview")
    total = len(df)
    crit = int((df["severity"] == "Critical").sum())
    high = int((df["severity"] == "High").sum())
    avg_conf = df["confidence"].mean() * 100 if "confidence" in df.columns else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Incidents", total)
    c2.metric("Critical", crit)
    c3.metric("High", high)
    c4.metric("Avg Confidence", f"{avg_conf:.1f}%")

    st.markdown("### Top Attack Types")
    top = df["attack_type"].value_counts().head(5)
    st.bar_chart(top)

    st.markdown("### Recommendations")
    recs = [
        "Implement network segmentation to limit lateral movement",
        "Enable multi-factor authentication on all critical systems",
        "Deploy endpoint detection and response (EDR) agents",
        "Conduct regular penetration testing and vulnerability assessments",
        "Maintain up-to-date threat intelligence feeds",
    ]
    for r in recs:
        st.markdown(f"- {r}")

    st.markdown("---")
    pdf_buf = _build_pdf(df)
    st.download_button(
        "📄 Download Full PDF Report",
        pdf_buf, file_name="cyber_defense_report.pdf", mime="application/pdf",
        width="stretch"
    )


def _build_pdf(df):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph("Autonomous AI Cyber Defense – Executive Report", styles["Title"]))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(
        f"Report Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]
    ))
    elements.append(Spacer(1, 20))

    # Summary stats
    total = len(df)
    sev = df["severity"].value_counts().to_dict()
    elements.append(Paragraph(f"<b>Total Incidents:</b> {total}", styles["Normal"]))
    for k, v in sev.items():
        elements.append(Paragraph(f"  • {k}: {v}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Attack breakdown
    elements.append(Paragraph("<b>Attack Type Breakdown</b>", styles["Heading3"]))
    atk = df["attack_type"].value_counts().head(10).reset_index()
    atk.columns = ["Attack Type", "Count"]
    atk_data = [["Attack Type", "Count"]] + atk.values.tolist()
    t = Table(atk_data, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#161b22")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#0d1117")),
        ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#c9d1d9")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#30363d")),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 20))

    # Recent incidents
    elements.append(Paragraph("<b>Recent Incidents (Top 20)</b>", styles["Heading3"]))
    cols = ["incident_id", "attack_type", "severity", "source_ip", "confidence"]
    inc_data = [cols]
    for _, row in df.head(20).iterrows():
        inc_data.append([str(row.get(c, ""))[:25] for c in cols])
    t2 = Table(inc_data, repeatRows=1)
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#161b22")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#0d1117")),
        ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#c9d1d9")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#30363d")),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
    ]))
    elements.append(t2)
    elements.append(Spacer(1, 20))

    # Recommendations
    elements.append(Paragraph("<b>Recommendations</b>", styles["Heading3"]))
    recs = [
        "Implement network segmentation to limit lateral movement",
        "Enable multi-factor authentication on all critical systems",
        "Deploy endpoint detection and response (EDR) agents",
        "Conduct regular penetration testing and vulnerability assessments",
        "Maintain up-to-date threat intelligence feeds",
    ]
    for r in recs:
        elements.append(Paragraph(f"• {r}", styles["Normal"]))

    doc.build(elements)
    buf.seek(0)
    return buf
