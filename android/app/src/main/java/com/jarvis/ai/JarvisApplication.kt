package com.jarvis.ai

import android.app.Application
import androidx.room.Room
import com.jarvis.ai.local.JarvisDatabase
import com.jarvis.ai.remote.JarvisApiService
import com.jarvis.ai.repository.JarvisRepository
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

class JarvisApplication : Application() {
    lateinit var repository: JarvisRepository
        private set

    override fun onCreate() {
        super.onCreate()

        // 1. Initialize Room Database
        val database = Room.databaseBuilder(
            applicationContext,
            JarvisDatabase::class.java,
            "jarvis_offline_db"
        ).fallbackToDestructiveMigration().build()

        // 2. Initialize Retrofit Client pointing to Railway production server
        val retrofit = Retrofit.Builder()
            .baseUrl("https://jarvis-ai-production-eb13.up.railway.app/")
            .addConverterFactory(GsonConverterFactory.create())
            .build()

        val apiService = retrofit.create(JarvisApiService::class.java)

        // 3. Initialize Repository
        repository = JarvisRepository(apiService, database)
    }
}
