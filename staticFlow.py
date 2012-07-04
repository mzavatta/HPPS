#! /usr/bin/python
import sys
import os
import subprocess

class Implementation:
	def __init__(self,pe,name):
		self.name=name
		self.pe=pe

class Task:
	def __init__(self,name):
		self.name=name
		self.implementations=list()
		self.exTime=list()
		self.recTime=list()

class Application:
	def __init__(self,name,fileName):
		self.name=name
		self.tasks=list()
		self.fileName=fileName


applications=list()
tasks=list()
implementations=list()

if(len(sys.argv) < 3):
	print "Error in parameters number"
	print "./pythonTagParse SOURCES ARCHITECTURE"
	sys.exit()


sourceFile=list();
for i in range(0,len(sys.argv)-1):
	sourceFile.append(sys.argv[i])

#arch=open(sys.argv[len(sys.argv)-1],"a")

for src in sourceFile:
	fileSrc=open(src,"r")
	sourceLines=fileSrc.readlines()

	for l in sourceLines:
		if(l.find("#pragma")==0):
			part=l.split(" ")
			typeTag=part[1]

			if(typeTag=="APP"):			
				nameTag=part[2]
				name=nameTag.split("=")[1]
				appName=name.strip()
				applications.append(Application(appName,src))

			if(typeTag=="TASK"):
				if(part[2].find("name")==0):
					nameTag=part[2]
					name=nameTag.split("=")[1]
					taskName=name.strip()
					task=Task(taskName)
					tasks.append(task)
					applications[len(applications)-1].tasks.append(task)
				if(part[2].find("mapping")==0):
					mapTag=part[2]
					maps=mapTag.split("=")[1]
					impls=maps.split("\t")
					for i in impls:
						implName=i.strip()
						normName=tasks[len(tasks)-1].name+"_"+implName
						impl=Implementation(i.strip(),implName)
						tasks[len(tasks)-1].implementations.append(impl)
						if(implementations.count(normName)==0):
							implementations.append(normName)



archXml=sys.argv[len(sys.argv)-1]

os.system("mkdir temp");
os.system("rm temp/* -Rf");

xmlName="./temp/application.xml"
srcName=sys.argv[1]

os.system("cp "+srcName+" ./temp/"+srcName)
os.system("cp "+archXml+" "+xmlName)
os.system("cp ./script/createArchitecture ./temp/createArchitecture")

source="./temp/"+srcName
srcName=srcName.split(".")[0]

for a in applications:
	outFile=open(xmlName,"a")

	outFile.write("<application id=\""+a.name+"\" name=\""+a.name+"\">\n");
	outFile.write("\t<solution>\n")
	for t in a.tasks:
		if(t.implementations[0].name.find("microblaze")==0):
			outFile.write("\t\t\t<mapping_task task=\""+t.name+"\" proc=\""+t.implementations[0].name+"\" impl=\"1\"/>\n")	
		else:
			outFile.write("\t\t\t<mapping_task task=\""+t.name+"\" proc=\"ReconfArea\" impl=\"1\"/>\n")
	outFile.write("\t</solution>\n")
	outFile.write("</application>\n");
	outFile.write("</faster>\n");

	outFile.close()

	scriptFile=open("scriptFile","w")
	os.system("chmod +x scriptFile")

	scriptFile.write("#! /bin/bash\n")
	scriptFile.write("cd temp\n")

	scriptFile.write("./createArchitecture "+srcName+"\n")

	scriptFile.write("cd ..\n")

	scriptFile.write("mkdir MPSoC-"+srcName+"\n")
	scriptFile.write("rm MPSoC-"+srcName+"/* -rf\n")
	scriptFile.write("cp ./temp/tempFiles/int_scripts/int_arch/* ./MPSoC-"+srcName+"/ -rf\n")

	scriptFile.write("rm temp/* -rf\n")
	scriptFile.write("rmdir temp\n")

	scriptFile.close()

	os.system("./scriptFile")

	os.system("rm scriptFile")