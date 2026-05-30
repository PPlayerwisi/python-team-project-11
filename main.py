# main.py
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QComboBox, QPushButton,
                             QTextEdit, QMessageBox)

# Логіка від Студента Б
from schedule_manager import ScheduleManager

class LearningPlanner(QWidget):
    def __init__(self):
        super().__init__()
        self.manager = ScheduleManager()
        self.init_ui()

    def init_ui(self):
        # Вікно
        self.setWindowTitle('Планувальник навчального тижня')
        self.resize(550, 500)
        
        # Головний вертикальний шар
        main_layout = QVBoxLayout()

        # Форма для додавання нових занять
        main_layout.addWidget(QLabel("<b>Додати нове заняття:</b>"))
        input_layout = QHBoxLayout()
        
        self.day_select = QComboBox()
        self.day_select.addItems(["Понеділок", "Вівторок", "Середа", 
                                  "Четвер", "П'ятниця", "Субота", "Неділя"])
        
        self.subject_edit = QLineEdit()
        self.subject_edit.setPlaceholderText("Назва предмета (напр., Математика)")
        
        self.time_edit = QLineEdit()
        self.time_edit.setPlaceholderText("Час (напр., 08:30)")

        self.add_btn = QPushButton("Додати")
        # Додавання при кліку
        self.add_btn.clicked.connect(self.add_class_handler)

        input_layout.addWidget(self.day_select)
        input_layout.addWidget(self.subject_edit)
        input_layout.addWidget(self.time_edit)
        input_layout.addWidget(self.add_btn)
        main_layout.addLayout(input_layout)

        # Панель пошуку занять
        main_layout.addWidget(QLabel("<b>Пошук предмета:</b>"))
        search_layout = QHBoxLayout()
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Введіть назву для пошуку...")
        
        self.search_btn = QPushButton("Знайти")
        self.search_btn.clicked.connect(self.search_class_handler)

        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(self.search_btn)
        main_layout.addLayout(search_layout)

        # Кнопка скидання пошуку та виведення всього розкладу
        self.refresh_btn = QPushButton("Показати весь розклад")
        self.refresh_btn.clicked.connect(self.show_full_schedule)
        main_layout.addWidget(self.refresh_btn)

        # Головне вікно виводу інформації
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        main_layout.addWidget(self.text_area)

        self.setLayout(main_layout)
        self.show_full_schedule()

    def add_class_handler(self):
        day = self.day_select.currentText()
        subject = self.subject_edit.text().strip()
        time = self.time_edit.text().strip()

        if not subject or not time:
            QMessageBox.warning(self, "Помилка вводу", "Заповніть назву предмета та час!")
            return

        # Виклик функції Студента Б
        self.manager.add_class(day, subject, time)
        
        # Очищаємо поля після успішного додавання
        self.subject_edit.clear()
        self.time_edit.clear()
        
        QMessageBox.information(self, "Успіх", f"Предмет {subject} додано на {day}.")
        self.show_full_schedule()

    def show_full_schedule(self):
        # Функція виводить порожній розклад при старті програми
        # Вона бере словник розкладу у менеджера
        schedule = self.manager.get_schedule()
        html_text = "<h3>Ваш розклад на тиждень:</h3>"
        
        has_classes = False
        for day, classes in schedule.items():
            if classes:
                has_classes = True
                html_text += f"<br><b>{day}</b>:<br>"
                for item in classes:
                    html_text += f"  • <i>{item['time']}</i> — {item['subject']}<br>"
        
        if not has_classes:
            html_text += "<p>Розклад поки що порожній. Додайте перше заняття вище!</p>"
            
        self.text_area.setHtml(html_text)

    def search_class_handler(self):
        # Функція пошуку занять 
        query = self.search_edit.text().strip()
        if not query:
            self.show_full_schedule()
            return

        # Виклик логіки пошуку Студента Б
        results = self.manager.search_by_subject(query)
        html_text = f"<h3>Результати пошуку за запитом '{query}':</h3><br>"
        
        if not results:
            html_text += "Нічого не знайдено за такою назвою."
        else:
            for item in results:
                html_text += f"• <b>{item['day']}</b> ({item['time']}) — {item['subject']}<br>"
                
        self.text_area.setHtml(html_text)

app = QApplication(sys.argv)
window = LearningPlanner()
window.show()
sys.exit(app.exec_())