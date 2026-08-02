package com.jarvis.ai.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun NotesMemoryScreen() {
    var noteTitle by remember { mutableStateOf("") }
    var noteContent by remember { mutableStateOf("") }
    var savedNotes by remember { mutableStateOf(listOf("Q3 AI Expansion Strategy", "Prayagraj Hindi Voice Preferences")) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Text("Notes & Long-Term Memory Sync", style = MaterialTheme.typography.titleLarge)

        OutlinedTextField(
            value = noteTitle,
            onValueChange = { noteTitle = it },
            label = { Text("Note Title") },
            modifier = Modifier.fillMaxWidth()
        )

        OutlinedTextField(
            value = noteContent,
            onValueChange = { noteContent = it },
            label = { Text("Content") },
            modifier = Modifier.fillMaxWidth()
        )

        Button(
            onClick = {
                if (noteTitle.isNotBlank()) {
                    savedNotes = savedNotes + noteTitle
                    noteTitle = ""
                    noteContent = ""
                }
            },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Save & Sync to Memory Agent")
        }

        Divider()

        Text("Synchronized Notes & Vector Facts", style = MaterialTheme.typography.titleMedium)
        savedNotes.forEach { note ->
            Card(modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(12.dp)) {
                    Text(note, style = MaterialTheme.typography.bodyMedium)
                }
            }
        }
    }
}
