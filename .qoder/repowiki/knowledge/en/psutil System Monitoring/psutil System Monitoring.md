---
kind: external_dependency
name: psutil System Monitoring
slug: psutil
category: external_dependency
category_hints:
    - client_constraint
scope:
    - '**'
---

### psutil System Resource Monitoring
- **Role**: Real-time system resource monitoring displaying CPU, RAM, and disk usage on the dashboard
- **Integration**: Used in `ui/dashboard.py` to fetch live system metrics and display them as KPI cards alongside threat statistics
- **Usage model**: Periodic polling of system resources to show current utilization levels in the dashboard interface