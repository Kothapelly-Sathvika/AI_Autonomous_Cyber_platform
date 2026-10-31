---
kind: external_dependency
name: ReportLab PDF Generation
slug: reportlab
category: external_dependency
category_hints:
    - sdk_real_api
scope:
    - '**'
---

### ReportLab PDF Generation
- **Role**: Generates downloadable executive PDF reports containing attack summaries, statistics, charts, and security recommendations
- **Integration**: Used in `ui/reports.py` to create formatted PDF documents with tables, text layouts, and embedded analytics
- **Usage model**: Reports include attack summary, top attack types breakdown, recent incidents table, and security recommendations based on current threat data
- **Output**: Downloadable PDF files generated on-demand through the Reports UI page