# schedule_manager.py
import json

class ScheduleManager:
    def __init__(self):
        self.days = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота"]
        self.times = [
            "07:45\n09:20", "09:30\n11:05", "11:15\n12:50",
            "13:10\n14:45", "14:55\n16:30", "16:40\n18:15"
        ]
        # При старті програми ініціалізуємо порожній глобальний пул предметів
        self.subjects_palette = set()
        self.clear_schedule()

    def clear_schedule(self):
        # Тепер цей метод очищає ТІЛЬКИ сітку розкладу. 
        # Пул предметів (self.subjects_palette) ми НЕ чіпаємо, щоб предмети переносились.
        self.schedule = {day: {i: None for i in range(len(self.times))} for day in self.days}

    def set_class(self, day: str, time_index: int, subject: str) -> bool:
        if day in self.schedule and 0 <= time_index < len(self.times):
            subject = subject.strip()
            self.schedule[day][time_index] = subject
            self.subjects_palette.add(subject)
            return True
        return False

    def remove_class(self, day: str, time_index: int) -> bool:
        if day in self.schedule and 0 <= time_index < len(self.times):
            self.schedule[day][time_index] = None
            return True
        return False

    def remove_from_palette(self, subject: str):
        if subject in self.subjects_palette:
            self.subjects_palette.remove(subject)

    def rename_subject(self, old_name: str, new_name: str):
        if old_name in self.subjects_palette:
            self.subjects_palette.remove(old_name)
            self.subjects_palette.add(new_name)
        
        for day, times in self.schedule.items():
            for idx, subj in times.items():
                if subj == old_name:
                    self.schedule[day][idx] = new_name

    def save_to_file(self, filename: str):
        # Зберігаємо поточну сітку розкладу та ВСІ накопичені на цей момент предмети
        data_to_save = {
            "schedule": self.schedule,
            "palette": list(self.subjects_palette)
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)

    def load_from_file(self, filename: str):
        with open(filename, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
            
        raw_schedule = loaded_data["schedule"]
        self.schedule = {day: {int(idx): subj for idx, subj in times.items()} for day, times in raw_schedule.items()}
        
        # Об'єднуємо предмети, які вже були в програмі, з тими, що завантажуються з файлу.
        # Завдяки структурі set() дублікатів не буде.
        if "palette" in loaded_data:
            self.subjects_palette.update(loaded_data["palette"])

    def get_schedule(self) -> dict:
        return self.schedule

    def search_by_subject(self, search_query: str) -> list:
        results = []
        query_lower = search_query.strip().lower()
        
        if not query_lower:
            return results

        for day, times_dict in self.schedule.items():
            for idx, subj in times_dict.items():
                if subj and query_lower in subj.lower():
                    results.append({
                        "day": day,
                        "time": self.times[idx],
                        "subject": subj
                    })
        return results