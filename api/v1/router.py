"""
Purpose:
API v1 Router Specifications for Jarvis AI OS (Sprint v4.1).

Namespaces:
- /api/v1/chat
- /api/v1/tasks
- /api/v1/auth
- /api/v1/health
- /api/v1/metrics
- /api/v1/analytics
- /api/v1/billing
- /api/v1/marketplace
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
