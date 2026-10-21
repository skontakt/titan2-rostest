#!/usr/bin/env python3
"""Adapt the public TypeQ25 sources for Titan 2 / Elite / Elite Pro."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"
ALLOWED = ("qwerty", "russian_translit", "russian_q25_rostest")

def edit(path, before, after):
    file = ROOT / path
    content = file.read_text(encoding="utf-8")
    if before not in content:
        raise RuntimeError(f"Expected source fragment absent in {path}: {before[:90]}")
    file.write_text(content.replace(before, after), encoding="utf-8")

def replace_between(path, begin, end, replacement):
    file = ROOT / path
    content = file.read_text(encoding="utf-8")
    a = content.index(begin)
    b = content.index(end, a)
    file.write_text(content[:a] + replacement + content[b:], encoding="utf-8")

# Independent Android package: does not overwrite the upstream installation.
gradle = "app/build.gradle.kts"
edit(gradle, 'applicationId = "it.srik.TypeQ25.russianphoto"', 'applicationId = "it.srik.titan2rostest"')
edit(gradle, 'versionCode = 5', 'versionCode = 1')
edit(gradle, 'versionName = "1.1"', 'versionName = "1.0.0"')

# Only English, Russian transliteration and the Russian Rostest photo layout.
layouts_dir = APP / "src/main/assets/common/layouts"
for layout_file in layouts_dir.glob("*.json"):
    if layout_file.stem not in ALLOWED:
        layout_file.unlink()

# The photo shows these Cyrillic letters against Latin hardware key positions.
# For paired keys, the UPPER printed Cyrillic character is entered first;
# the LOWER printed Cyrillic character is entered on the next tap.
photo = {
    "Q": "йц", "W": "у", "E": "к", "R": "её", "T": "н",
    "Y": "г", "U": "шщ", "I": "з", "O": "хъ", "P": "ю",
    "A": "фы", "S": "в", "D": "а", "F": "п", "G": "р",
    "H": "о", "J": "л", "K": "д", "L": "жэ",
    "Z": "яч", "X": "с", "C": "м", "V": "и",
    "B": "т", "N": "ь", "M": "б",
}
assert len(photo) == 26
assert len("".join(photo.values())) == 33
assert set("".join(photo.values())) == set("абвгдеёжзийклмнопрстуфхцчшщъыьэюя")
assert {k: v for k, v in photo.items() if len(v) == 2} == {
    "Q": "йц", "R": "её", "U": "шщ", "O": "хъ",
    "A": "фы", "L": "жэ", "Z": "яч",
}

def mapped(letter):
    base = {
        "lowercase": letter[0],
        "uppercase": letter[0].upper(),
    }
    if len(letter) > 1:
        base["multiTapEnabled"] = True
        base["taps"] = [
            {"lowercase": value, "uppercase": value.upper()}
            for value in letter
        ]
    return base

rostest = {
    "name": "Русский Ростест",
    "description": "Русская раскладка Ростест для Titan 2 / Elite / Pro.",
    "mappings": {"KEYCODE_" + key: mapped(value) for key, value in photo.items()},
}
(layouts_dir / "russian_q25_rostest.json").write_text(
    json.dumps(rostest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
)
translit_path = layouts_dir / "russian_translit.json"
translit = json.loads(translit_path.read_text(encoding="utf-8"))
translit["name"] = "Русский транслит"
translit["description"] = "Русская транслитерация для физической клавиатуры."
translit_path.write_text(json.dumps(translit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

# Restrict the layout selector to the 3 supported modes (QWERTY is displayed
# separately by KeyboardLayoutSettingsScreen).
layout_loader = "app/src/main/java/it/Q25/typeq25/data/layout/JsonLayoutLoader.kt"
replace_between(
    layout_loader,
    "    fun getAvailableLayouts(",
    "\n}",
    """    fun getAvailableLayouts(
        assets: AssetManager,
        context: Context? = null
    ): List<String> = listOf("russian_translit", "russian_q25_rostest")
""",
)

settings = "app/src/main/java/it/Q25/typeq25/SettingsManager.kt"
edit(settings,
     'private const val DEFAULT_KEYBOARD_LAYOUT = "qwerty"',
     'private const val DEFAULT_KEYBOARD_LAYOUT = "qwerty"\n    private val TITAN_LAYOUTS = listOf("qwerty", "russian_translit", "russian_q25_rostest")')
edit(settings,
     'return getPreferences(context).getString(KEY_KEYBOARD_LAYOUT, DEFAULT_KEYBOARD_LAYOUT) ?: DEFAULT_KEYBOARD_LAYOUT',
     'return getPreferences(context).getString(KEY_KEYBOARD_LAYOUT, DEFAULT_KEYBOARD_LAYOUT)?.takeIf { it in TITAN_LAYOUTS } ?: DEFAULT_KEYBOARD_LAYOUT')
edit(settings,
     '.putString(KEY_KEYBOARD_LAYOUT, layoutName)',
     '.putString(KEY_KEYBOARD_LAYOUT, layoutName.takeIf { it in TITAN_LAYOUTS } ?: DEFAULT_KEYBOARD_LAYOUT)')
edit(settings,
     'val jsonString = prefs.getString(KEY_KEYBOARD_LAYOUT_LIST, null) ?: return listOf(getKeyboardLayout(context))',
     'val jsonString = prefs.getString(KEY_KEYBOARD_LAYOUT_LIST, null) ?: return TITAN_LAYOUTS')
edit(settings,
     'if (!name.isNullOrEmpty()) {\n                    seen.add(name)',
     'if (!name.isNullOrEmpty() && name in TITAN_LAYOUTS) {\n                    seen.add(name)')
edit(settings,
     'val normalized = layouts.map { it.trim() }.filter { it.isNotBlank() }.distinct()',
     'val normalized = layouts.map { it.trim() }.filter { it in TITAN_LAYOUTS }.distinct()')

# Titan 2 family shares the same physical keycodes and numeric Alt mapping.
device = "app/src/main/java/it/Q25/typeq25/DeviceManager.kt"
edit(device, 'getString(KEY_DEVICE, "Q25") ?: "Q25"', 'getString(KEY_DEVICE, "titan2") ?: "titan2"')
edit(device,
     'fun setDevice(context: Context, device: String) {\n        cachedDevice = device',
     'fun setDevice(context: Context, device: String) {\n        require(device == "titan2") { "Поддерживается только Titan 2 / Elite / Elite Pro" }\n        cachedDevice = device')
for file in [
    "app/src/main/java/it/Q25/typeq25/MainActivity.kt",
    "app/src/main/java/it/Q25/typeq25/DeviceSettingsScreen.kt",
]:
    edit(file, 'listOf("Q25", "titan2")', 'listOf("titan2")')
edit(
    "app/src/main/java/it/Q25/typeq25/MainActivity.kt",
    'showDeviceSelectionDialog = true',
    'DeviceManager.setDevice(context, "titan2")'
)
# Above replacement only changes the first-run assignment (dialog no longer appears).
# Keep the device settings screen compatible with upstream settings structure.

service = "app/src/main/java/it/Q25/typeq25/inputmethod/PhysicalKeyboardInputMethodService.kt"
edit(service,
     'private var suppressNextLayoutReload: Boolean = false',
     'private var suppressNextLayoutReload: Boolean = false\n    private var consumeAltSpaceKeyUp: Boolean = false')
replace_between(
    service,
    '        // Handle Ctrl+Space layout switching even when Alt is active.',
    '        multiTapController.resetForNewKey(keyCode)',
    """        // Alt+Space changes the layout without inserting a space.
        if (
            hasEditableField &&
            keyCode == KeyEvent.KEYCODE_SPACE &&
            (event?.isAltPressed == true || altPressed || altLatchActive || altOneShot || altPhysicallyPressed) &&
            !(event?.isCtrlPressed == true || ctrlPressed || ctrlLatchActive || ctrlOneShot || ctrlPhysicallyPressed)
        ) {
            consumeAltSpaceKeyUp = true
            if ((event?.repeatCount ?: 0) == 0) {
                multiTapController.finalizeCycle()
                modifierStateController.clearAltState(resetPressedState = true)
                cycleLayoutFromShortcut()
                updateStatusBarText()
            }
            return true
        }

""",
)
edit(service,
     'override fun onKeyUp(keyCode: Int, event: KeyEvent?): Boolean {\n',
     'override fun onKeyUp(keyCode: Int, event: KeyEvent?): Boolean {\n        if (keyCode == KeyEvent.KEYCODE_SPACE && consumeAltSpaceKeyUp) {\n            consumeAltSpaceKeyUp = false\n            return true\n        }\n')

# The app header, launcher label and IME label are in Russian.
strings = "app/src/main/res/values/strings.xml"
for old, new in {
    '<string name="app_name">TypeQ25 Russian</string>':
        '<string name="app_name">Клавиатура для Titan 2 / Elite / Pro</string>',
    '<string name="input_method_name">TypeQ25 Russian Keyboard</string>':
        '<string name="input_method_name">Клавиатура для Titan 2 / Elite / Pro</string>',
    '<string name="keyboard_title">TypeQ25 Keyboard</string>':
        '<string name="keyboard_title">Клавиатура для Titan 2 / Elite / Pro</string>',
    '<string name="keyboard_brand_subtitle">Физическая клавиатура от BlackBerry Russia</string>':
        '<string name="keyboard_brand_subtitle">Английский • русский транслит • Ростест</string>',
    '<string name="keyboard_subtitle">Physical keyboard with long press support</string>':
        '<string name="keyboard_subtitle">Переключение: Alt + Пробел</string>',
}.items():
    edit(strings, old, new)

edit(
    "app/src/main/java/it/Q25/typeq25/ui/CustomTopBar.kt",
    'text = "TypeQ25",',
    'text = stringResource(R.string.keyboard_title),'
)

print("OK: Titan 2 / Elite / Elite Pro, 3 layouts, photo mapping, Alt+Space, Russian header")
