import tkinter as tk
from tkinter import filedialog
from threading import Thread
from functools import partial
from time_entry import run_time_entry


def browse_file_path(entry_widget):
    file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
    entry_widget.delete(0, tk.END)
    entry_widget.insert(0, file_path)


def run_script(file_path_entry, output_label, status_label):
    file_path = file_path_entry.get()
    status_label.config(text="Running...")

    def worker():
        try:
            run_time_entry(file_path)
            output_label.config(text="All time entries have been completed.")
        except Exception as e:
            output_label.config(text=f"Error: {e}")
        finally:
            status_label.config(text="Idle")

    script_thread = Thread(target=worker)
    script_thread.start()


# GUI setup
root = tk.Tk()
root.title("Time Entry Automation GUI")

# File Path
file_path_label = tk.Label(root, text="Excel File Path:")
file_path_label.grid(row=0, column=0, padx=10, pady=10)
path_entry = tk.Entry(root, width=50)
path_entry.grid(row=0, column=1, padx=10, pady=10)
browse_button = tk.Button(root, text="Browse", command=partial(browse_file_path, path_entry))
browse_button.grid(row=0, column=2, padx=10, pady=10)

# Output Label
output = tk.Label(root, text="")
output.grid(row=1, column=0, columnspan=3, pady=10)

# Status Label
status = tk.Label(root, text="Idle")
status.grid(row=2, column=0, columnspan=3, pady=10)

# Run Button
run_button = tk.Button(root, text="Run Automation", command=partial(run_script, path_entry, output, status))
run_button.grid(row=3, column=0, columnspan=3, pady=10)

# Start the GUI event loop
root.mainloop()
