import PySimpleGUI as sg
import time,sys
import subprocess

"""
	Demo Program - Realtime output of a shell command in the window
		Shows how you can run a long-running subprocess and have the output
		be displayed in realtime in the window.
    
    Copyright 2022 PySimpleGUI		
"""
def runCommand(cmd, timeout=None, window=None):

    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return p

def main():
    layout = [
        [sg.Multiline(size=(110, 30), echo_stdout_stderr=True, reroute_stdout=True, autoscroll=True, background_color='black', text_color='white', key='-MLINE-')],
        [sg.T('Promt> '), sg.Input(key='-IN-', focus=True, do_not_clear=False)],
        [sg.Text('process 1', size=(8, 1)),sg.ProgressBar(5, orientation='h', size=(20, 20), key='progressbar1')],
        [sg.Text('process 2', size=(8, 1)),sg.ProgressBar(10, orientation='h', size=(20, 20), key='progressbar2')],
        [sg.Button('Run', bind_return_key=True), sg.Button('Exit')]]

    window = sg.Window('Realtime Shell Command Output', layout)
    while True:  # Event Loop
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        elif event == 'Run':
            p1 = subprocess.Popen("sh run1.sh", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            p2 = subprocess.Popen("sh run2.sh", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            # p1 = subprocess.Popen("sh run1.sh", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            # p2 = runCommand(cmd="sh run2.sh")
            while True:
                output1 = p1.stdout.readline().rstrip().decode('utf-8')
                if output1 != '':
                    print(output1.strip())
                    window['progressbar1'].Update(int(output1),bar_color = ("blue","white"))
                output2 = p2.stdout.readline().rstrip().decode('utf-8')
                if output2 != '':
                    print(output2.strip())
                    window['progressbar2'].Update(int(output2),bar_color = ("blue","white"))
                # if output1 == '' and p1.poll() is None and output2 == '' and p1.poll() is None:
                #     break
                time.sleep(0.1)


    window.close()


main()