package com.jarvis.ai.ui

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.navigation.compose.*
import com.jarvis.ai.theme.JarvisCompanionTheme
import com.jarvis.ai.ui.screens.*

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            JarvisCompanionTheme {
                MainScreen()
            }
        }
    }
}

@Composable
fun MainScreen() {
    val navController = rememberNavController()
    var selectedItem by remember { mutableIntStateOf(0) }
    val items = listOf("Home", "Voice", "Remote", "Chat", "Notes")

    Scaffold(
        bottomBar = {
            NavigationBar {
                items.forEachIndexed { index, item ->
                    NavigationBarItem(
                        selected = selectedItem == index,
                        onClick = {
                            selectedItem = index
                            when (index) {
                                0 -> navController.navigate("home")
                                1 -> navController.navigate("voice")
                                2 -> navController.navigate("remote")
                                3 -> navController.navigate("chat")
                                4 -> navController.navigate("notes")
                            }
                        },
                        label = { Text(item) },
                        icon = { Text(if (selectedItem == index) "●" else "○") }
                    )
                }
            }
        }
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = "home",
            modifier = Modifier.padding(innerPadding)
        ) {
            composable("home") { HomeScreen() }
            composable("voice") { VoiceAssistantScreen() }
            composable("remote") { RemoteCommandsScreen() }
            composable("chat") { ChatHistoryScreen() }
            composable("notes") { NotesMemoryScreen() }
        }
    }
}
