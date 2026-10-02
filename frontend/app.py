import uuid

import streamlit as st

from backend.ingestion.ingest import ingest_repository
from backend.graph.workflow import graph

from backend.ingestion.ingest import ingest_repository


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Repo-Memory-Agent",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* Main background */
    .stApp {
        background-color: #0e1117;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #11151c;
        border-right: 1px solid #262b35;
    }

    /* Header */
    .agent-header {
        padding: 10px 0 20px 0;
    }

    .agent-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 4px;
    }

    .agent-subtitle {
        color: #9ca3af;
        font-size: 0.95rem;
    }

    /* Status cards */
    .status-card {
        background-color: #161b22;
        border: 1px solid #262b35;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 10px;
    }

    .status-title {
        font-size: 0.8rem;
        color: #9ca3af;
        margin-bottom: 4px;
    }

    .status-value {
        font-size: 0.95rem;
        font-weight: 600;
    }

    /* Chat messages */
    [data-testid="stChatMessage"] {
        border-radius: 12px;
        margin-bottom: 10px;
    }

    /* Divider */
    .section-divider {
        border-top: 1px solid #262b35;
        margin: 20px 0;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "user_id" not in st.session_state:
    st.session_state.user_id = "demo-user"

if "project_id" not in st.session_state:
    st.session_state.project_id = "paperpilot"

if "messages" not in st.session_state:
    st.session_state.messages = []


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🧠 Repo-Memory-Agent")

    st.caption(
        "Agentic RAG assistant for understanding GitHub codebases."
    )

    st.markdown("---")

    # --------------------------------------------------------
    # PROJECT
    # --------------------------------------------------------

    st.markdown("### Repository")

    github_url = st.text_input(
        "GitHub URL",
        placeholder="https://github.com/user/repository",
        help="Repository ingestion will be connected here next.",
    )

    project_id = st.text_input(
        "Project ID",
        value=st.session_state.project_id,
    )

    st.session_state.project_id = project_id

    if st.button(
    "Load Repository",
    use_container_width=True,
):
        if not github_url:
            st.error("Please enter a GitHub repository URL.")

        elif not project_id:
            st.error("Please enter a project ID.")

        else:
            try:
                with st.spinner(
                f"Indexing repository '{project_id}'..."
            ):
                    ingest_repository(
                    repo_url=github_url,
                    project_id=project_id,
                )

                st.success(
                f"Repository '{project_id}' loaded successfully."
            )

            except Exception as e:
                st.error(
                f"Repository ingestion failed: {str(e)}"
            )

    st.markdown(
        '<div class="section-divider"></div>',
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # AGENT STATUS
    # --------------------------------------------------------

    st.markdown("### Agent Status")

    st.markdown(
        """
        <div class="status-card">
            <div class="status-title">Agent Router</div>
            <div class="status-value">🟢 Active</div>
        </div>

        <div class="status-card">
            <div class="status-title">RAG</div>
            <div class="status-value">🟢 Active</div>
        </div>

        <div class="status-card">
            <div class="status-title">Persistent Memory</div>
            <div class="status-value">🟢 Active</div>
        </div>

        <div class="status-card">
            <div class="status-title">Guardrails</div>
            <div class="status-value">🟢 Active</div>
        </div>

        <div class="status-card">
            <div class="status-title">LangGraph</div>
            <div class="status-value">🟢 Active</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-divider"></div>',
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # SESSION
    # --------------------------------------------------------

    st.markdown("### Session")

    st.caption(
        f"Thread: `{st.session_state.thread_id[:8]}...`"
    )

    st.caption(
        f"User: `{st.session_state.user_id}`"
    )

    st.caption(
        f"Project: `{st.session_state.project_id}`"
    )

    if st.button(
        "🗑️ New Conversation",
        use_container_width=True,
    ):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()


# ============================================================
# MAIN HEADER
# ============================================================

st.markdown(
    """
    <div class="agent-header">
        <div class="agent-title">
            🧠 Repo-Memory-Agent
        </div>

        <div class="agent-subtitle">
            Ask questions about your codebase using RAG,
            persistent memory, and guarded agentic reasoning.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# ============================================================
# CHAT INPUT
# ============================================================

question = st.chat_input(
    "Ask about your repository..."
)


# ============================================================
# PROCESS QUESTION
# ============================================================

if question:

    # --------------------------------------------------------
    # Display user message
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    # --------------------------------------------------------
    # Build LangGraph state
    # --------------------------------------------------------

    state = {
        "question": question,
        "context": "",
        "memories": "",
        "answer": "",

        "user_id": st.session_state.user_id,
        "project_id": st.session_state.project_id,

        "route": "",

        "input_allowed": True,
        "repository_allowed": True,
        "output_allowed": True,

        "guardrail_reason": "",

        "conversation": [],
    }

    config = {
        "configurable": {
            "thread_id": st.session_state.thread_id
        }
    }

    # --------------------------------------------------------
    # Run agent
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner("Agent is analyzing your question..."):

            try:

                result = graph.invoke(
                    state,
                    config=config,
                )

                # --------------------------------------------
                # Extract result
                # --------------------------------------------

                answer = result.get(
                    "answer",
                    "No response generated.",
                )

                route = result.get(
                    "route",
                    "unknown",
                )

                memories = result.get(
                    "memories",
                    "",
                )

                context = result.get(
                    "context",
                    "",
                )

                guardrail_reason = result.get(
                    "guardrail_reason",
                    "",
                )

                output_allowed = result.get(
                    "output_allowed",
                    True,
                )

                # --------------------------------------------
                # Display answer
                # --------------------------------------------

                st.markdown(answer)

                # --------------------------------------------
                # Agent metadata
                # --------------------------------------------

                with st.expander(
                    "🔍 Agent Details"
                ):

                    # ----------------------------------------
                    # Route
                    # ----------------------------------------

                    st.markdown("**Agent Route**")

                    route_labels = {
                        "repository": "📚 Repository",
                        "memory": "🧠 Persistent Memory",
                        "both": "🔀 Repository + Memory",
                        "direct": "💬 Direct",
                    }

                    st.info(
                        route_labels.get(
                            route,
                            f"❓ {route}",
                        )
                    )

                    st.markdown("---")

                    # ----------------------------------------
                    # Memory + Guardrails
                    # ----------------------------------------

                    col1, col2 = st.columns(2)

                    with col1:

                        st.markdown(
                            "**Persistent Memory**"
                        )

                        if memories:
                            st.caption(memories)
                        else:
                            st.caption(
                                "No persistent memory retrieved."
                            )

                    with col2:

                        st.markdown(
                            "**Guardrail Status**"
                        )

                        if output_allowed:
                            st.success(
                                "Output allowed"
                            )
                        else:
                            st.error(
                                guardrail_reason
                                or "Output blocked"
                            )

                    # ----------------------------------------
                    # Repository Context
                    # ----------------------------------------

                    if route in {
                        "repository",
                        "both",
                    }:

                        st.markdown("---")

                        st.markdown(
                            "**Repository Context Retrieved**"
                        )

                        if context:
                            st.caption(
                                "Repository information was "
                                "retrieved for this question."
                            )
                        else:
                            st.caption(
                                "No repository context retrieved."
                            )

                # --------------------------------------------
                # Save UI message
                # --------------------------------------------

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                    }
                )

            except Exception as e:

                error_message = (
                    f"Agent error: `{str(e)}`"
                )

                st.error(error_message)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message,
                    }
                )
