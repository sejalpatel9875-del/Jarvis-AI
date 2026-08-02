package com.jarvis.ai.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun RemoteCommandsScreen() {
    var statusMessage by remember { mutableStateOf("Ready to send remote desktop actions.") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Text("Remote Desktop Productivity Controls", style = MaterialTheme.typography.titleLarge)
        Text(statusMessage, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.secondary)

        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(
                onClick = { statusMessage = "Command sent: Launch VS Code" },
                modifier = Modifier.weight(1f)
            ) {
                Text("Launch VS Code")
            }
            Button(
                onClick = { statusMessage = "Command sent: Open Terminal" },
                modifier = Modifier.weight(1f)
            ) {
                Text("Open Terminal")
            }
        }

        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(
                onClick = { statusMessage = "Command sent: Take Screenshot" },
                modifier = Modifier.weight(1f)
            ) {
                Text("Take Screenshot")
            }
            Button(
                onClick = { statusMessage = "Command sent: Increase Volume" },
                modifier = Modifier.weight(1f)
            ) {
                Text("Volume Up")
            }
        }

        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(
                onClick = { statusMessage = "Command sent: Open Browser" },
                modifier = Modifier.weight(1f)
            ) {
                Text("Open Browser")
            }
            Button(
                onClick = { statusMessage = "Command sent: Clipboard Sync" },
                modifier = Modifier.weight(1f)
            ) {
                Text("Sync Clipboard")
            }
        }
    }
}
