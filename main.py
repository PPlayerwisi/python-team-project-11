# main.py
import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QGridLayout, QLabel, QLineEdit, QPushButton, 
                             QInputDialog, QFrame, QMenu, QComboBox, QMessageBox)
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag

# Імпортуємо логіку Студента Б
from schedule_manager import ScheduleManager

class DraggableSubject(QLabel):
    def __init__(self, subject_name, manager, update_callback):
        super().__init__(subject_name)
        self.subject_name = subject_name
        self.manager = manager
        self.update_callback = update_callback
        self.setStyleSheet("""
            background-color: lightblue; 
            border: 1px solid gray; 
            border-radius: 5px;
            padding: 5px;
        """)
        self.setAlignment(Qt.AlignCenter)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            mime.setText(self.text())
            drag.setMimeData(mime)
            drag.exec_(Qt.CopyAction)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        edit_action = menu.addAction("Редагувати")
        delete_action = menu.addAction("Видалити")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        
        if action == edit_action:
            new_name, ok = QInputDialog.getText(self, "Редагування", "Нова назва:", text=self.subject_name)
            if ok and new_name.strip() and new_name != self.subject_name:
                self.manager.rename_subject(self.subject_name, new_name.strip())
                self.update_callback()
        elif action == delete_action:
            self.manager.remove_from_palette(self.subject_name)
            self.update_callback()

class ScheduleSlot(QLabel):
    def __init__(self, day, time_idx, manager, update_callback):
        super().__init__("")
        self.day = day
        self.time_idx = time_idx
        self.manager = manager
        self.update_callback = update_callback
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignCenter)
        self.setWordWrap(True)
        self.reset_style()

    def reset_style(self):
        self.setStyleSheet("background-color: white; border: 1px dashed #ccc;")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self.text():
            text, ok = QInputDialog.getText(self, 'Новий предмет', 'Введіть назву предмета:')
            if ok and text:
                self.manager.set_class(self.day, self.time_idx, text)
                self.update_callback()
        elif event.button() == Qt.RightButton and self.text():
            self.manager.remove_class(self.day, self.time_idx)
            self.update_callback()

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        subject = event.mimeData().text()
        self.manager.set_class(self.day, self.time_idx, subject)
        self.update_callback()

class LearningPlanner(QWidget):
    def __init__(self):
        super().__init__()
        self.manager = ScheduleManager()
        self.slots_ui = []
        self.current_active_file = "Тиждень_1.json" # Дефолтний файл при старті
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Планувальник v3.0 (Менеджер файлів)')
        self.resize(1000, 650)
        
        main_layout = QVBoxLayout()

        # --- НОВА ПАНЕЛЬ ДЛЯ РОБОТИ З ФАЙЛАМИ ЗБЕРЕЖЕННЯ ---
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("<b>Оберіть розклад (тиждень):</b>"))
        
        self.file_combo = QComboBox()
        self.file_combo.currentTextChanged.connect(self.switch_file_handler)
        file_layout.addWidget(self.file_combo)

        self.save_btn = QPushButton("Зберегти зміни")
        self.save_btn.clicked.connect(self.save_current_file_handler)
        file_layout.addWidget(self.save_btn)

        self.new_week_btn = QPushButton("Створити новий тиждень")
        self.new_week_btn.clicked.connect(self.create_new_file_handler)
        file_layout.addWidget(self.new_week_btn)
        
        main_layout.addLayout(file_layout)
        # --------------------------------------------------

        # Панель пошуку
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("<b>Пошук:</b>"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Введіть назву предмета...")
        self.search_edit.textChanged.connect(self.refresh_ui)
        search_layout.addWidget(self.search_edit)
        main_layout.addLayout(search_layout)

        # Сітка розкладу
        self.grid = QGridLayout()
        self.grid.setSpacing(5)
        
        for col, day in enumerate(self.manager.days):
            header = QLabel(f"<b>{day}</b>")
            header.setAlignment(Qt.AlignCenter)
            self.grid.addWidget(header, 0, col + 1)

        for row, time_str in enumerate(self.manager.times):
            time_label = QLabel(f"<b>{time_str}</b>")
            time_label.setAlignment(Qt.AlignCenter)
            self.grid.addWidget(time_label, row + 1, 0)

            for col, day in enumerate(self.manager.days):
                slot = ScheduleSlot(day, row, self.manager, self.refresh_ui)
                self.grid.addWidget(slot, row + 1, col + 1)
                self.slots_ui.append(slot)

        main_layout.addLayout(self.grid)

        main_layout.addWidget(QLabel("<br><b>Конструктор предметів:</b>"))
        
        self.palette_frame = QFrame()
        self.palette_frame.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ddd;")
        self.palette_layout = QHBoxLayout()
        self.palette_layout.setAlignment(Qt.AlignLeft)
        self.palette_frame.setLayout(self.palette_layout)
        
        main_layout.addWidget(self.palette_frame)
        self.setLayout(main_layout)

        # Скануємо папку на наявність збережень та завантажуємо актуальний файл
        self.scan_saved_files()

    def scan_saved_files(self):
        # Функція шукає усі .json файли у папці проєкту для випадаючого списку
        # Тимчасово блокуємо сигнали комбобокса, щоб уникнути спам-викликів при оновленні списку
        self.file_combo.blockSignals(True)
        self.file_combo.clear()
        
        files = [f for f in os.listdir('.') if f.endswith('.json')]
        
        # Якщо збережень взагалі немає, створюємо перше автоматично
        if not files:
            self.manager.clear_schedule()
            self.manager.save_to_file("Тиждень_1.json")
            files = ["Тиждень_1.json"]
            
        self.file_combo.addItems(files)
        
        # Виставляємо у списку той файл, який є поточним активним
        if self.current_active_file in files:
            self.file_combo.setCurrentText(self.current_active_file)
        else:
            self.current_active_file = files[0]
            self.file_combo.setCurrentText(files[0])
            
        self.file_combo.blockSignals(False)
        
        # Викликаємо логіку завантаження даних файлу Студента Б
        self.manager.load_from_file(self.current_active_file)
        self.refresh_ui()

    def switch_file_handler(self, selected_file):
        # Обробник події зміни файлу у комбобоксі
        if selected_file:
            self.current_active_file = selected_file
            self.manager.load_from_file(selected_file)
            self.refresh_ui()

    def save_current_file_handler(self):
        # Обробник для кнопки збереження поточного стану таблиці
        self.manager.save_to_file(self.current_active_file)
        QMessageBox.information(self, "Збережено", f"Зміни у файлі {self.current_active_file} успішно збережено!")

    def create_new_file_handler(self):
        # Створення нового файлу (наприклад, Тиждень_3)
        name, ok = QInputDialog.getText(self, "Новий розклад", "Введіть назву для нового тижня:")
        if ok and name.strip():
            filename = name.strip().replace(" ", "_") + ".json"
            
            if os.path.exists(filename):
                QMessageBox.warning(self, "Помилка", "Файл з такою назвою вже існує!")
                return
                
            # Очищаємо матрицю через логіку Студента Б та створюємо новий порожній файл
            self.current_active_file = filename
            self.manager.clear_schedule()
            self.manager.save_to_file(filename)
            
            # Оновлюємо список файлів на екрані
            self.scan_saved_files()

    def refresh_ui(self):
        search_query = self.search_edit.text().strip().lower()

        for slot in self.slots_ui:
            subject = self.manager.schedule[slot.day][slot.time_idx]
            if subject:
                slot.setText(subject)
                if not search_query:
                    slot.setStyleSheet("background-color: #ffeb3b; border: 1px solid gray;")
                elif search_query in subject.lower():
                    slot.setStyleSheet("background-color: #4caf50; color: white; border: 1px solid gray;")
                else:
                    slot.setStyleSheet("background-color: #9e9e9e; color: white; border: 1px solid gray;")
            else:
                slot.setText("")
                slot.reset_style()

        for i in reversed(range(self.palette_layout.count())): 
            self.palette_layout.itemAt(i).widget().setParent(None)
            
        for subject in self.manager.subjects_palette:
            draggable = DraggableSubject(subject, self.manager, self.refresh_ui)
            self.palette_layout.addWidget(draggable)

app = QApplication(sys.argv)
window = LearningPlanner()
window.show()
sys.exit(app.exec_())