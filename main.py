import time
import json
import os

class Taskmaster:
    FILE_NAME = "task.json"
    EXPORT_FILE_NAME = "task.md"

    def __init__(self):
        self._tasks = []

        if os.path.exists(self.FILE_NAME):
            with open(f"{self.FILE_NAME}", "r") as file:
                contents = json.load(file)

                if contents["tasks"]:
                    self._tasks = contents["tasks"]

        self._current_task_index = -1
        self._current_activity_index = -1
        self._is_done = False

    @property
    def is_done(self):
        return self._is_done

    @property
    def current_task(self):
        return self._tasks[self._current_task_index]

    @property
    def current_activity(self):
        return self.current_task["activities"][self._current_activity_index]

    def print_task_list(self):
        for i, task in enumerate(self._tasks):
            print(f"[{i}] {task["summary"]}")
        print("[+] Create New Task / [=] Export / [x] Exit")

    def print_task(self):
        print(f"Current Task: {self.current_task["summary"]}")

    def print_activity(self):
        activity = self.current_activity
        timestamp = activity["start_time"]
        current_time = time.localtime(timestamp)
        formatted_time = time.strftime("%Y-%m-%d %I:%M %p", current_time)
        print(f"Current Activity: {activity["summary"]}")
        print(f"Started at {formatted_time}")

    def start_task(self, index):
        self._current_task_index = index
        self._current_activity_index = -1

    def stop_task(self):
        self._current_task_index = -1
        self._current_activity_index = -1

    def create_task(self):
        summary = input("Task summary: ")
        self._tasks.append({ "summary": summary, "activities": [] })
        self.save()

    def start_activity(self):
        summary = input("Activity summary: ")
        task = self.current_task
        task["activities"].append({ "summary": summary, "start_time": time.time() })
        self._current_activity_index = len(task["activities"]) - 1
        self.save()

    def stop_activity(self):
        self.current_activity["end_time"] = time.time()
        self._current_activity_index = -1
        self.save()

    def save(self):
        dictionary = {
            "tasks": self._tasks
        }

        with open(f"{self.FILE_NAME}", "w") as file:
            file.write(json.dumps(dictionary))

    @staticmethod
    def format_duration(duration):
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)

        hours = round(hours)
        minutes = round(minutes)

        if seconds > 30:
            minutes += 1

        if hours == 0 and minutes == 0:
            return f"{round(seconds)} s"

        time_iterable = []

        if hours > 1:
            time_iterable.append(f"{hours} hrs")
        elif hours == 1:
            time_iterable.append(f"{hours} hr")

        if minutes > 0:
            time_iterable.append(f"{minutes} min")

        return " ".join(time_iterable)

    @staticmethod
    def calculate_duration(activity):
        return activity["end_time"] - activity["start_time"]

    def export_activity(self, activity, duration, lines):
        lines.append(f"- {activity["summary"]} ({self.format_duration(duration)})")

    def export_task(self, task, lines):
        durations = list(map(self.calculate_duration, task["activities"]))
        total_duration = sum(durations)
        lines.append(f"# {task["summary"]}")
        lines.append(f"Total duration: {self.format_duration(total_duration)}")

        for i, activity in enumerate(task["activities"]):
            self.export_activity(activity,durations[i], lines)

    def export(self):
        lines = []
        with open(f"{self.EXPORT_FILE_NAME}", "w") as file:
            for task in self._tasks:
                self.export_task(task, lines)
            file.write("\n".join(lines))
        print("Export Complete!")

    def handle_main_loop(self):
        self.print_task_list()

        entered_value = input("Select Option: ")

        if entered_value == "exit":
            self._is_done = True
            return

        if entered_value == '+':
            self.create_task()
            self.start_task(len(self._tasks) - 1)
            return

        if entered_value.lower() == 'x':
            self._is_done = True
            return

        if entered_value == '=':
            self.export()
            return

        if not entered_value.isdigit():
            print("Not an option")
            return

        index = int(entered_value)

        if index < 0 or index >= len(self._tasks):
            print("Not a task")
            return

        self.start_task(index)

    def handle_task_loop(self):
        self.print_task()

        if self._current_activity_index == -1:
            print(f"[+] Start Activity / [x] Stop Task")
            entered_value = input("Select Option: ")

            if entered_value == '+':
                self.start_activity()
                return

            if entered_value.lower() == 'x':
                self.stop_task()
                return
        else:
            self.print_activity()
            input("Enter anything to stop activity: ")
            self.stop_activity()

    def run(self):
        print("=========================")
        if self._current_task_index == -1:
            self.handle_main_loop()
        else:
            self.handle_task_loop()


def main_loop():
    taskmaster = Taskmaster()
    while True:
        taskmaster.run()
        if taskmaster.is_done:
            return


main_loop()