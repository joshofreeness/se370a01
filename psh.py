
import os
import shlex
import sys
import subprocess
import signal

jobs = []
current_child_pid = None

def intercept_z(signum, frame):
    process = current_child_pid
    if process is not None:
        jobs.append(process)
        os.kill(process, signal.SIGKILL)
    for job in jobs:
        try:
            fo = open("/proc/{0}/status".format(job),"r")
            fo.readline()
            line = fo.readline()
            if ("zombie" in line) or ("done" in line):
                jobs.remove(job)
                os.waitpid(job, 0)

            fo.close()
            
        except FileNotFoundError:
            jobs.remove(job)
    x=1
    for job in jobs:
        # subp = subprocess.Popen(["ps", "-p", str(job), "-o", "state="])
        # out = subp.communicate()
        try:
            out = subprocess.check_output(["ps", "-p", str(job), "-o", "state="])
        except subprocess.CalledProcessError:
            out=[68,0]
            jobs.remove(job)
        status=out[0]
        if out[0] == 83:
            status = "Sleeping"
        if out[0] == 90:
            os.waitpid(job, 0)
            status = "Done"
        if out[0] == 68:
            status = "Done" 

        print ("[{0}] <{1}> cmd_string ({2})".format(x+1,status,job))
        x+=1


    #print("HAHAHAHAHAHAHAHA")


signal.signal(signal.SIGTSTP, intercept_z)

def main():
    counter = 0
    history = {}
    
    initial_directory = os.getcwd()

    while True:
        #current_processes = os.listdir("/proc")
        #print (current_processes)
        for job in jobs:
            try:
                fo = open("/proc/{0}/status".format(job),"r")
                fo.readline()
                line = fo.readline()
                if ("zombie" in line) or ("done" in line):
                    jobs.remove(job)
                    os.waitpid(job, 0)
                fo.close()
                
            except FileNotFoundError:
                jobs.remove(job)
                #print("Closed")

        redirected = not os.isatty(sys.stdin.fileno())

        if redirected:
            print ("$>"),
            arg = sys.stdin.readline()
            print(arg),
            if not arg:
                exit()
        else:
            arg = input("$> ")

        if not arg:
            continue

        counter += 1
        history[counter] = arg
        if counter > 10:
            del history[counter - 10]

        list_arg = string_to_list(arg)

        amper = ('&' in list_arg)

        if amper:
            list_arg.remove('&')


        #Handle cd
        if "cd" in list_arg:
            #print (list_arg)
            if len(list_arg) == 2:
                list_arg[1] = list_arg[1].replace('~',os.getenv("HOME"))

                try:
                    #print (list_arg)
                    os.chdir(list_arg[1])
                except FileNotFoundError:
                    print("No such file or directory: " + list_arg[1])
                continue
            elif len(list_arg) == 1:
                #os.chdir(os.getenv("HOME"))
                os.chdir(initial_directory)
                continue
            else:
                print("Incorrect use of cd: Need exactly one or two arguments")
                continue

        #handle history
        if ("history" in list_arg) or ("h" in list_arg):
            if (len(list_arg) == 1) or ("|" in list_arg):
                pass
                #Return formatted history list
                #for key in history:
                    #print("{} : {}".format(key, history[key]))
                #continue

            elif len(list_arg) == 2:
                try:
                    float(list_arg[1])
                    #execute history for specific number and update dictionary
                    history[counter] = history[float(list_arg[1])]

                    list_arg = string_to_list(history[float(list_arg[1])])
                    #print("A specific history value to execute")

                except ValueError:
                    print("Argument must be a number")
                    continue
            else:
                print("Incorrect use of history, either the command by itself or with one argument which is a number")
                continue

        execute(list_arg, amper, history, jobs)


def execute(list_arg, amper, history, jobs):
    input_fid = sys.stdin.fileno()
    output_fid = sys.stdout.fileno()
    first_read = None
    last_read = None
    pid_main = os.fork()
    current_child_pid = pid_main
    
    #If in the child process
    if pid_main == 0:

        #if piping
        if "|" in list_arg:
            list_pipe = list_to_list_pipe(list_arg)
            #Pipe and save read and write
            first_read, first_write = os.pipe()

            #fork
            pid = os.fork()
            #execute first command
            execute_command(list_pipe[0], input_fid, first_write, pid, history, jobs)


            if len(list_pipe) == 2:
                #Reassign read and write
                last_read = first_read
            else:
                last_read = first_read

                #loop through the second command to the second to last command
                for x in range(1, len(list_pipe) - 1):

                    #New pipe
                    new_read, new_write = os.pipe()
                    #fork 
                    pid = os.fork()
                    #Execute with the previous read pipe and the new write pipe
                    execute_command(list_pipe[x], last_read, new_write, pid, history, jobs)

                    last_read = new_read
            #fork again
            pid = os.fork()
            #Execute the last command with stdout as output
            execute_command(list_pipe[-1], last_read, output_fid, pid, history, jobs)
            try:
                os.wait()
            except InterruptedError:
                pass
            exit()

        else:
            pid = os.fork()
            execute_command(list_arg, input_fid, output_fid, pid, history, jobs)
            try:
                os.wait()
            except InterruptedError:
                pass

            #jobs.pop(pid_value)
            exit()
    if pid_main != 0:
        jobs.append(pid_main)



    if not amper:
        try:
            os.wait()
        except InterruptedError:
            pass
        current_child_pid = None
    else:
        print("[{0}] {1}".format(len(jobs), jobs[-1]))


def execute_command(command, input_fid, output_fid, pid, history, jobs):

    if pid == 0:
        os.dup2(input_fid, sys.stdin.fileno())
        os.dup2(output_fid, sys.stdout.fileno())

        if len(command) == 1:
            check_inbuilt(command, history, jobs)
            os.execvp(command[0], [""])
            print("THIS SHOULD NEVER BE PRINTED")
        check_inbuilt(command, history, jobs)
        os.execvp(command[0], command)
        print("THIS SHOULD NEVER BE PRINTED")



def check_inbuilt(command, history, jobs):

    #Handle pwd
    if "pwd" in command:
            if len(command) == 1:
                print(os.getcwd())
                exit()
            else:
                print("Incorrect use of pwd")
                exit()

    if ("history" in command) or ("h" in command):
            if len(command) == 1:
                #Return formatted history list
                for key in history:
                    print("{} : {}".format(key, history[key]))
                exit()
            else:
                print("Incorrect use of history")
                exit()

    if "jobs" in command:
        for job in jobs:
            try:
                fo = open("/proc/{0}/status".format(job),"r")
                fo.readline()
                line = fo.readline()
                if ("zombie" in line) or ("done" in line):
                    jobs.remove(job)
                    os.waitpid(job, 0)

                fo.close()
                
            except FileNotFoundError:
                jobs.remove(job)
        x=1
        for job in jobs:
            # subp = subprocess.Popen(["ps", "-p", str(job), "-o", "state="])
            # out = subp.communicate()
            try:
                out = subprocess.check_output(["ps", "-p", str(job), "-o", "state="])
            except subprocess.CalledProcessError:
                out=[68,0]
                jobs.remove(job)
            status=out[0]
            if out[0] == 83:
                status = "Sleeping"
            if out[0] == 90:
                status = "Zombie"
            if out[0] == 68:
                status = "Done" 

            print ("[{0}] <{1}> cmd_string ({2})".format(x+1,status,job))
            x+=1

            
        exit()

    return


def list_to_list_pipe(list_arg):

    while list_arg[0] == "|":
        list_arg.pop(0)

    while list_arg[-1] == "|":
        list_arg.pop(-1)

    last = ""
    for arg in list_arg:
        if arg == last and arg == "|":
            list_arg.remove(arg)
        last = arg

    split_list = [[] for _ in range(list_arg.count("|") + 1)]
    count = 0
    list_count = 0
    for arg in list_arg:
        if arg == "|":
            list_count += 1
        else:
            split_list[list_count].append(arg)
        count += 1

    return split_list


def string_to_list(line):
    lexer = shlex.shlex(line, posix=True)
    lexer.whitespace_split = False
    lexer.wordchars += '#$+-,./?@^='
    args = list(lexer)
    return args

if __name__ == '__main__':
    main()