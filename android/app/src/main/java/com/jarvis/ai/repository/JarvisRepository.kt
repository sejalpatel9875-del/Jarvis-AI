package com.jarvis.ai.repository

import com.jarvis.ai.local.*
import com.jarvis.ai.remote.*
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow

class JarvisRepository(
    private val apiService: JarvisApiService,
    private val db: JarvisDatabase
) {
    suspend fun getChatHistory(): List<ChatMessageEntity> {
        return db.chatMessageDao().getAllMessages()
    }

    suspend fun sendChatMessage(userMessage: String): String {
        // Save user message to offline database first
        db.chatMessageDao().insertMessage(
            ChatMessageEntity(sender = "User", message = userMessage)
        )

        return try {
            val response = apiService.sendChatMessage(ChatRequest(message = userMessage))
            val botReply = response.body()?.response ?: "Response received from JARVIS Backend."
            
            // Save bot response to local database
            db.chatMessageDao().insertMessage(
                ChatMessageEntity(sender = "JARVIS", message = botReply)
            )
            botReply
        } catch (e: Exception) {
            val offlineFallback = "Offline mode: Message queued for sync."
            db.chatMessageDao().insertMessage(
                ChatMessageEntity(sender = "JARVIS", message = offlineFallback, isSynced = false)
            )
            offlineFallback
        }
    }

    suspend fun executeRemoteCommand(action: String, params: Map<String, Any> = emptyMap()): DesktopActionResponse? {
        return try {
            val res = apiService.executeDesktopAction(DesktopActionRequest(action, params))
            res.body()
        } catch (e: Exception) {
            null
        }
    }

    suspend fun getNotes(): List<OfflineNoteEntity> {
        return db.offlineNoteDao().getAllNotes()
    }

    suspend fun createNote(title: String, content: String) {
        db.offlineNoteDao().insertNote(
            OfflineNoteEntity(title = title, content = content)
        )
    }
}
