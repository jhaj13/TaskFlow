import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional

from models import Task
from task_service import TaskService


class TaskFlowApp(tk.Tk):
    def __init__(self, service: TaskService):
        super().__init__()
        self.service = service
        self.tasks_by_item = {}
        self.timer_seconds = 25 * 60
        self.timer_job = None
        self.timer_running = False

        self.title("TaskFlow")
        self.geometry("860x620")
        self.minsize(760, 540)
        self.configure(padx=20, pady=20)

        self.build_task_form()
        self.build_filter()
        self.build_task_table()
        self.build_task_buttons()
        self.build_timer()
        self.refresh_tasks()

    def build_task_form(self):
        frame = ttk.LabelFrame(self, text="Add a task", padding=12)
        frame.pack(fill="x", pady=(0, 12))

        ttk.Label(frame, text="Task").grid(row=0, column=0, sticky="w")
        self.name_entry = ttk.Entry(frame)
        self.name_entry.grid(row=1, column=0, sticky="ew", padx=(0, 10))

        ttk.Label(frame, text="Category").grid(row=0, column=1, sticky="w")
        self.category_entry = ttk.Entry(frame, width=22)
        self.category_entry.grid(row=1, column=1, sticky="ew", padx=(0, 10))

        ttk.Button(frame, text="Add Task", command=self.add_task).grid(row=1, column=2)
        frame.columnconfigure(0, weight=1)
        self.name_entry.bind("<Return>", lambda _event: self.add_task())

    def build_filter(self):
        frame = ttk.Frame(self)
        frame.pack(fill="x", pady=(0, 8))
        ttk.Label(frame, text="Filter by category:").pack(side="left")
        self.filter_var = tk.StringVar(value="All")
        self.filter_box = ttk.Combobox(
            frame, textvariable=self.filter_var, state="readonly", width=22
        )
        self.filter_box.pack(side="left", padx=8)
        self.filter_box.bind("<<ComboboxSelected>>", lambda _event: self.refresh_tasks())

    def build_task_table(self):
        columns = ("name", "category", "status", "minutes")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=13)
        self.tree.heading("name", text="Task")
        self.tree.heading("category", text="Category")
        self.tree.heading("status", text="Status")
        self.tree.heading("minutes", text="Focus Minutes")
        self.tree.column("name", width=330)
        self.tree.column("category", width=160)
        self.tree.column("status", width=110, anchor="center")
        self.tree.column("minutes", width=110, anchor="center")
        self.tree.pack(fill="both", expand=True)

    def build_task_buttons(self):
        frame = ttk.Frame(self)
        frame.pack(fill="x", pady=10)
        ttk.Button(frame, text="Complete / Reopen", command=self.toggle_task).pack(
            side="left", padx=(0, 8)
        )
        ttk.Button(frame, text="Edit", command=self.edit_task).pack(side="left", padx=8)
        ttk.Button(frame, text="Delete", command=self.delete_task).pack(side="left", padx=8)

    def build_timer(self):
        frame = ttk.LabelFrame(self, text="Pomodoro", padding=12)
        frame.pack(fill="x")

        self.timer_label = ttk.Label(frame, text="25:00", font=("Helvetica", 24, "bold"))
        self.timer_label.pack(side="left", padx=(0, 20))

        ttk.Button(frame, text="Start", command=self.start_timer).pack(side="left", padx=4)
        ttk.Button(frame, text="Pause", command=self.pause_timer).pack(side="left", padx=4)
        ttk.Button(frame, text="Reset", command=self.reset_timer).pack(side="left", padx=4)
        ttk.Label(frame, text="Select a task before starting to log focus time.").pack(
            side="right"
        )

    def selected_task(self) -> Optional[Task]:        
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Select a task", "Please select a task first.")
            return None
        return self.tasks_by_item[selected[0]]

    def add_task(self):
        try:
            self.service.add_task(self.name_entry.get(), self.category_entry.get())
        except ValueError as error:
            messagebox.showerror("Cannot add task", str(error))
            return

        self.name_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)
        self.refresh_tasks()
        self.name_entry.focus()

    def refresh_tasks(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.tasks_by_item.clear()

        for task in self.service.get_tasks(self.filter_var.get()):
            status = "Completed" if task.completed else "Open"
            item = self.tree.insert(
                "", "end", values=(task.name, task.category, status, task.minutes)
            )
            self.tasks_by_item[item] = task

        categories = ["All"] + self.service.get_categories()
        self.filter_box["values"] = categories
        if self.filter_var.get() not in categories:
            self.filter_var.set("All")

    def toggle_task(self):
        task = self.selected_task()
        if task:
            self.service.toggle_complete(task)
            self.refresh_tasks()

    def edit_task(self):
        task = self.selected_task()
        if not task:
            return

        window = tk.Toplevel(self)
        window.title("Edit Task")
        window.resizable(False, False)
        window.transient(self)
        window.grab_set()

        ttk.Label(window, text="Task name").grid(row=0, column=0, padx=12, pady=(12, 4), sticky="w")
        name_entry = ttk.Entry(window, width=42)
        name_entry.insert(0, task.name)
        name_entry.grid(row=1, column=0, padx=12, sticky="ew")

        ttk.Label(window, text="Category").grid(row=2, column=0, padx=12, pady=(12, 4), sticky="w")
        category_entry = ttk.Entry(window, width=42)
        category_entry.insert(0, task.category)
        category_entry.grid(row=3, column=0, padx=12, sticky="ew")

        def save_changes():
            try:
                self.service.update_task(task, name_entry.get(), category_entry.get())
            except ValueError as error:
                messagebox.showerror("Cannot update task", str(error), parent=window)
                return
            window.destroy()
            self.refresh_tasks()

        ttk.Button(window, text="Save", command=save_changes).grid(
            row=4, column=0, padx=12, pady=12, sticky="e"
        )
        name_entry.focus()

    def delete_task(self):
        task = self.selected_task()
        if task and messagebox.askyesno("Delete task", f'Delete "{task.name}"?'):
            self.service.delete_task(task)
            self.refresh_tasks()

    def start_timer(self):
        if not self.tree.selection():
            messagebox.showinfo("Select a task", "Select the task you are focusing on.")
            return
        if not self.timer_running:
            self.timer_running = True
            self.tick_timer()

    def tick_timer(self):
        if not self.timer_running:
            return

        if self.timer_seconds <= 0:
            self.timer_running = False
            self.timer_job = None
            task = self.selected_task()
            if task:
                self.service.add_minutes(task, 25)
            self.bell()
            messagebox.showinfo("Pomodoro complete", "Great work! You completed 25 focused minutes.")
            self.reset_timer()
            self.refresh_tasks()
            return

        self.timer_seconds -= 1
        self.update_timer_label()
        self.timer_job = self.after(1000, self.tick_timer)

    def pause_timer(self):
        self.timer_running = False
        if self.timer_job:
            self.after_cancel(self.timer_job)
            self.timer_job = None

    def reset_timer(self):
        self.pause_timer()
        self.timer_seconds = 25 * 60
        self.update_timer_label()

    def update_timer_label(self):
        minutes, seconds = divmod(self.timer_seconds, 60)
        self.timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
