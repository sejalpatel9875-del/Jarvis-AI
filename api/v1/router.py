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

from fastapi import APIRouter
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
    get_status
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

v1_router = APIRouter(prefix="/v1")

# System & Health
v1_router.add_api_route("/status", get_status, methods=["GET"], tags=["v1 System"])
v1_router.add_api_route("/health", health_check, methods=["GET"], tags=["v1 System"])
v1_router.add_api_route("/metrics", get_metrics, methods=["GET"], tags=["v1 Metrics"])

# Auth & User Accounts
v1_router.add_api_route("/auth/register", register_account, methods=["POST"], tags=["v1 User Auth"])
v1_router.add_api_route("/auth/login", login_account, methods=["POST"], tags=["v1 User Auth"])

# Chat AI
v1_router.add_api_route("/chat", chat_endpoint, methods=["POST"], tags=["v1 Chat AI"])
v1_router.add_api_route("/chat/stream", chat_stream_endpoint, methods=["POST"], tags=["v1 Chat AI"])

# Task Engine
v1_router.add_api_route("/tasks", list_tasks, methods=["GET"], tags=["v1 Task Engine"])
v1_router.add_api_route("/tasks", create_task, methods=["POST"], tags=["v1 Task Engine"])

# Document AI
v1_router.add_api_route("/upload", upload_document, methods=["POST"], tags=["v1 Document AI"])
v1_router.add_api_route("/documents/query", query_documents, methods=["POST"], tags=["v1 Document AI"])

# Analytics, Billing & Marketplace
v1_router.add_api_route("/analytics", get_analytics, methods=["GET"], tags=["v1 Analytics"])
v1_router.add_api_route("/billing/plans", get_billing_plans, methods=["GET"], tags=["v1 Billing"])
v1_router.add_api_route("/marketplace/agents", list_marketplace_agents, methods=["GET"], tags=["v1 Marketplace"])

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
def get_team_messages_endpoint(workspace_id: str = "default", channel: str = "SALES", limit: int = 50):
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

@v1_router.get("/command-palette", tags=["v1 Product Polish"])
def get_command_palette_endpoint(role: str = "owner"):
    return {"commands": command_palette.get_available_commands(role)}

@v1_router.get("/onboarding/status", tags=["v1 Product Polish"])
def get_onboarding_status_endpoint(workspace_id: str = "default"):
    return onboarding_wizard.get_onboarding_status(workspace_id)

@v1_router.post("/onboarding/complete-step", tags=["v1 Product Polish"])
def complete_onboarding_step_endpoint(workspace_id: str = "default", step_name: str = "workspace_setup"):
    return onboarding_wizard.complete_onboarding_step(workspace_id, step_name)
