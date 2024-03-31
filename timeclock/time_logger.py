#------------
# Simple Program that logs beginning and end times by given project name.
#------------

import argparse
import json
from datetime import datetime
import tkinter as tk

TIME_LOG_FILE = 'time_log.json'
STATUS_DATA = 'status_data.json'


#----------- Major Functions ---------

def begin_time_log(project_name):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    entry = {'project_name': project_name, 'begin_time': current_time}
    save_entry(entry)
    print(f'Time logging started for project: {project_name} at {current_time}')

def stop_time_log(active_project):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    saved_entries = load_entries(active_project)

    if saved_entries:
        last_entry = saved_entries[-1]

        if 'end_time' not in last_entry:
            last_entry['end_time'] = current_time
            last_entry['total_time'] = calculate_total_time([last_entry])

            save_entries(active_project, saved_entries)
            save_active_project(None)

            print(f'Time logging stopped for project: {active_project} at {current_time}')
            print(f'Total time logged for {active_project}: {last_entry["total_time"]}')
        else:
            print(f'Time logging stopped for project: {active_project} at {last_entry['end_time']}')
            save_active_project(None)
            set_pause(False)
    else:
        print(f'Error: No time log entries found for project {active_project}.')

def pause_time_log(active_project,paused):
    if paused:
        begin_time_log(active_project)
        set_pause(False)
    else:
        stop_time_log(active_project)
        save_active_project(active_project)
        set_pause(True)

def display_report_by_day(selected_date):
    time_logs = load_time_logs()

    print(f'{selected_date}\'s time logs:')
    for project_name, entries in time_logs.items():
        selected_entries = [entry for entry in entries if entry.get('begin_time', '').startswith(selected_date)]
        if selected_entries:
            print(f'Project: {project_name}')
            print(json.dumps(selected_entries, indent=2))
            total_time = calculate_total_time(selected_entries)
            print(f'Total time for {selected_date}: {total_time}')

# ---------- utlity functions -----------
def calculate_total_time(entries):
    total_time = sum((datetime.strptime(entry['end_time'], '%Y-%m-%d %H:%M:%S') -
                     datetime.strptime(entry['begin_time'], '%Y-%m-%d %H:%M:%S')).total_seconds()
                    for entry in entries)
    hours, remainder = divmod(total_time, 3600)
    minutes, _ = divmod(remainder, 60)
    return f'{int(hours)} hours {int(minutes)} minutes'

#------------ time log file -------------
def save_entries(project_name, entries):
    time_logs = load_time_logs()
    time_logs[project_name] = entries
    with open(TIME_LOG_FILE, 'w') as file:
        json.dump(time_logs, file, indent=2)

def load_entries(project_name):
    time_logs = load_time_logs()
    return time_logs.get(project_name, [])

def save_entry(entry):
    active_project = load_active_project()
    if active_project:
        saved_entries = load_entries(active_project)
        saved_entries.append(entry)
        save_entries(active_project, saved_entries)
    else:
        print('Error: No active project found. Use "begin" to begin a time log for a project.')

def load_time_logs():
    try:
        with open(TIME_LOG_FILE, 'r') as file:
            time_logs = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        time_logs = {}
    return time_logs

 #-------------- Active Projects and Pause File-------

def save_active_project(project_name):
    data = load_data()
    data['active_project'] = project_name
    save_data(data)

def load_active_project():
    data = load_data()
    return data.get('active_project', None)

def set_pause(pause):
    data = load_data()
    data['pause'] = pause
    save_data(data)

def get_pause():
    data = load_data()
    return data.get('pause', None)

def load_data():
    try:
        with open(STATUS_DATA, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_data(data):
    with open(STATUS_DATA, 'w') as file:
        json.dump(data, file)

#------------Define Tkinter GUI -------
root = tk.Tk()
root.title("Project Time Clock")

# Project Name entry
project_name_label = tk.Label(root, text="Project Name:")
project_name_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
project_name_entry = tk.Entry(root)
project_name_entry.grid(row=0, column=1, padx=10, pady=5)

# Date entry
date_label = tk.Label(root, text="Date (YYYY-MM-DD):")
date_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
date_entry = tk.Entry(root)
date_entry.grid(row=1, column=1, padx=10, pady=5)
date_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))  # Autofill today's date

#------------ GUI event handling ------
        
def begin_event():
    active_project = load_active_project()
    if not active_project:
            project_name = project_name_entry.get()
            save_active_project(project_name)
            begin_time_log(project_name)
    else:
        #impleplemt pop up box with error
        pass

def pause_event():
    active_project = load_active_project()
    paused = get_pause()
    if active_project:
            pause_time_log(active_project, paused)
    else:
        #impleplemt pop up box with error
        pass

def end_event():
    active_project = load_active_project()
    if active_project:
            stop_time_log(active_project)
    else:
        #impleplemt pop up box with error
        pass

def report_event():
    active_project = load_active_project()
    paused = get_pause()
    if not active_project or paused:
        display_report_by_day(date_entry.get())
    else:
        #impleplemt pop up box with error
        pass


# Buttons
begin_button = tk.Button(root, text="Begin", command=begin_event)
begin_button.grid(row=2, column=0, padx=10, pady=5)

pause_resume_button = tk.Button(root, text="Pause/Resume", command=pause_event)
pause_resume_button.grid(row=2, column=1, padx=10, pady=5)

end_button = tk.Button(root, text="End", command=end_event)
end_button.grid(row=2, column=2, padx=10, pady=5)

report_button = tk.Button(root, text="Report", command=report_event)
report_button.grid(row=2, column=3, padx=10, pady=5)

#------------ driver code -----------
def main():
    parser = argparse.ArgumentParser(description='Time logging script for projects.')
    parser.add_argument('command', choices=['begin', 'pause_resume', 'end', 'today', 'report', 'status', 'gui'], help='Command to perform (begin, end, today)')
    args = parser.parse_args()

    active_project = load_active_project()
    paused = get_pause()

    if args.command == 'pause_resume':
        if active_project:
            pause_time_log(active_project, paused)
        else:
            print("There is no active project currently running.")

    elif args.command == 'end':
        if active_project:
            stop_time_log(active_project)
        else:
            print("There is no active project currently running.")
        
    elif args.command == 'begin':
        if not active_project:
            project_name = input('Enter the project name to begin time logging: ')
            save_active_project(project_name)
            begin_time_log(project_name)
        else:
            print(f"{active_project} is active. Please end the project before beginning a new one.")

    elif args.command == 'today':
        if not active_project or paused:
            display_report_by_day(datetime.now().strftime('%Y-%m-%d'))
        else:
            print(f"{active_project} is active. Please pause or end the project to query the timelog.")

    elif args.command == 'report':
        if not active_project or paused:
            display_report_by_day(input("Enter date (YYYY-MM-DD): "))
        else:
            print(f"{active_project} is active. Please pause or end the project to query the timelog.")

    elif args.command == 'status':
        print(f"Project: {active_project} - Paused: {paused}")

    elif args.command == 'gui':
        root.mainloop()

if __name__ == "__main__":
    main()