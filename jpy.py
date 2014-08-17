#!/usr/bin/env python3

"""jpy.py: A python shell. Written by Joshua Free (jfre553 2646577)"""

import os
import shlex
import sys


def main():
    counter = 0
    history = {}

    while True:
        arg = input(os.getcwd() + "$> ")
        counter += 1
        history[counter] = arg
        if counter > 10:
            del history[counter - 10]

        amper = ('&' in arg)

        list_arg = string_to_list(arg)

        list_arg_length = len(list_arg)

        # Handle "PWD"
        if "pwd" in list_arg:
            if list_arg_length == 1:
                print(os.getcwd())
                continue
            else:
                print("Incorrect use of pwd")
                continue

        #Handle cd
        if "cd" in list_arg:
            if list_arg_length == 2:
                os.chdir(list_arg[1])
                continue
            else:
                print("Incorrect use of cd: Need exactly one arg")
                continue

        #handle history
        if "history" in list_arg or "h" in list_arg:
            if list_arg_length == 1:
                #Return formatted history list
                for key in history:
                    print("{} : {}".format(key, history[key]))
                continue

            elif list_arg_length == 2:
                try:
                    float(list_arg[1])
                    #execute history for specific number and update dictionary
                    history[counter] = history[float(list_arg[1])]

                    execute_fork(string_to_list(history[float(list_arg[1])]), amper)
                    print("A specific history value to execute")
                    continue

                except ValueError:
                    print ("Argument must be a number")
                    continue
            else:
                print("Incorrect use of history, either the command by itself or with one argument which is a number")
                continue

        piping = False

        if "|" in list_arg:
            piping = True
            split_list = [[] for _ in range(list_arg.count("|") + 1)]
            count = 0
            list_count = 0
            for arg in list_arg:
                if arg == "|":
                    list_count += 1
                else:
                    split_list[list_count].append(arg)
                count += 1

        if piping:
            execute_piping(split_list, amper)
        else:
            execute_fork(list_arg, amper)


def execute_piping(split_list, amper):
    pipe_list = []

    for i in range(0, (len(split_list) + 1)):
        pipe_list.append((os.pipe()))

    pid = os.fork()

    if pid == 0:

        for j in range(0, len(split_list) - 1, 2):
            print ("iteration")
            print (j)

            if j == len(split_list):
                os.dup2(pipe_list[j][0], sys.stdin.fileno())

                print ("executed last")
                if len(split_list[j]) == 1:
                    # print ("1 arg")
                    os.execvp(split_list[j][0], [""])
                # print ("2 arg")
                # os.execvp("ls",["l"])
                os.execvp(split_list[j][0], split_list[j])

            pid = os.fork()

            if pid == 0:
                if j != len(split_list):
                    print(j, pid)
                    os.dup2(pipe_list[j][0], sys.stdin.fileno())
                    os.dup2(pipe_list[j + 1][1], sys.stdout.fileno())

                    if len(split_list[j]) == 1:
                        # print ("1 arg")
                        os.execvp(split_list[j][0], [""])
                    # print ("2 arg")
                    # os.execvp("ls",["l"])
                    os.execvp(split_list[j][0], split_list[j])
                else:
                    os.dup2(pipe_list[j][0], sys.stdin.fileno())

                    print ("executed last")
                    if len(split_list[j]) == 1:
                        # print ("1 arg")
                        os.execvp(split_list[j][0], [""])
                    # print ("2 arg")
                    # os.execvp("ls",["l"])
                    os.execvp(split_list[j][0], split_list[j])

            else:
                if j != len(split_list):
                    print("else")
                    print(j, pid)
                    os.dup2(pipe_list[j + 1][0], sys.stdin.fileno())
                    os.dup2(pipe_list[j + 2][1], sys.stdout.fileno())

                    if len(split_list[j + 1]) == 1:
                        # print ("1 arg")
                        os.execvp(split_list[j][0], [""])
                    # print ("2 arg")
                    # os.execvp("ls",["l"])
                    os.execvp(split_list[j][0], split_list[j])
                else:
                    os.dup2(pipe_list[j][0], sys.stdin.fileno())

                    print ("executed last")
                    if len(split_list[j]) == 1:
                        # print ("1 arg")
                        os.execvp(split_list[j][0], [""])
                    # print ("2 arg")
                    # os.execvp("ls",["l"])
                    os.execvp(split_list[j][0], split_list[j])

    else:
        if not amper:
            # wait for process to finish
            ret_id = os.wait()


def execute_fork(list_arg, amper):
    pid = os.fork()
    if pid == 0:

        if len(list_arg) == 1:
            # print ("1 arg")
            os.execvp(list_arg[0], [""])
        # print ("2 arg")
        # os.execvp("ls",["l"])
        os.execvp(list_arg[0], list_arg)

    if not amper:
        # wait for process to finish
        ret_id = os.wait()


def string_to_list(line):
    lexer = shlex.shlex(line, posix=True)
    lexer.whitespace_split = False
    lexer.wordchars += '#$+-,./?@^='
    args = list(lexer)
    return args

if __name__ == '__main__':
    main()


