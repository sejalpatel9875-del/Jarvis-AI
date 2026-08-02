package com.jarvis.ai.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

data class LocalChatMessage(val sender: String, val text: String)

@Composable
fun ChatHistoryScreen() {
    var messages by remember {
        mutableStateOf(
            listOf(
                LocalChatMessage("JARVIS", "Namaste! Welcome to JARVIS AI OS Companion App."),
                LocalChatMessage("User", "Check my active workflow tasks.")
            )
        )
    }
    var inputText by remember { mutableStateOf("") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.SpaceBetween
    ) {
        Text("Synchronized Chat History", style = MaterialTheme.typography.titleLarge)

        LazyColumn(
            modifier = Modifier
                .weight(1f)
                .padding(vertical = 8.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            items(messages) { msg ->
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(
                        containerColor = if (msg.sender == "User") MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surfaceVariant
                    )
                ) {
                    Column(modifier = Modifier.padding(12.dp)) {
                        Text(msg.sender, style = MaterialTheme.typography.labelMedium)
                        Text(msg.text, style = MaterialTheme.typography.bodyMedium)
                    }
                }
            }
        }

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            OutlinedTextField(
                value = inputText,
                onValueChange = { inputText = it },
                modifier = Modifier.weight(1f),
                placeholder = { Text("Ask JARVIS...") }
            )
            Button(
                onClick = {
                    if (inputText.isNotBlank()) {
                        messages = messages + LocalChatMessage("User", inputText)
                        messages = messages + LocalChatMessage("JARVIS", "Processing: '$inputText' via Multi-Agent AI OS...")
                        inputText = ""
                    }
                }
            ) {
                Text("Send")
            }
        }
    }
}
