"""
Incident Center – search, filter, export incidents
"""
import streamlit as st
import pandas as pd
from core.incident_manager import search_incidents, update_incident_status, export_csv, get_stats
from core.database import get_incidents_df
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import io


def show_incidents():
    st.markdown("## 🗂️ Incident Center")
    st.markdown("---")

    stats = get_stats()
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("Total Incidents", stats["total"])
    with c2:
        st.metric("Critical", stats["critical"])
    with c3:
        st.metric("High", stats["high"])
    with c4:
        st.metric("Open", stats["open"])
    with c5:
        st.metric("Resolved", stats["resolved"])

    st.markdown("---")

    # Search & filter
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        query = st.text_input("🔍 Search incidents", placeholder="ID, IP, attack type…")
    with col2:
        severity = st.selectbox("Severity", ["All", "Low", "Medium", "High", "Critical"])
    with col3:
        status = st.selectbox("Status", ["All", "open", "resolved", "investigating"])

    df = search_incidents(query, severity, status)

    if df.empty:
        st.info("No incidents match your filters.")
        return

    # Display
    display_cols = ["incident_id", "timestamp", "attack_type", "severity",
                    "source_ip", "confidence", "status"]
    available = [c for c in display_cols if c in df.columns]
    st.dataframe(df[available], width="stretch", hide_index=True, height=350)

    # Actions
    st.markdown("### ⚙️ Actions")
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        csv_data = export_csv(df)
        st.download_button("📥 Export CSV", csv_data, "incidents.csv", "text/csv")

    with c2:
        pdf_buf = _generate_pdf(df)
        st.download_button("📄 Export PDF", pdf_buf, "incidents.pdf", "application/pdf")

    with c3:
        sel_id = st.text_input("Incident ID to resolve")
        if st.button("✅ Mark Resolved"):
            if sel_id:
                update_incident_status(sel_id, "resolved")
                st.success(f"Incident {sel_id} marked as resolved.")
                st.rerun()

    with c4:
        sel_id2 = st.text_input("Incident ID to investigate")
        if st.button("🔬 Mark Investigating"):
            if sel_id2:
                update_incident_status(sel_id2, "investigating")
                st.success(f"Incident {sel_id2} marked as investigating.")
                st.rerun()


def _generate_pdf(df):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Cyber Defense Incident Report", styles["Title"]))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Summary
    elements.append(Paragraph(f"Total Incidents: {len(df)}", styles["Normal"]))
    elements.append(Spacer(1, 6))

    # Table (limit to 30 rows)
    cols = ["incident_id", "attack_type", "severity", "source_ip", "status"]
    data = [cols]
    for _, row in df.head(30).iterrows():
        data.append([str(row.get(c, "")) for c in cols])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#161b22")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#0d1117")),
        ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#c9d1d9")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#30363d")),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
    ]))
    elements.append(table)
    doc.build(elements)
    buf.seek(0)
    return buf
