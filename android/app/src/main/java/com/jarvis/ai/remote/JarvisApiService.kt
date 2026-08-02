package com.jarvis.ai.remote

import retrofit2.Response
import retrofit2.http.*

data class ChatRequest(val message: str = "", val workspace_id: String = "default")
data class ChatResponse(val response: String, val status: String)

data class DesktopActionRequest(
    val action: String,
    val params: Map<String, Any> = emptyMap(),
    val is_confirmed: Boolean = false
)
data class DesktopActionResponse(
    val success: Boolean,
    val action: String,
    val status: String,
    val result: Map<String, Any>? = null,
    val confirmation_prompt: String? = null
)

data class ActivityFeedResponse(val activity_feed: List<Map<String, Any>>)
data class RemindersResponse(val reminders: List<Map<String, Any>>)
data class SystemStatusResponse(val status: String, val active_agents: Int)

interface JarvisApiService {
    @POST("api/v1/chat")
    suspend fun sendChatMessage(@Body request: ChatRequest): Response<ChatResponse>

    @POST("api/v1/desktop/execute")
    suspend fun executeDesktopAction(@Body request: DesktopActionRequest): Response<DesktopActionResponse>

    @POST("api/v1/desktop/confirm")
    suspend fun confirmDesktopAction(@Body request: DesktopActionRequest): Response<DesktopActionResponse>

    @GET("api/v1/activity-feed")
    suspend fun getActivityFeed(@Query("workspace_id") workspaceId: String = "default"): Response<ActivityFeedResponse>

    @GET("api/v1/reminders")
    suspend fun getReminders(@Query("workspace_id") workspaceId: String = "default"): Response<RemindersResponse>

    @GET("api/v1/agent-os/agents")
    suspend fun getSystemStatus(): Response<SystemStatusResponse>
}
