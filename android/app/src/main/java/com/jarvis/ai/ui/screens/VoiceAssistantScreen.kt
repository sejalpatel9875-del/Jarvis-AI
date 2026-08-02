package com.jarvis.ai.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun VoiceAssistantScreen() {
    var voiceState by remember { mutableStateOf("Idle (Press Orb to Speak)") }
    var textInput by remember { mutableStateOf("") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.SpaceBetween
    ) {
        Text("Voice Assistant Core", style = MaterialTheme.typography.titleLarge)

        Card(
            modifier = Modifier
                .size(200.dp)
                .padding(16.dp),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer)
        ) {
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center
            ) {
                Text(voiceState, style = MaterialTheme.typography.bodyMedium)
            }
        }

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Button(
                onClick = { voiceState = "Listening in Hindi/English..." },
                modifier = Modifier.weight(1f)
            ) {
                Text("Listen Voice")
            }

            Button(
                onClick = { voiceState = "Synthesizing Neural Speech..." },
                modifier = Modifier.weight(1f)
            ) {
                Text("Speak Neural")
            }
        }
    }
}
