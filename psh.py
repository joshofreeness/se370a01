
import os
import shlex
import sys


def main():
    counter = 0
    history = {}
    jobs = []

    while True:
        redirected = not os.isatty(sys.stdin.fileno())

        if redirected:
            arg = sys.stdin.readline()
            print(arg)
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
            if len(list_arg) == 2:
                try:
                    os.chdir(list_arg[1])
                except FileNotFoundError:
                    print("No such file or directory: " + list_arg[1])
                continue
            elif len(list_arg) == 1:
                os.chdir(os.getenv("HOME"))
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
    jobs.append(pid_main)
    pid_value = len(jobs) - 1
    if pid_main == 0:
        if "|" in list_arg:
            list_pipe = list_to_list_pipe(list_arg)
            first_read, first_write = os.pipe()
            pid = os.fork()
            execute_command(list_pipe[0], input_fid, first_write, pid, history)

            if len(list_pipe) == 2:
                last_read = first_read
            else:
                last_read = first_read

                for x in range(1, len(list_pipe) - 1):

                    #print(list_pipe[x])
                    new_read, new_write = os.pipe()

                    pid = os.fork()
                    execute_command(list_pipe[x], last_read, new_write, pid, history)

                    last_read = new_read
            pid = os.fork()
            execute_command(list_pipe[-1], last_read, output_fid, pid, history)
            os.wait()
            exit()

        else:
            pid = os.fork()
            execute_command(list_arg, input_fid, output_fid, pid, history)
            os.wait()
            #jobs.pop(pid_value)
            exit()

    if not amper:
        os.wait()
    else:
        print("[{0}] {1}".format(len(jobs), jobs[-1]))


def execute_command(command, input_fid, output_fid, pid, history):

    if pid == 0:
        os.dup2(input_fid, sys.stdin.fileno())
        os.dup2(output_fid, sys.stdout.fileno())

        if len(command) == 1:
            check_inbuilt(command, history)
            os.execvp(command[0], [""])
            print("THIS SHOULD NEVER BE PRINTED")
        check_inbuilt(command, history)
        os.execvp(command[0], command)
        print("THIS SHOULD NEVER BE PRINTED")


def check_inbuilt(command, history):

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