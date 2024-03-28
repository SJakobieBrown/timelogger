#------------
# Simple Program that logs beginning and end times by given project name.
#
# Improvements:
# Respond to command 'report', prompt user for the date and create a report for given date
# Create a 'break' function, allow for stamping the time out and starting up again easier.
#------------

import argparse
import json
from datetime import datetime

TIME_LOG_FILE = 'time_log.json'
ACTIVE_PROJECT_FILE = 'active_project.json'

def begin_time_log(project_name):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    entry = {'project_name': project_name, 'begin_time': current_time}
    save_entry(entry)
    print(f'Time logging started for project: {project_name} at {current_time}')

def stop_time_log():
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    active_project = load_active_project()

    if active_project:
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
                print(f'Error: Project "{active_project}" is not actively being timed. Use "begin" to begin.')
        else:
            print(f'Error: No time log entries found for project {active_project}.')
    else:
        print('Error: No active project found. Use "begin" to begin a time log for a project.')

def pause_time_log():
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    active_project = load_active_project()

    if active_project:
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
                print(f'Error: Project "{active_project}" is not actively being timed. Use "begin" to begin.')
        else:
            print(f'Error: No time log entries found for project {active_project}.')
    else:
        print('Error: No active project found. Use "begin" to begin a time log for a project.')

def calculate_total_time(entries):
    total_time = sum((datetime.strptime(entry['end_time'], '%Y-%m-%d %H:%M:%S') -
                     datetime.strptime(entry['begin_time'], '%Y-%m-%d %H:%M:%S')).total_seconds()
                    for entry in entries)
    hours, remainder = divmod(total_time, 3600)
    minutes, _ = divmod(remainder, 60)
    return f'{int(hours)} hours {int(minutes)} minutes'

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

def save_active_project(project_name):
    with open(ACTIVE_PROJECT_FILE, 'w') as file:
        json.dump({'active_project': project_name}, file)

def load_active_project():
    try:
        with open(ACTIVE_PROJECT_FILE, 'r') as file:
            data = json.load(file)
            return data.get('active_project', None)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def display_report_by_day(selected_date):
    active_project = load_active_project()
    if active_project:
        print(f'Error: Project "{active_project}" is active. Stop it before viewing the report for {selected_date}.')
    else:
        time_logs = load_time_logs()

        print(f'{selected_date}\'s time logs:')
        for project_name, entries in time_logs.items():
            selected_entries = [entry for entry in entries if entry.get('begin_time', '').startswith(selected_date)]
            if selected_entries:
                print(f'Project: {project_name}')
                print(json.dumps(selected_entries, indent=2))
                total_time = calculate_total_time(selected_entries)
                print(f'Total time for {selected_date}: {total_time}')

def choose_date():
    return input("Enter date (YYYY-MM-DD): ")

def main():
    parser = argparse.ArgumentParser(description='Time logging script for projects.')
    parser.add_argument('command', choices=['begin', 'pause', 'end', 'today', 'report'], help='Command to perform (begin, end, today)')
    args = parser.parse_args()

    if args.command == 'begin':
        active_project = load_active_project()
        if active_project:
            print(f'Error: Project "{active_project}" is already active. Stop it before beginning a new one.')
        else:
            project_name = input('Enter the project name to begin time logging: ')
            save_active_project(project_name)
            begin_time_log(project_name)
    elif args.command == 'end':
        stop_time_log()
    elif args.command == 'pause':
        pause_time_log()
    elif args.command == 'today':
        display_report_by_day(datetime.now().strftime('%Y-%m-%d'))
    elif args.command == 'report':
        display_report_by_day(choose_date())
    else:
        print('Error: Invalid command. Use "begin", "end", or "today".')

if __name__ == "__main__":
    main()
