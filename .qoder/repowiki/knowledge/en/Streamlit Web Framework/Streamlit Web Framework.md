---
kind: external_dependency
name: Streamlit Web Framework
slug: streamlit
category: external_dependency
category_hints:
    - framework_behavior
scope:
    - '**'
---

### Streamlit Web Framework
- **Role**: Primary frontend framework powering the entire UI — sidebar navigation, page routing, session state, widgets, and layout
- **Integration**: `app.py` sets page config (`set_page_config`), manages sidebar with `st.radio`, handles authentication via `st.session_state`, and routes to individual UI modules
- **Configuration**: `.streamlit/config.toml` controls theme colors, server port (8501), headless mode, and usage stats collection
- **Pattern**: Each UI feature is a separate module under `ui/` imported lazily by the main router to avoid circular imports