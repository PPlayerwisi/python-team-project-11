# schedule_manager.py
import json

class ScheduleManager:
    # Клас відповідає за внутрішню логіку розкладу, зберігання матриці занять 
    # та JSON серіалізацію
    def __init__(self):
        self.days = ["Понеділок", "Вівторок", "Середа", 
                     "Четвер", "П'ятниця", "Субота"]
        self.times = [
            "07:45\n09:20", "09:30\n11:05", "11:15\n12:50",
            "13:10\n14:45", "14:55\n16:30", "16:40\n18:15"
        ]
        self.subjects_palette = set()
        self.clear_schedule()

    def clear_schedule(self):
        # Очищення поточної сітки розкладу без видалення предметів з палітри
        self.schedule = {day: {i: None for i in range(len(self.times))} 
                         for day in self.days}

    def set_class(self, day: str, time_index: int, subject: str) -> bool:
        # Запис предмета у відповідний слот координатної сітки
        if day in self.schedule and 0 <= time_index < len(self.times):
            subject = subject.strip()
            self.schedule[day][time_index] = subject
            self.subjects_palette.add(subject)
            return True
        return False

    def remove_class(self, day: str, time_index: int) -> bool:
        # Видалення заняття з конкретної комірки розкладу
        if day in self.schedule and 0 <= time_index < len(self.times):
            self.schedule[day][time_index] = None
            return True
        return False

    def remove_from_palette(self, subject: str):
        # Видалення предмета з пулу доступних для перетягування елементів
        if subject in self.subjects_palette:
            self.subjects_palette.remove(subject)

    def rename_subject(self, old_name: str, new_name: str):
        # Каскадне перейменування предмета в палітрі та по всій сітці розкладу
        if old_name in self.subjects_palette:
            self.subjects_palette.remove(old_name)
            self.subjects_palette.add(new_name)
        
        for day, times in self.schedule.items():
            for idx, subj in times.items():
                if subj == old_name:
                    self.schedule[day][idx] = new_name

    def save_to_file(self, filename: str):
        # Експорт поточного стану розкладу та палітри у JSON файл
        data_to_save = {
            "schedule": self.schedule,
            "palette": list(self.subjects_palette)
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)

    def load_from_file(self, filename: str):
        # Імпорт даних із JSON файлу та мерж палітри предметів
        with open(filename, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
            
        raw_schedule = loaded_data["schedule"]
        self.schedule = {day: {int(idx): subj for idx, subj in times.items()} 
                         for day, times in raw_schedule.items()}
        
        if "palette" in loaded_data:
            self.subjects_palette.update(loaded_data["palette"])

    def get_schedule(self) -> dict:
        return self.schedule

    def search_by_subject(self, search_query: str) -> list:
        # Регістронезалежний пошук співпадінь по матриці розкладу
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