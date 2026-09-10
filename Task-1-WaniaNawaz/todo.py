
import json
from pathlib import Path

# File path used for data persistence across runs
DATA_FILE = Path("tasks.json")


def add_task(tasks: list[dict], task_text: str) -> dict:
    """
    Appends a new task record to the in-memory tasks list.

    DATA ARCHITECTURE: List of Dictionaries
    ---------------------------------------
    Think of `tasks` as an in-memory SQL database table.
    - Each dictionary in the list represents a single 'row' or 'record'.
    - Each key ('id', 'task', 'completed') is a 'column'.
    - 'id' serves as our PRIMARY KEY, guaranteeing a unique identifier
      even if multiple tasks share identical descriptions.
    """
    # Auto-incrementing primary key: find max id present, or start at 1
    next_id = max((t["id"] for t in tasks), default=0) + 1

    new_task = {
        "id": next_id,
        "task": task_text,
        "completed": False,
    }
    tasks.append(new_task)
    return new_task


def view_tasks(tasks: list[dict]) -> None:
    """
    Renders all tasks to standard output.

    WHY `enumerate()` INSTEAD OF `range(len(...))`?
    -----------------------------------------------
    In Python, `range(len(collection))` is considered an anti-pattern:
    it forces manual indexing (`tasks[i]`), increases clutter, and introduces
    index error risks.

    `enumerate(tasks, start=1)` yields a clean `(index, item)` tuple on each
    iteration, giving us both human-friendly display numbering and direct access
    to the task dictionary without manual lookup syntax.
    """
    if not tasks:
        print("\n[!] Your to-do list is currently empty.")
        return

    print("\n" + "=" * 60)
    print(f"{'#':<4} {'ID':<6} {'STATUS':<12} {'TASK'}")
    print("-" * 60)

    # Idiomatic Python iteration: unpacking tuple (display_index, task_dict)
    for display_idx, task in enumerate(tasks, start=1):
        status = "[DONE]" if task.get("completed", False) else "[PENDING]"
        print(f"{display_idx:<4} {task['id']:<6} {status:<12} {task['task']}")

    print("=" * 60)


def mark_task_done(tasks: list[dict], task_id: int) -> bool:
    """
    Finds a task by its primary key (`id`) and toggles its status to completed.
    Returns True if found and updated, False otherwise.
    """
    for task in tasks:
        if task["id"] == task_id:
            task["completed"] = True
            return True
    return False


def delete_task(tasks: list[dict], task_id: int) -> bool:
    """
    Finds and deletes a task by its primary key (`id`).
    Returns True if found and removed, False otherwise.
    """
    for index, task in enumerate(tasks):
        if task["id"] == task_id:
            tasks.pop(index)
            return True
    return False


def save_tasks_to_file(tasks: list[dict], filepath: Path = DATA_FILE) -> None:
    """
    Serializes the tasks list to disk as a JSON file.
    Provides persistence so records survive application restart.
    """
    try:
        with open(filepath, mode="w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=4)
    except OSError as err:
        print(f"\n[!] Error saving tasks to disk: {err}")


def load_tasks_from_file(filepath: Path = DATA_FILE) -> list[dict]:
    """
    Loads and deserializes tasks from disk.
    If the file does not exist or contains invalid JSON, returns an empty list.
    """
    if not filepath.exists():
        return []

    try:
        with open(filepath, mode="r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            print("\n[!] Warning: Stored data is not a list. Starting with empty list.")
            return []
    except (json.JSONDecodeError, OSError) as err:
        print(f"\n[!] Warning: Could not read {filepath} ({err}). Starting with empty list.")
        return []


# ============================================================================
# USER INTERFACE / PRESENTATION LAYER
# Rule: Menu code handles user input, prompts, and validation, but delegates
# list modifications to the data functions above.
# ============================================================================

def prompt_non_empty(prompt_message: str) -> str:
    """
    Repeatedly prompts the user until a non-empty, stripped string is provided.
    Stretch Goal: Input Validation.
    """
    while True:
        value = input(prompt_message).strip()
        if value:
            return value
        print("[!] Input cannot be empty or whitespace. Please try again.")


def prompt_integer(prompt_message: str) -> int:
    """
    Safely prompts for an integer without crashing if user types invalid text.
    Stretch Goal: Robust Error Handling.
    """
    while True:
        user_input = input(prompt_message).strip()
        try:
            return int(user_input)
        except ValueError:
            print("[!] Please enter a valid numerical ID.")


def show_menu() -> None:
    """Prints the command menu options."""
    print("\n--- TO-DO LIST MANAGER ---")
    print("1. View Tasks")
    print("2. Add Task")
    print("3. Mark Task as Done")
    print("4. Delete Task")
    print("5. Save & Exit")


def main() -> None:
    """
    Application entry point.
    Coordinates initialization, main event loop, and teardown.
    """
    # Initialize state from disk (Stretch Goal: Persistence)
    my_tasks: list[dict] = load_tasks_from_file()
    print("Welcome to To-Do List Manager!")
    if my_tasks:
        print(f"[i] Loaded {len(my_tasks)} existing task(s) from {DATA_FILE.name}.")

    while True:
        show_menu()
        choice = input("Enter choice (1-5): ").strip()

        if choice == "1":
            view_tasks(my_tasks)

        elif choice == "2":
            task_text = prompt_non_empty("Enter task description: ")
            created = add_task(my_tasks, task_text)
            print(f"[✓] Task added successfully! (ID: {created['id']})")

        elif choice == "3":
            if not my_tasks:
                print("\n[!] No tasks available to mark as done.")
                continue
            view_tasks(my_tasks)
            task_id = prompt_integer("Enter the ID of the task to mark done: ")
            if mark_task_done(my_tasks, task_id):
                print(f"[✓] Task {task_id} marked as completed!")
            else:
                print(f"[!] Task with ID {task_id} not found.")

        elif choice == "4":
            if not my_tasks:
                print("\n[!] No tasks available to delete.")
                continue
            view_tasks(my_tasks)
            task_id = prompt_integer("Enter the ID of the task to delete: ")
            if delete_task(my_tasks, task_id):
                print(f"[✓] Task {task_id} deleted successfully!")
            else:
                print(f"[!] Task with ID {task_id} not found.")

        elif choice == "5":
            save_tasks_to_file(my_tasks)
            print(f"\n[✓] Tasks saved to {DATA_FILE.name}. Goodbye!")
            break

        else:
            # Stretch Goal: Handle invalid menu choices without crashing
            print("[!] Invalid option. Please enter a number from 1 to 5.")


# ============================================================================
# MAIN GUARD
# ----------------------------------------------------------------------------
# The `if __name__ == '__main__':` pattern guarantees that `main()` runs
# ONLY when this file is executed directly as a script (e.g. `python todo.py`).
# If this file is imported by another module or automated test runner
# (e.g. `import todo` in pytest), `main()` will not unintentionally run.
# ============================================================================
if __name__ == "__main__":
    main()
