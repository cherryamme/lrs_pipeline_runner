import os
import subprocess
import sys
import threading
import time

import PySimpleGUI as sg

task_dict = {
    "task1":1,
    "task2":2,
    "task3":3,
    "task4":4,
    "task5":5,
    "ERROR":0,
}
# print=sg.Print
cp = sg.cprint

THREAD_KEY='-THREAD-'
THREAD_DONE='-THREAD_DONE-'
THREAD_TASK_DONE=len(task_dict)-1

def run_command(window,cmd,task_name):
    cp("run in commmand")
    pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(cmd)
    for line in pipe.stdout:
        line = line.decode(errors='replace' if (sys.version_info) < (3, 5) else 'backslashreplace').rstrip()
        print(line)
        for key in task_dict:
            if key in line:
                window.write_event_value(('-THREAD-', task_name), task_dict[key])

def run_batch(window):
    # 运行整个批次
    # 使用singularity、inputdir、outputdir、configdir
    cp("run command1")
    window.start_thread(lambda: run_command(window,"bash run3.sh","run3"), (THREAD_KEY, THREAD_TASK_DONE))
    cp("run command2")
    window.start_thread(lambda: run_command(window,"bash run4.sh","run4"), (THREAD_KEY, THREAD_TASK_DONE))
    layout_task = [[sg.Text(f'TASK-{i}'),sg.ProgressBar(THREAD_TASK_DONE, 'h', size=(30,20), k=f'-PROGRESS-{i}', expand_x=True)] for i in ["run3","run4"]]
    taskwindow = sg.Window('lrs_pipeline2', layout_task,finalize=True,enable_close_attempted_event=True)
    return taskwindow
def run_barcode():
    # 运行一个barcode
    # 使用singularity、inputdir、outputdir、configdir
    pass

# Define the window's contents
layout = [[sg.Text("What's your name?")],
          [sg.Input(key='-INPUT-')],
          [sg.Text('docker', size=(8, 1)), sg.Input(key="docker"), sg.FileBrowse()],
          [sg.Text('inputdir', size=(8, 1)), sg.Input(key="inputdir"), sg.FolderBrowse()],
          [sg.Text('configdir', size=(8, 1)), sg.Input(key="configdir"), sg.FolderBrowse()],
          [sg.Text('outputdir', size=(8, 1)), sg.Input(key="outputdir"), sg.FolderBrowse()],
          [sg.Text('Output Log here',key='-LOG-', font='Any 15')],
          [sg.Multiline(size=(65,20), key='-ML-', autoscroll=True, reroute_stdout=True, write_only=True, reroute_cprint=True)],
          [sg.Text(key='-OUTPUT-')],
          [sg.Button('Run')]]

# Create the window
window = sg.Window('lrs_pipeline', layout,enable_close_attempted_event=True)
while True:
    event, values = window.read()
    # See if user wants to quit or window was closed
    if event == (sg.WINDOW_CLOSE_ATTEMPTED_EVENT or event == 'Exit') and sg.popup_yes_no('Do you really want to exit?') == 'Yes':
        break
    # else:
    #     continue
    # Output a message to the window
    print(event,values)
    if event == "Run":
        batch_name=os.path.basename(values["inputdir"])
        cp(f"Run {batch_name} config:{values}",colors='white on green')
        ## 使用config投递任务
        taskwindow = run_batch(window)
    elif event[0] == THREAD_KEY:
        print(event,values)
        if values[event] == THREAD_TASK_DONE:
            taskwindow[f'-PROGRESS-{event[1]}'].update(values[event], THREAD_TASK_DONE,bar_color = ("green","white"))
        elif isinstance(values[event],int):
            # sg.one_line_progress_meter(f'Process {event[1]}',values[event], THREAD_TASK_DONE, event[1],'Optional message')
            taskwindow[f'-PROGRESS-{event[1]}'].update(values[event], THREAD_TASK_DONE,bar_color = ("blue","white"))


# Finish up by removing from the screen
window.close()