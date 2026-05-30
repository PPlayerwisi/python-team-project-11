# schedule_manager.py

class ScheduleManager:
    def __init__(self):
        # Словник, в якому ключі це дні тижня, а значення — список занять

        self.schedule = {
            "Понеділок": [],
            "Вівторок": [],
            "Середа": [],
            "Четвер": [],
            "П'ятниця": [],
            "Субота": [],
            "Неділя": []
        }

    def add_class(self, day: str, subject: str, time: str) -> bool:
        
        # Функція для додавання занять у відповідний день тижня
        # Повертає True, якщо додано успішно, і False, якщо у нас нема такого дня
        
        if day in self.schedule:
            self.schedule[day].append({
                "subject": subject,
                "time": time
            })
            # Автоматично сортуємо заняття за часом
            self.schedule[day] = sorted(self.schedule[day], key=lambda x: x["time"])
            return True
        return False

    def get_schedule(self) -> dict:
        # Ця функція повертає весь розклад для того, аби користувач їх бачив
        return self.schedule

    def search_by_subject(self, search_query: str) -> list:
        
        # Функція шукає заняття за назвою предмета і не залежить від регістру.
        # Повертає список знайдених занять із зазначенням дня та часу.
        
        results = []
        query_lower = search_query.strip().lower()
        
        if not query_lower:
            return results

        for day, classes in self.schedule.items():
            for item in classes:
                if query_lower in item["subject"].lower():
                    results.append({
                        "day": day,
                        "time": item["time"],
                        "subject": item["subject"]
                    })
        return results