# read parameter from file
import os
class ParameterReader(object):
	def __init__(self, _filename="parameters.txt"):
		self.filename = _filename
		fp = open(self.filename, 'r')
		self.parameters = {}
		while True:
			line = fp.readline() # '\n' is part of line
			if line=="": # line="" means end of file
				break
			line = line.strip()
			if line=="": # after strip, line=="": white line
				continue
			if (line[0]=='#'): # skip comment line
				continue
#			print("line=|"+line+"|")
			pair = line.split('=')
			if len(pair)!=2:
				continue
			key = pair[0].strip()
			value = pair[1].strip()
			self.parameters[key] = value
		fp.close()
	def getData(self, key):
		try:
			ret = self.parameters[key.strip()]
		except:
			print("EXCEPTION:no parameter called:%s!!!"%key)
		return ret
