package com.jarvis.ai.local

import androidx.room.*

@Entity(tableName = "chat_messages")
data class ChatMessageEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val sender: String,
    val message: String,
    val timestamp: Long = System.currentTimeMillis(),
    val isSynced: Boolean = true
)

@Entity(tableName = "offline_notes")
data class OfflineNoteEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val title: String,
    val content: String,
    val updatedAt: Long = System.currentTimeMillis(),
    val isSynced: Boolean = false
)

@Dao
interface ChatMessageDao {
    @Query("SELECT * FROM chat_messages ORDER BY timestamp ASC")
    suspend fun getAllMessages(): List<ChatMessageEntity>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertMessage(msg: ChatMessageEntity)
}

@Dao
interface OfflineNoteDao {
    @Query("SELECT * FROM offline_notes ORDER BY updatedAt DESC")
    suspend fun getAllNotes(): List<OfflineNoteEntity>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertNote(note: OfflineNoteEntity)
}

@Database(entities = [ChatMessageEntity::class, OfflineNoteEntity::class], version = 1)
abstract class JarvisDatabase : RoomDatabase() {
    abstract fun chatMessageDao(): ChatMessageDao
    abstract fun offlineNoteDao(): OfflineNoteDao
}
