#!/usr/bin/env python3

"""jpy.py: A python shell. Written by Joshua Free (jfre553 2646577)"""


import os
import shlex



def main():
	counter = 0
	history = {}

	while (True):
		arg = input(os.getcwd() + "$> ")
		counter += 1
		history[counter]=arg
		if (counter>10):
			del history[counter-10]

		amper = ('&' in arg)

		listarg = stringToList(arg)

		listargLength = len(listarg)

		
		#Handle "PWD"
		if("pwd" in listarg):
			if (listargLength==1):
				print(os.getcwd())
				continue
			else:
				print("Incorrect use of pwd")
				continue

		#Handle cd
		if ("cd" in listarg):
			if (listargLength==2):
				os.chdir(listarg[1])
				continue
			else:
				print("Incorrect use of cd: Need exactly one arg")
				continue

		#handle history
		if ("history" in listarg or "h" in listarg):
			if (listargLength == 1):
				#Return formatted history list
				for key in history:
					print("{} : {}".format(key, history[key]))
				continue

			elif (listargLength == 2):
				try:
					float(listarg[1])
					#execute history for specific number and update dictionary
					history[counter] = history[float(listarg[1])]

					executeFork(stringToList(history[float(listarg[1])]), amper)
					print("A specific history value to execute")
					continue

				except ValueError:
					print ("Argument must be a number")
					continue
			else:
				print("Incorrect use of history, either the command by itself or with one argument which is a number")
				continue

		piping=False
		
		if ("|" in listarg):
			piping = True
			splitList = [[] for _ in range(listarg.count("|")+1)]
			count=0
			listcount=0
			for arg in listarg:
				if (arg == "|"):
					listcount+=1
				else:
					splitList[listcount].append(arg)
				count+=1

		
		if (piping):
			executeFork(listarg, amper, splitList, piping)
		else:
			executeFork(listarg, amper, None, piping)


def executeFork(listarg, amper, splitList,piping):
	pid = os.fork()
	if (pid == 0):

		if (piping):
			for command in splitList:
				#Do forking and piping



		if (len(listarg)==1):
			# print ("1 arg")
			os.execvp(listarg[0],[""])
		# print ("2 arg")
		# os.execvp("ls",["l"])
		os.execvp(listarg[0], listarg)

	if (not amper):
		# wait for process to finish
		retid = os.wait()

def stringToList(line):

    lexer = shlex.shlex(line, posix=True)
    lexer.whitespace_split = False
    lexer.wordchars += '#$+-,./?@^='
    args = list(lexer)
    return args




if __name__ == '__main__':
	main()


