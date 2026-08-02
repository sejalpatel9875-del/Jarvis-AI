package com.jarvis.ai.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun HomeScreen() {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Text(
            text = "JARVIS AI OS",
            style = MaterialTheme.typography.headlineLarge,
            color = MaterialTheme.colorScheme.primary
        )

        Card(
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("System Telemetry: ONLINE", style = MaterialTheme.typography.titleMedium)
                Text("Multi-Agent AI Network: 8 Specialized Agents Active")
                Text("Backend Endpoint: Railway Cloud Container")
            }
        }

        Card(
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Offline Synchronization Status", style = MaterialTheme.typography.titleMedium)
                Text("Room Database Cache: Synchronized")
                Text("Background Sync Engine: Ready")
            }
        }
    }
}
