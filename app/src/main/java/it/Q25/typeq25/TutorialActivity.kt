package it.srik.TypeQ25

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp

class TutorialActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                TutorialScreen {
                    SettingsManager.setTutorialCompleted(this, true)
                    finish()
                }
            }
        }
    }
}

private data class TitanLesson(
    val heading: String,
    val description: String,
    val details: List<Pair<String, String>>
)

private val lessons = listOf(
    TitanLesson(
        "Установка и включение",
        "Клавиатура для Titan 2 / Elite / Pro",
        listOf(
            "Совместимость" to "Titan 2, Titan 2 Elite и Titan 2 Elite Pro.",
            "Включение" to "Откройте настройки Android → Языки и ввод → Экранная клавиатура → Управление клавиатурами. Включите нашу клавиатуру.",
            "Выбор" to "Выберите «Клавиатура для Titan 2 / Elite / Pro» как текущий метод ввода.",
            "Проверка" to "Откройте поле для набора текста и попробуйте физические клавиши."
        )
    ),
    TitanLesson(
        "Три раскладки",
        "Только английский, русский транслит и русский Ростест",
        listOf(
            "Английский" to "Обычная английская QWERTY-клавиатура.",
            "Русский транслит" to "Русские буквы расположены близко к их латинским соответствиям.",
            "Русский Ростест" to "33 русские буквы на 26 физических клавишах. На клавишах с двумя русскими буквами первой вводится верхняя буква.",
            "Переключение" to "Нажмите Alt + Пробел. Каждое нажатие переключает на следующую из трёх раскладок."
        )
    ),
    TitanLesson(
        "Русский Ростест",
        "Сначала верхняя русская буква, затем нижняя",
        listOf(
            "Пример Q" to "Первое нажатие — Й, следующее быстрое нажатие — Ц.",
            "Другие пары" to "R — Е/Ё, U — Ш/Щ, O — Х/Ъ, A — Ф/Ы, L — Ж/Э, Z — Я/Ч.",
            "Остальные буквы" to "Клавиши с одной русской буквой вводят её обычным нажатием.",
            "Заглавные буквы" to "Используйте Shift, как на стандартной физической клавиатуре."
        )
    ),
    TitanLesson(
        "Подсказки и нижняя панель",
        "Дополнительные возможности ввода",
        listOf(
            "Подсказки" to "При наборе слова на нижней панели показываются варианты продолжения. Нажмите на вариант, чтобы вставить его.",
            "Нижняя панель" to "Кнопка меню открывает действия редактирования. Доступны также символы и голосовой ввод.",
            "SYM" to "Клавиша sym открывает экран символов и эмодзи. Элементы можно выбирать касанием.",
            "Чувствительные поля" to "В паролях и других защищённых полях подсказки не показываются."
        )
    ),
    TitanLesson(
        "Специальные клавиши и настройки",
        "Краткая памятка",
        listOf(
            "Alt" to "Alt + буквенная клавиша вводит дополнительный символ, если он назначен. Alt + Пробел меняет раскладку.",
            "Shift" to "Используйте для прописных букв. Backspace удаляет символ.",
            "Настройки" to "Можно изменять длительность удержания, параметры текста, автозамену, символы и поведение аппаратной клавиатуры.",
            "Готово" to "Вы можете открыть это обучение снова в настройках приложения."
        )
    )
)

@Composable
fun TutorialScreen(onComplete: () -> Unit) {
    var page by remember { mutableIntStateOf(0) }
    val lesson = lessons[page]
    Scaffold(
        bottomBar = {
            Row(
                modifier = Modifier.fillMaxWidth().padding(16.dp),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                OutlinedButton(onClick = { if (page > 0) page-- else onComplete() }) {
                    Text(if (page == 0) "Закрыть" else "Назад")
                }
                Button(onClick = { if (page < lessons.lastIndex) page++ else onComplete() }) {
                    Text(if (page == lessons.lastIndex) "Готово" else "Далее")
                }
            }
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier.fillMaxSize().padding(paddingValues)
                .verticalScroll(rememberScrollState()).padding(20.dp)
        ) {
            Text("Обучение • " + (page + 1) + " из " + lessons.size, style = MaterialTheme.typography.labelLarge)
            Spacer(modifier = Modifier.height(16.dp))
            Text(lesson.heading, style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
            Spacer(modifier = Modifier.height(8.dp))
            Text(lesson.description, style = MaterialTheme.typography.bodyLarge)
            Spacer(modifier = Modifier.height(20.dp))
            lesson.details.forEach { (title, explanation) ->
                Text(title, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
                Spacer(modifier = Modifier.height(4.dp))
                Text(explanation, style = MaterialTheme.typography.bodyMedium)
                Spacer(modifier = Modifier.height(16.dp))
            }
        }
    }
}
