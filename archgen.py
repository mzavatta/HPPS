#! /usr/bin/python
import sys
import os
import subprocess
import xml.dom
import copy
from xml.dom.minidom import parseString

class Parameter:
	def __init__(self,name,value):
		self.name=name
		self.value=value

class Port:
	def __init__(self,name,value):
		self.name=name
		self.value=value

class BusInterface:
	def __init__(self,name,value):
		self.name=name
		self.value=value

class Component:
	def __init__(self,cls,parameters,ports,businterfaces):
		self.cls=cls
		self.parameters=parameters
		self.ports=ports
		self.businterfaces=businterfaces

#class BusPLB:
#	def __init__(self,parameters,ports,businterfaces):
#		self.parameters=parameters
#		self.ports=ports
#		self.businterfaces=businterfaces

componentSpecs=list()
components=list()

mpspecFile = open('mpspecs','r')
mpspecLines = mpspecFile.readlines()

# import component descriptions from mpd-like file
l=0;
while (l<len(mpspecLines)):
	if mpspecLines[l].find("BEGIN")>=0:
		elem=mpspecLines[l].rstrip().split(" ")
		tempComponent = Component(elem[1],list(),list(),list())
		#print elem
		#print tempComponent.cls
		l=l+1
		while (mpspecLines[l].find("END")!=0):
			elem=mpspecLines[l].rstrip().split(" ")
			#print elem
			for e in range(0,len(elem)):
				if elem[e]=="PARAMETER":
					tempComponent.parameters.append(Parameter(elem[e+1],""))
					break
				if elem[e]=="PORT":
					tempComponent.ports.append(Port(elem[e+1],""))
					break
				if elem[e]=="BUS_INTERFACE":
					tempComponent.businterfaces.append(BusInterface(elem[e+1],""))
					break	
			l=l+1
			#else if elem[0]=="PORT":
		componentSpecs.append(tempComponent)
	l=l+1


for item1 in componentSpecs:
	print "BEGIN "+item1.cls
        for item2 in item1.parameters:
		print "PARAMETER "+item2.name
	for item3 in item1.ports:
		print "PORT "+item3.name
	for item4 in item1.businterfaces:
		print "BUS_INTERFACE "+item4.name
	print "END"



#open the xml file for reading:
archFile = open('architecture.xml','r')
#convert to string:
data = archFile.read()
#close file because we dont need it anymore:
archFile.close()
#parse the xml you got from the file
dom = parseString(data)

for node in dom.documentElement.childNodes:
	if node.nodeType == 1 and node.tagName=="architecture":
		architectureNode = node

for node in architectureNode.childNodes:
	if node.nodeType == 1 and node.tagName=="system":
		systemNode = node

#print systemNode.tagName
#print systemNode.childNodes


for node in systemNode.childNodes:
	if node.nodeType == 1:
		if node.getAttribute("class")=="xps_mailbox":
			# find component specification and instanciate
			for item in componentSpecs:
				if item.cls == "xps_mailbox":
					tempInstance = item
					break
			# assign instance name
			for p in tempInstance.parameters:
				if p.name == "INSTANCE":
					p.value = node.getAttribute("id")
					break
			# assign addresses
			for child in node.childNodes:
				print child
				if child.nodeType == 1 and child.tagName=="addrs":
					for addresses in child.childNodes:
						print addresses
						if (addresses.nodeType == 1 and addresses.tagName=="addr" and \
									addresses.getAttribute("id")=="SPLB0"):
							for p in tempInstance.parameters:
								if p.name=="C_SPLB0_BASEADDR":
									p.value=addresses.getAttribute("base")
								if p.name=="C_SPLB0_HIGHADDR":
									p.value=addresses.getAttribute("high")
						if (addresses.nodeType == 1 and addresses.tagName=="addr" and
												addresses.getAttribute("id")=="SPLB1"):
							for p in tempInstance.parameters:
								if p.name=="C_SPLB1_BASEADDR":
									p.value=addresses.getAttribute("base")
								if p.name=="C_SPLB1_HIGHADDR":
									p.value=addresses.getAttribute("high")
			# insert the instance into the component list
			components.append(copy.deepcopy(tempInstance))

		elif node.getAttribute("class")=="plb_v46":
			# find component specification and instanciate
			for item in componentSpecs:
				if item.cls == "plb_v46":
					tempInstance = item
					break
			# assign instance name
			for p in tempInstance.parameters:
				if p.name == "INSTANCE":
					p.value = node.getAttribute("id")
					break
			# insert the instance into the component list
			components.append(copy.deepcopy(tempInstance))

		
		elif node.getAttribute("class")=="microblaze":
			# find component specification and instanciate
			for item in componentSpecs:
				if item.cls == "microblaze":
					tempInstance = item
					break
			# assign instance name
			for p in tempInstance.parameters:
				if p.name == "INSTANCE":
					p.value = node.getAttribute("id")
					break
			# insert the instance into the component list
			components.append(copy.deepcopy(tempInstance))


		elif node.getAttribute("class")=="bram_block":
			# find component specification and instanciate
			for item in componentSpecs:
				if item.cls == "bram_block":
					tempInstance = item
					break
			# assign instance name
			for p in tempInstance.parameters:
				if p.name == "INSTANCE":
					p.value = node.getAttribute("id")
					break
			# insert the instance into the component list
			components.append(copy.deepcopy(tempInstance))

		elif node.getAttribute("class")=="lmb_v10":
			# find component specification and instanciate
			for item in componentSpecs:
				if item.cls == "lmb_v10":
					tempInstance = item
					break
			# assign instance name
			for p in tempInstance.parameters:
				if p.name == "INSTANCE":
					p.value = node.getAttribute("id")
					break
			# insert the instance into the component list
			components.append(copy.deepcopy(tempInstance))


		elif node.getAttribute("class")=="lmb_bram_if_cntlr":
			# find component specification and instanciate
			for item in componentSpecs:
				if item.cls == "lmb_bram_if_cntlr":
					tempInstance = item
					break
			# assign instance name
			for p in tempInstance.parameters:
				if p.name == "INSTANCE":
					p.value = node.getAttribute("id")
					break
			# assign addresses
			for child in node.childNodes:
				print child
				if child.nodeType == 1 and child.tagName=="addrs":
					for addresses in child.childNodes:
						if (addresses.nodeType == 1 and addresses.tagName=="addr"):
							for p in tempInstance.parameters:
								if p.name=="C_BASEADDR":
									p.value=addresses.getAttribute("base")
								if p.name=="C_HIGHADDR":
									p.value=addresses.getAttribute("high")
			# insert the instance into the component list
			components.append(copy.deepcopy(tempInstance))





print "\nIMPORTED ARCH"
for item1 in components:
	print "BEGIN "+item1.cls
        for item2 in item1.parameters:
		print "PARAMETER "+item2.name+" "+item2.value
	for item3 in item1.ports:
		print "PORT "+item3.name+" "+item3.value
	for item4 in item1.businterfaces:
		print "BUS_INTERFACE "+item4.name+" "+item4.value
	print "END"


# stats extraction
nnmicroblaze=0
nnplb=0
nnbram=0
nnlmb=0
nnlmb_bram_if_cntlr=0


for item in components:
	if item.cls == "microblaze": nnmicroblaze+=1
	elif item.cls == "bram_block": nnbram+=1
	elif item.cls == "plb_v46": nnplb+=1
	elif item.cls == "lmb_v10": nnlmb+=1
	elif item.cls == "lmb_bram_if_cntlr": nnlmb_bram_if_cntlr+=1
	

#### building architecture

# how many masters on each bus?
# bus with only slaves doesn't make much sense

# assign processor-memory cluster
if nnmicroblaze==2:
	assert nnlmb==4
	assert nnlmb_bram_if_cntlr==4
	

		

		

