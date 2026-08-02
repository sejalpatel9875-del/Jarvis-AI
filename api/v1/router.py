"""
Purpose:
API v1 Router Specifications for Jarvis AI OS (Sprint v4.7 Product Polish & Launch Readiness Platform).

Namespaces:
- /api/v1/chat
- /api/v1/tasks
- /api/v1/auth
- /api/v1/health
- /api/v1/metrics
- /api/v1/analytics
- /api/v1/billing
- /api/v1/marketplace
- /api/v1/orgs
- /api/v1/workspaces
- /api/v1/apikeys
- /api/v1/audit-logs
- /api/v1/ceo-dashboard
- /api/v1/knowledge/query
- /api/v1/knowledge/report
- /api/v1/knowledge/timeline
- /api/v1/workflows/create
- /api/v1/workflows/execute
- /api/v1/workflows/history
- /api/v1/crm/leads
- /api/v1/crm/deals
- /api/v1/crm/ai-assist
- /api/v1/activity-feed
- /api/v1/team-inbox/messages
- /api/v1/reminders
- /api/v1/search
- /api/v1/command-palette
- /api/v1/onboarding/status
"""

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from api.routes import (
    health_check,
    get_metrics,
    chat_endpoint,
    chat_stream_endpoint,
    list_tasks,
    create_task,
    register_account,
    login_account,
    get_analytics,
    get_billing_plans,
    list_marketplace_agents,
    upload_document,
    query_documents,
    get_status,
)
from core.workspaces import workspace_manager
from core.rbac import rbac_service
from services.api_keys import api_key_service
from services.audit_logger import audit_logger
from services.dashboard import ceo_dashboard
from services.knowledge_engine import knowledge_engine
from services.report_generator import report_generator
from services.knowledge_timeline import knowledge_timeline
from services.automation_engine import automation_engine
from services.workflow_execution import workflow_execution
from services.workflow_scheduler import workflow_scheduler
from services.crm_engine import crm_engine
from services.deal_pipeline import deal_pipeline
from services.lead_ai_assistant import lead_ai_assistant
from services.activity_feed import activity_feed
from services.team_inbox import team_inbox
from services.calendar_reminders import calendar_reminders
from services.global_search import global_search
from services.command_palette import command_palette
from services.onboarding_wizard import onboarding_wizard
from services.llm_router import ask_ai
from services.notifications import notification_service
from services.redis_cache import redis_cache
from services.task_queue import task_queue
from services.voice_pipeline import voice_pipeline
from memory.storage import load_recent
import agents.memory as memory_agent
from core.agent_os import agent_os
from services.desktop_assistant import desktop_assistant
from mcp.manager import mcp_manager
from mcp.models import MCPClientConfig

v1_router = APIRouter(prefix="/v1")


class MCPConnectPayload(BaseModel):
    name: str
    transport: str = "http"
    url: str = ""
    auth_token: str = ""
    timeout_seconds: float = 10.0


class MCPExecutePayload(BaseModel):
    server_name: str
    tool_name: str
    arguments: dict = {}
    fallback_internal_tool: str = ""


class DesktopActionPayload(BaseModel):
    action: str
    params: dict = {}
    is_confirmed: bool = False
    task_id: str = ""


class AgentOSDispatchPayload(BaseModel):
    goal: str
    context: dict = {}


class AgentExecutionRequest(BaseModel):
    agent_id: str
    request: str
    workspace_id: str = "default"


class VoiceSynthesisRequest(BaseModel):
    text: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class CreateTeamRequest(BaseModel):
    workspace_id: str
    name: str


class AddMemberRequest(BaseModel):
    team_id: str
    user_id: str
    role: str = "employee"


_AGENT_CATALOG = [
    {
        "id": "ceo",
        "name": "CEO Agent",
        "icon": "👑",
        "role": "Executive decisions, KPIs and business recommendations",
        "capability": "Executive dashboard",
    },
    {
        "id": "planner",
        "name": "Planner Agent",
        "icon": "📋",
        "role": "Goals, task breakdowns and execution plans",
        "capability": "Autonomous planning",
    },
    {
        "id": "reasoning",
        "name": "Reasoning Agent",
        "icon": "🧠",
        "role": "Complex, multi-step decision analysis",
        "capability": "Structured reasoning",
    },
    {
        "id": "validator",
        "name": "Validator Agent",
        "icon": "✅",
        "role": "Output checks, risks and verification",
        "capability": "Quality validation",
    },
    {
        "id": "executor",
        "name": "Executor Agent",
        "icon": "⚡",
        "role": "Creates executable task plans and workflow handoffs",
        "capability": "Task execution",
    },
    {
        "id": "knowledge",
        "name": "Knowledge Agent",
        "icon": "📚",
        "role": "RAG document and knowledge-base questions",
        "capability": "Semantic retrieval",
    },
    {
        "id": "crm",
        "name": "CRM Agent",
        "icon": "💼",
        "role": "Lead, contact and opportunity intelligence",
        "capability": "CRM pipeline",
    },
    {
        "id": "sales",
        "name": "Sales AI Agent",
        "icon": "💰",
        "role": "Follow-ups, lead scoring and sales suggestions",
        "capability": "Sales assistance",
    },
    {
        "id": "automation",
        "name": "Automation Agent",
        "icon": "⚙️",
        "role": "Workflow design and automation guidance",
        "capability": "Workflow engine",
    },
    {
        "id": "search",
        "name": "Search Agent",
        "icon": "🔍",
        "role": "Searches workspace leads, deals, activity and workflows",
        "capability": "Global search",
    },
    {
        "id": "memory",
        "name": "Memory Agent",
        "icon": "🧠",
        "role": "Preferences and conversation context",
        "capability": "Persistent memory",
    },
    {
        "id": "activity",
        "name": "Activity Feed Agent",
        "icon": "📢",
        "role": "Workspace events and operational timeline",
        "capability": "Activity feed",
    },
    {
        "id": "notification",
        "name": "Notification Agent",
        "icon": "🔔",
        "role": "Dashboard alerts and reminders",
        "capability": "Notifications",
    },
    {
        "id": "dashboard",
        "name": "Dashboard Agent",
        "icon": "📊",
        "role": "CEO metrics, pipeline and system health",
        "capability": "Business dashboard",
    },
    {
        "id": "workspace",
        "name": "Workspace Agent",
        "icon": "🏢",
        "role": "Organizations and workspace isolation",
        "capability": "Workspace management",
    },
    {
        "id": "authentication",
        "name": "Authentication Agent",
        "icon": "🔐",
        "role": "JWT sessions and secure access status",
        "capability": "Authentication",
    },
    {
        "id": "rbac",
        "name": "RBAC Agent",
        "icon": "👥",
        "role": "Role and permission evaluation",
        "capability": "Access control",
    },
    {
        "id": "security",
        "name": "Security Agent",
        "icon": "🛡️",
        "role": "Security controls and request protections",
        "capability": "Security posture",
    },
    {
        "id": "rate-limiter",
        "name": "Rate Limiter Agent",
        "icon": "🚫",
        "role": "Brute-force protection controls",
        "capability": "Rate limiting",
    },
    {
        "id": "database",
        "name": "Database Agent",
        "icon": "🗄️",
        "role": "Workspace data-store readiness",
        "capability": "SQLite adapter",
    },
    {
        "id": "cache",
        "name": "Redis Cache Agent",
        "icon": "⚡",
        "role": "Fast retrieval with safe local fallback",
        "capability": "Cache layer",
    },
    {
        "id": "commands",
        "name": "Command Palette Agent",
        "icon": "⌨️",
        "role": "Keyboard shortcuts and global actions",
        "capability": "Command palette",
    },
    {
        "id": "onboarding",
        "name": "Onboarding Agent",
        "icon": "🎯",
        "role": "First-workspace setup progress",
        "capability": "Onboarding",
    },
]


@v1_router.get("/agents", tags=["v1 Agent Hub"])
def list_agent_catalog():
    return {"agents": [{**agent, "status": "ready"} for agent in _AGENT_CATALOG]}


@v1_router.post("/agents/execute", tags=["v1 Agent Hub"])
def execute_agent(request: AgentExecutionRequest):
    agent_id = request.agent_id.strip().lower()
    prompt = request.request.strip()
    workspace_id = request.workspace_id.strip() or "default"
    if not prompt:
        raise HTTPException(
            status_code=400, detail="Tell the selected agent what you want it to do."
        )
    if agent_id not in {agent["id"] for agent in _AGENT_CATALOG}:
        raise HTTPException(status_code=404, detail="Unknown agent.")

    try:
        if agent_id in {"ceo", "dashboard"}:
            result = ceo_dashboard.get_dashboard_summary(workspace_id=workspace_id)
            output = ask_ai(
                f"You are the CEO Agent. Reply in the same primary language and script as the user. Review these live workspace metrics and answer the request concisely with recommendations. Metrics: {result}\nRequest: {prompt}"
            )
        elif agent_id == "knowledge":
            result = knowledge_engine.query_workspace_knowledge(workspace_id, prompt, 5)
            output = (
                result.get("formatted_answer")
                or result.get("answer")
                or "No matching knowledge found."
            )
        elif agent_id == "search":
            result = global_search.search_all(workspace_id, prompt)
            output = f"Found {result['total_matches']} workspace matches. Leads: {len(result['leads'])}; deals: {len(result['deals'])}; workflows: {len(result['workflows'])}; activity: {len(result['activity_feed'])}."
        elif agent_id == "executor":
            task = task_queue.create_task(prompt, ["Plan", "Execute", "Validate"])
            output = f"Execution task queued: {task.to_dict().get('description', prompt)}"
        elif agent_id == "activity":
            result = activity_feed.get_activity_feed(workspace_id, limit=10)
            output = "Recent activity:\n" + (
                "\n".join(f"• {item.get('action')}: {item.get('details')}" for item in result)
                or "No activity recorded yet."
            )
        elif agent_id == "notification":
            result = notification_service.send_notification(
                "default_user", "JARVIS agent request", prompt, "dashboard"
            )
            output = (
                "Dashboard notification created."
                if result.get("success")
                else result.get("error", "Could not create notification.")
            )
        elif agent_id == "memory":
            learned = memory_agent.auto_learn_from_input(prompt)
            output = memory_agent.get_memory_context() + (
                f"\nNew facts learned: {learned}"
                if learned
                else "\nNo new preference pattern detected; current context is ready."
            )
        elif agent_id == "automation":
            workflows = automation_engine.list_workflows(workspace_id)
            output = ask_ai(
                f"You are the Automation Agent. Reply in the same primary language and script as the user. Design a safe no-code workflow for: {prompt}\nExisting workflows: {workflows}. Do not claim external actions were sent unless listed as configured."
            )
        elif agent_id == "crm":
            leads = crm_engine.list_leads(workspace_id)
            output = ask_ai(
                f"You are the CRM Agent. Reply in the same primary language and script as the user. Use this live lead data to answer: {prompt}\nLeads: {leads}"
            )
        elif agent_id == "sales":
            leads = crm_engine.list_leads(workspace_id)
            output = ask_ai(
                f"You are the Sales AI Agent. Reply in the same primary language and script as the user. Draft practical, compliant sales guidance for: {prompt}\nLead data: {leads}"
            )
        elif agent_id == "workspace":
            output = f"Workspace '{workspace_id}' is isolated for this session. Create and manage organizations/workspaces through the Workspace API before inviting additional members. Request noted: {prompt}"
        elif agent_id == "rbac":
            output = f"RBAC check: owner can run AI={rbac_service.check_permission('owner', 'run_ai')}; employee can run AI={rbac_service.check_permission('employee', 'run_ai')}; employee can view reports={rbac_service.check_permission('employee', 'view_reports')}. Request: {prompt}"
        elif agent_id == "cache":
            output = f"Cache ready. Redis connected: {redis_cache.is_redis_active}. Local in-memory fallback is active when Redis is unavailable. Request: {prompt}"
        elif agent_id == "commands":
            commands = command_palette.get_available_commands("owner")
            output = "Available commands:\n" + "\n".join(
                f"• {item['shortcut']} — {item['title']}" for item in commands
            )
        elif agent_id == "onboarding":
            result = onboarding_wizard.get_onboarding_status(workspace_id)
            output = f"Onboarding status: {result}"
        elif agent_id in {"authentication", "security", "rate-limiter", "database"}:
            details = {
                "authentication": "Signed JWT browser sessions are enabled; the session cookie is HTTP-only and secure in production.",
                "security": "Security headers, authenticated API access, XSS-safe UI rendering, and parameterized SQLite queries are enabled.",
                "rate-limiter": "Authentication rate limiting is enabled by middleware to reduce brute-force attempts.",
                "database": "SQLite workspace database is operational. On Vercel it is ephemeral; use managed PostgreSQL for durable multi-user production data.",
            }
            output = f"{details[agent_id]} Request: {prompt}"
        else:
            roles = {
                "planner": "goal planning and ordered execution steps",
                "reasoning": "structured multi-step reasoning",
                "validator": "quality validation and risk detection",
            }
            output = ask_ai(
                f"You are the JARVIS {roles[agent_id]} agent. Reply in the same primary language and script as the user. For the request below, give useful work product without revealing private chain-of-thought. Request: {prompt}"
            )
        activity_feed.log_activity(
            workspace_id,
            f"{agent_id.title()} Agent",
            "agent_request_completed",
            prompt[:240],
            "AI_AGENT",
        )
        return {"status": "completed", "agent_id": agent_id, "output": output}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {exc}")


@v1_router.get("/conversations", tags=["v1 Conversation Memory"])
def get_conversation_history(limit: int = 100):
    turns = load_recent(max(1, min(limit, 100)))
    return {
        "conversations": [
            {
                "id": turn.id,
                "timestamp": turn.timestamp,
                "user_message": turn.user_message,
                "assistant_reply": turn.assistant_reply,
                "provider": turn.provider,
            }
            for turn in turns
        ]
    }


@v1_router.post("/voice/transcribe", tags=["v1 Voice"])
async def transcribe_voice_command(file: UploadFile = File(...)):
    audio = await file.read()
    if not audio:
        raise HTTPException(status_code=400, detail="No audio was received.")
    if len(audio) > 12 * 1024 * 1024:
        raise HTTPException(
            status_code=413, detail="Voice recording is too large. Please keep it under 12 MB."
        )
    try:
        text = voice_pipeline.transcribe_audio(
            audio, file.filename or "voice.webm", file.content_type or "audio/webm"
        )
        if not text:
            raise HTTPException(
                status_code=422, detail="I could not understand that recording. Please try again."
            )
        return {"text": text}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@v1_router.post("/voice/synthesize", tags=["v1 Voice"])
async def synthesize_voice_reply(request: VoiceSynthesisRequest):
    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="No text was received for speech synthesis.")
    return StreamingResponse(voice_pipeline.stream_neural_speech(text), media_type="audio/mpeg")


# System & Health
v1_router.add_api_route("/status", get_status, methods=["GET"], tags=["v1 System"])
v1_router.add_api_route("/health", health_check, methods=["GET"], tags=["v1 System"])
v1_router.add_api_route("/metrics", get_metrics, methods=["GET"], tags=["v1 Metrics"])

# Auth & User Accounts
v1_router.add_api_route("/auth/register", register_account, methods=["POST"], tags=["v1 User Auth"])
v1_router.add_api_route("/auth/login", login_account, methods=["POST"], tags=["v1 User Auth"])


@v1_router.post("/auth/refresh", tags=["v1 User Auth"])
def refresh_auth_token(request: RefreshTokenRequest):
    from core.auth import auth_service

    res = auth_service.verify_token(request.refresh_token)
    if not res.get("valid"):
        raise HTTPException(status_code=401, detail=res.get("error", "Invalid refresh token."))
    payload = res.get("payload", {})
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Token type must be refresh.")
    new_tokens = auth_service.create_tokens(
        payload.get("sub"), payload.get("email"), payload.get("role", "user")
    )
    return new_tokens


# Chat AI
v1_router.add_api_route("/chat", chat_endpoint, methods=["POST"], tags=["v1 Chat AI"])
v1_router.add_api_route("/chat/stream", chat_stream_endpoint, methods=["POST"], tags=["v1 Chat AI"])

# Task Engine
v1_router.add_api_route("/tasks", list_tasks, methods=["GET"], tags=["v1 Task Engine"])
v1_router.add_api_route("/tasks", create_task, methods=["POST"], tags=["v1 Task Engine"])

# Document AI
v1_router.add_api_route("/upload", upload_document, methods=["POST"], tags=["v1 Document AI"])
v1_router.add_api_route(
    "/documents/query", query_documents, methods=["POST"], tags=["v1 Document AI"]
)

# Analytics, Billing & Marketplace
v1_router.add_api_route("/analytics", get_analytics, methods=["GET"], tags=["v1 Analytics"])
v1_router.add_api_route("/billing/plans", get_billing_plans, methods=["GET"], tags=["v1 Billing"])
v1_router.add_api_route(
    "/marketplace/agents", list_marketplace_agents, methods=["GET"], tags=["v1 Marketplace"]
)


# SaaS Core Endpoints
@v1_router.post("/orgs", tags=["v1 SaaS Core"])
def create_org_endpoint(name: str, owner_id: str, plan: str = "business"):
    return workspace_manager.create_organization(name, owner_id, plan)


@v1_router.post("/workspaces", tags=["v1 SaaS Core"])
def create_workspace_endpoint(org_id: str, name: str, department: str = "General"):
    return workspace_manager.create_workspace(org_id, name, department)


@v1_router.get("/workspaces", tags=["v1 SaaS Core"])
def list_workspaces_endpoint(org_id: str):
    return {"workspaces": workspace_manager.list_workspaces(org_id)}


@v1_router.post("/teams", tags=["v1 SaaS Core"])
def create_team_endpoint(request: CreateTeamRequest):
    res = workspace_manager.create_team(request.workspace_id, request.name)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res


@v1_router.post("/teams/members", tags=["v1 SaaS Core"])
def add_team_member_endpoint(request: AddMemberRequest):
    res = workspace_manager.add_team_member(request.team_id, request.user_id, request.role)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res


@v1_router.get("/teams", tags=["v1 SaaS Core"])
def list_teams_endpoint(workspace_id: str):
    return {"teams": workspace_manager.list_teams(workspace_id)}


@v1_router.post("/apikeys", tags=["v1 SaaS Core"])
def generate_apikey_endpoint(workspace_id: str, name: str = "Default Key"):
    return api_key_service.generate_key(workspace_id, name)


@v1_router.get("/audit-logs", tags=["v1 SaaS Core"])
def get_audit_logs_endpoint(org_id: str = None, workspace_id: str = None):
    return {"logs": audit_logger.get_logs(org_id, workspace_id)}


@v1_router.get("/ceo-dashboard", tags=["v1 SaaS Core"])
def get_ceo_dashboard_endpoint(org_id: str = None, workspace_id: str = "default"):
    return {"dashboard": ceo_dashboard.get_dashboard_summary(org_id, workspace_id)}


# Knowledge Intelligence Platform Endpoints
@v1_router.post("/knowledge/query", tags=["v1 Knowledge Platform"])
def query_knowledge_endpoint(workspace_id: str, query: str, top_k: int = 5):
    return knowledge_engine.query_workspace_knowledge(workspace_id, query, top_k)


@v1_router.post("/knowledge/report", tags=["v1 Knowledge Platform"])
def generate_report_endpoint(title: str, topic: str, context_text: str = ""):
    return report_generator.generate_executive_report(title, topic, context_text)


@v1_router.get("/knowledge/timeline", tags=["v1 Knowledge Platform"])
def get_timeline_endpoint(workspace_id: str = "default", limit: int = 30):
    return {"timeline": knowledge_timeline.get_timeline(workspace_id, limit)}


# Automation Engine Endpoints
@v1_router.post("/workflows/create", tags=["v1 Automation Engine"])
def create_workflow_endpoint(workspace_id: str, name: str, trigger_type: str, action_type: str):
    return automation_engine.create_workflow(workspace_id, name, trigger_type, action_type)


@v1_router.post("/workflows/execute", tags=["v1 Automation Engine"])
def execute_workflow_endpoint(workflow_id: int):
    return workflow_execution.execute_workflow(workflow_id)


@v1_router.get("/workflows/history", tags=["v1 Automation Engine"])
def get_workflow_history_endpoint(workspace_id: str = "default", limit: int = 30):
    return {"history": workflow_execution.get_execution_history(workspace_id, limit)}


# Business CRM & Lead Platform Endpoints
@v1_router.post("/crm/leads", tags=["v1 Business CRM"])
def create_lead_endpoint(workspace_id: str, name: str, email: str, company: str = ""):
    return crm_engine.create_lead(workspace_id, name, email, company)


@v1_router.get("/crm/leads", tags=["v1 Business CRM"])
def list_leads_endpoint(workspace_id: str = "default", status: str = None):
    return {"leads": crm_engine.list_leads(workspace_id, status)}


@v1_router.post("/crm/deals", tags=["v1 Business CRM"])
def create_deal_endpoint(lead_id: int, workspace_id: str, title: str, value_usd: float):
    return deal_pipeline.create_deal(lead_id, workspace_id, title, value_usd)


@v1_router.get("/crm/deals/pipeline", tags=["v1 Business CRM"])
def get_deal_pipeline_endpoint(workspace_id: str = "default"):
    return {"pipeline": deal_pipeline.get_pipeline_summary(workspace_id)}


@v1_router.post("/crm/ai/draft-email", tags=["v1 Business CRM"])
def draft_sales_email_endpoint(lead_id: int, tone: str = "professional"):
    return lead_ai_assistant.draft_followup_email(lead_id, tone)


# Communication Hub & Activity Feed Endpoints
@v1_router.get("/activity-feed", tags=["v1 Communication Hub"])
def get_activity_feed_endpoint(workspace_id: str = "default", limit: int = 30):
    return {"activity_feed": activity_feed.get_activity_feed(workspace_id, limit)}


@v1_router.post("/team-inbox/messages", tags=["v1 Communication Hub"])
def send_team_message_endpoint(workspace_id: str, channel: str, sender: str, message: str):
    return team_inbox.send_message(workspace_id, channel, sender, message)


@v1_router.get("/team-inbox/messages", tags=["v1 Communication Hub"])
def get_team_messages_endpoint(
    workspace_id: str = "default", channel: str = "SALES", limit: int = 50
):
    return {"messages": team_inbox.get_channel_messages(workspace_id, channel, limit)}


@v1_router.post("/reminders", tags=["v1 Communication Hub"])
def create_reminder_endpoint(workspace_id: str, title: str, due_at: str = "", assignee: str = "me"):
    return calendar_reminders.create_reminder(workspace_id, title, due_at, assignee)


@v1_router.get("/reminders", tags=["v1 Communication Hub"])
def list_reminders_endpoint(workspace_id: str = "default", pending_only: bool = True):
    return {"reminders": calendar_reminders.list_reminders(workspace_id, pending_only)}


# Product Polish & Global Experience Endpoints
@v1_router.get("/search", tags=["v1 Product Polish"])
def global_search_endpoint(workspace_id: str = "default", query: str = ""):
    return global_search.search_all(workspace_id, query)


@v1_router.get("/search/history", tags=["v1 Product Polish"])
def get_search_history_endpoint(workspace_id: str = "default", limit: int = 20):
    return {"history": global_search.get_history(workspace_id, limit)}


@v1_router.get("/command-palette", tags=["v1 Product Polish"])
def get_command_palette_endpoint(role: str = "owner"):
    return {"commands": command_palette.get_available_commands(role)}


@v1_router.get("/onboarding/status", tags=["v1 Product Polish"])
def get_onboarding_status_endpoint(workspace_id: str = "default"):
    return onboarding_wizard.get_onboarding_status(workspace_id)


@v1_router.post("/onboarding/complete-step", tags=["v1 Product Polish"])
def complete_onboarding_step_endpoint(
    workspace_id: str = "default", step_name: str = "workspace_setup"
):
    return onboarding_wizard.complete_onboarding_step(workspace_id, step_name)


# Multi-Agent AI OS Endpoints
@v1_router.post("/agent-os/dispatch", tags=["v5.2 Multi-Agent AI OS"])
def dispatch_agent_os_goal(payload: AgentOSDispatchPayload):
    return agent_os.dispatch_goal(payload.goal, payload.context)


@v1_router.get("/agent-os/agents", tags=["v5.2 Multi-Agent AI OS"])
def list_agent_os_agents():
    return agent_os.get_system_status()


@v1_router.post("/agent-os/cancel/{task_id}", tags=["v5.2 Multi-Agent AI OS"])
def cancel_agent_os_task(task_id: str):
    return agent_os.cancel_goal(task_id)


# Desktop Productivity Assistant Endpoints
@v1_router.post("/desktop/execute", tags=["v5.3 Desktop Assistant"])
def execute_desktop_action_endpoint(payload: DesktopActionPayload):
    return desktop_assistant.execute_desktop_action(
        payload.action, payload.params, payload.is_confirmed, payload.task_id
    )


@v1_router.post("/desktop/confirm", tags=["v5.3 Desktop Assistant"])
def confirm_desktop_action_endpoint(payload: DesktopActionPayload):
    return desktop_assistant.execute_desktop_action(
        payload.action, payload.params, is_confirmed=True, task_id=payload.task_id
    )


@v1_router.get("/desktop/audit-logs", tags=["v5.3 Desktop Assistant"])
def get_desktop_audit_logs_endpoint(limit: int = 50):
    return {"audit_logs": audit_logger.get_logs(limit=limit)}


# Model Context Protocol (MCP) Endpoints
@v1_router.get("/mcp/servers", tags=["v5.6 Model Context Protocol"])
def list_mcp_servers_endpoint():
    return {"servers": mcp_manager.get_server_statuses()}


@v1_router.post("/mcp/servers/connect", tags=["v5.6 Model Context Protocol"])
def connect_mcp_server_endpoint(payload: MCPConnectPayload):
    cfg = MCPClientConfig(
        name=payload.name,
        transport=payload.transport,
        url=payload.url,
        auth_token=payload.auth_token if payload.auth_token else None,
        timeout_seconds=payload.timeout_seconds,
    )
    success = mcp_manager.add_server(cfg)
    return {
        "success": success,
        "server_name": payload.name,
        "status": "CONNECTED" if success else "FAILED",
    }


@v1_router.get("/mcp/tools", tags=["v5.6 Model Context Protocol"])
def list_mcp_tools_endpoint():
    return {"tools": mcp_manager.discover_all_tools()}


@v1_router.post("/mcp/tools/execute", tags=["v5.6 Model Context Protocol"])
def execute_mcp_tool_endpoint(payload: MCPExecutePayload):
    res = mcp_manager.execute_tool_with_fallback(
        payload.server_name,
        payload.tool_name,
        payload.arguments,
        fallback_internal_tool=(
            payload.fallback_internal_tool if payload.fallback_internal_tool else None
        ),
    )
    return res.to_dict()
