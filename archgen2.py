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
	def __init__(self,name,sigis,dir,value):
		self.name=name
		self.sigis=sigis
		self.dir=dir
		self.value=value

class BusInterface:
	def __init__(self,name,std,type,value):
		self.name=name		#name e.g. SPLB
		self.std=std 		#standard bus e.g. PLBV46, XIL_BRAM...
		self.type=type
		self.value=value 	#interconnect value

class Component:
	bus = "" 
	def __init__(self,cls,instance,parameters,ports,businterfaces):
		self.cls=cls
		self.instance=instance	#instance should be into the parameters list but it is kept outside for convenience
					#as it is often a search objective
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
#l=0;
#while (l<len(mpspecLines)):
#	if mpspecLines[l].find("BEGIN")>=0:
#		elem=mpspecLines[l].rstrip().split(" ")
#		tempComponent = Component(elem[1],list(),list(),list())
#		#print elem
#		#print tempComponent.cls
#		l=l+1
#		while (mpspecLines[l].find("END")!=0):
#			elem=mpspecLines[l].rstrip().split(" ")
#			#print elem
#			for e in range(0,len(elem)):
#				if elem[e]=="PARAMETER":
#					tempComponent.parameters.append(Parameter(elem[e+1],""))
#					break
#				if elem[e]=="PORT":
#					tempComponent.ports.append(Port(elem[e+1],""))
#					break
#				if elem[e]=="BUS_INTERFACE":
#					tempComponent.businterfaces.append(BusInterface(elem[e+1],""))
#					break	
#			l=l+1
#			#else if elem[0]=="PORT":
#		componentSpecs.append(tempComponent)
#	l=l+1


#for item1 in componentSpecs:
#	print "BEGIN "+item1.cls
 #       for item2 in item1.parameters:
#		print "PARAMETER "+item2.name
#	for item3 in item1.ports:
#		print "PORT "+item3.name
#	for item4 in item1.businterfaces:
#		print "BUS_INTERFACE "+item4.name
#	print "END"


################################################################## XML Import ###########################################################
#################  Creation of the "space" of the possible interconnect combinations ####################################################

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

for node in dom.documentElement.childNodes:
	if node.nodeType == 1 and node.tagName=="connection":
		connectionNode = node

for node in architectureNode.childNodes:
	if node.nodeType == 1 and node.tagName=="system":
		systemNode = node

#print systemNode.tagName
#print systemNode.childNodes

for node in systemNode.childNodes:
	if node.nodeType == 1:

		if node.getAttribute("class")=="xps_mailbox":
			# assign class and instance name
			tempInstance = Component("xps_mailbox",node.getAttribute("id"),list(),list(),list())
			# assign addresses
			for child in node.childNodes:
				if child.nodeType == 1 and child.tagName=="addrs":
					for addresses in child.childNodes:
						if (addresses.nodeType == 1 and addresses.tagName=="addr" and \
									addresses.getAttribute("id")=="SPLB0"):
							tempInstance.parameters.append(Parameter("C_SPLB0_BASEADDR",addresses.getAttribute("base")))
							tempInstance.parameters.append(Parameter("C_SPLB0_HIGHADDR",addresses.getAttribute("high")))
						if (addresses.nodeType == 1 and addresses.tagName=="addr" and
												addresses.getAttribute("id")=="SPLB1"):
							tempInstance.parameters.append(Parameter("C_SPLB1_BASEADDR",addresses.getAttribute("base")))
							tempInstance.parameters.append(Parameter("C_SPLB1_HIGHADDR",addresses.getAttribute("high")))
				
			# go into ./hw/XilinxProcessorIPLib/xps_mailbox_v2_00_b/xps_mailbox.mpd and read it
			tmpFile = open('./hw/XilinxProcessorIPLib/pcores/xps_mailbox_v2_00_b/data/xps_mailbox_v2_1_0.mpd','r')
			tmpFileLines = tmpFile.readlines()
			# fetch bus interfaces
			for line in range(0,len(tmpFileLines)):
				if tmpFileLines[line].find("BUS_INTERFACE")>=0:
					elem=tmpFileLines[line].rstrip().split(" ")
					elem = [e.strip(",") for e in elem]
					stdIndex = elem.index("BUS_STD") + 2
					nameIndex = elem.index("BUS") + 2
					typeIndex = elem.index("BUS_TYPE") +2
					tempInstance.businterfaces.append(BusInterface(elem[nameIndex],elem[stdIndex],elem[typeIndex],""))
			# fetch ports which do not belong to a bus
			for line in range(0,len(tmpFileLines)):
				if tmpFileLines[line].find("PORT")>=0 and tmpFileLines[line].find("BUS")<0:
					elem = tmpFileLines[line].rstrip().split(" ")
					elem = [e.strip(",") for e in elem]
					sigisIndex=0
					dirIndex=0
					for e in range(0,len(elem)):
						if elem[e]=="SIGIS": sigisIndex=e+2
						elif elem[e]=="DIR": dirIndex=e+2
					if sigisIndex!=0 and dirIndex!=0:					
						tempInstance.ports.append(Port(elem[1],elem[sigisIndex],elem[dirIndex],""))
					elif sigisIndex!=0 and dirIndex==0:
						tempInstance.ports.append(Port(elem[1],elem[sigisIndex],"",""))
					elif sigisIndex==0 and dirIndex!=0:
						tempInstance.ports.append(Port(elem[1],"",elem[dirIndex],""))
					else: tempInstance.ports.append(Port(elem[1],"","",""))

			# insert the instance into the component list
			components.append(copy.deepcopy(tempInstance))


		elif node.getAttribute("class")=="plb_v46":
			# assign instance name
			tempInstance = Component("plb_v46",node.getAttribute("id"),list(),list(),list())
			tempInstance.bus = "PLBV46"

			# go into the component folder and fetch BUS_INTERFACEs and PORTS
			tmpFile = open('./hw/XilinxProcessorIPLib/pcores/plb_v46_v1_04_a/data/plb_v46_v2_1_0.mpd','r')
			tmpFileLines = tmpFile.readlines()
			# fetch bus interfaces
			for line in range(0,len(tmpFileLines)):
				if tmpFileLines[line].find("BUS_INTERFACE")>=0:
					elem=tmpFileLines[line].rstrip().split(" ")
					elem = [e.strip(",") for e in elem]
					stdIndex = elem.index("BUS_STD") + 2
					nameIndex = elem.index("BUS") + 2
					typeIndex = elem.index("BUS_TYPE") +2
					tempInstance.businterfaces.append(BusInterface(elem[nameIndex],elem[stdIndex],elem[typeIndex],""))

			# fetch ports which do not belong to a bus
			for line in range(0,len(tmpFileLines)):
				if tmpFileLines[line].find("PORT")>=0 and tmpFileLines[line].find("BUS")<0:
					elem=tmpFileLines[line].rstrip().split(" ")
					elem = [e.strip(",") for e in elem]
					sigisIndex=0
					dirIndex=0
					for e in range(0,len(elem)):
						if elem[e]=="SIGIS": sigisIndex=e+2
						elif elem[e]=="DIR": dirIndex=e+2
					if sigisIndex!=0 and dirIndex!=0:					
						tempInstance.ports.append(Port(elem[1],elem[sigisIndex],elem[dirIndex],""))
					elif sigisIndex!=0 and dirIndex==0:
						tempInstance.ports.append(Port(elem[1],elem[sigisIndex],"",""))
					elif sigisIndex==0 and dirIndex!=0:
						tempInstance.ports.append(Port(elem[1],"",elem[dirIndex],""))
					else: tempInstance.ports.append(Port(elem[1],"","",""))


			# insert the instance into the component list
			components.append(copy.deepcopy(tempInstance))

		
		elif node.getAttribute("class")=="microblaze":
			# assign instance name
			tempInstance = Component("microblaze",node.getAttribute("id"),list(),list(),list())

			# go into the component folder and fetch BUS_INTERFACEs and PORTS
			tmpFile = open('./hw/XilinxProcessorIPLib/pcores/microblaze_v7_30_a/data/microblaze_v2_1_0.mpd','r')
			tmpFileLines = tmpFile.readlines()
			# fetch bus interfaces
			for line in range(0,len(tmpFileLines)):
				if tmpFileLines[line].find("BUS_INTERFACE")>=0:
					elem=tmpFileLines[line].rstrip().split(" ")
					elem = [e.strip(",") for e in elem]
					stdIndex = elem.index("BUS_STD") + 2
					nameIndex = elem.index("BUS") + 2
					typeIndex = elem.index("BUS_TYPE") +2
					tempInstance.businterfaces.append(BusInterface(elem[nameIndex],elem[stdIndex],elem[typeIndex],""))

			# fetch ports which do not belong to a bus
			for line in range(0,len(tmpFileLines)):
				if tmpFileLines[line].find("PORT")>=0 and tmpFileLines[line].find("BUS")<0:
					elem=tmpFileLines[line].rstrip().split(" ")
					elem = [e.strip(",") for e in elem]
					sigisIndex=0
					dirIndex=0
					for e in range(0,len(elem)):
						if elem[e]=="SIGIS": sigisIndex=e+2
						elif elem[e]=="DIR": dirIndex=e+2
					if sigisIndex!=0 and dirIndex!=0:					
						tempInstance.ports.append(Port(elem[1],elem[sigisIndex],elem[dirIndex],""))
					elif sigisIndex!=0 and dirIndex==0:
						tempInstance.ports.append(Port(elem[1],elem[sigisIndex],"",""))
					elif sigisIndex==0 and dirIndex!=0:
						tempInstance.ports.append(Port(elem[1],"",elem[dirIndex],""))
					else: tempInstance.ports.append(Port(elem[1],"","",""))


			# insert the instance into the component list
			components.append(copy.deepcopy(tempInstance))


		elif node.getAttribute("class")=="bram_block":
			# assign instance name
			tempInstance = Component("bram_block",node.getAttribute("id"),list(),list(),list())

			# go into the component folder and fetch BUS_INTERFACEs and PORTS
			tmpFile = open('./hw/XilinxProcessorIPLib/pcores/bram_block_v1_00_a/data/bram_block_v2_1_0.mpd','r')
			tmpFileLines = tmpFile.readlines()
			# fetch bus interfaces
			for line in range(0,len(tmpFileLines)):
				if tmpFileLines[line].find("BUS_INTERFACE")>=0:
					elem=tmpFileLines[line].rstrip().split(" ")
					elem = [e.strip(",") for e in elem]
					stdIndex = elem.index("BUS_STD") + 2
					nameIndex = elem.index("BUS") + 2
					typeIndex = elem.index("BUS_TYPE") +2
					tempInstance.businterfaces.append(BusInterface(elem[nameIndex],elem[stdIndex],elem[typeIndex],""))

			# fetch ports which do not belong to a bus
			for line in range(0,len(tmpFileLines)):
				if tmpFileLines[line].find("PORT")>=0 and tmpFileLines[line].find("BUS")<0:
					elem=tmpFileLines[line].rstrip().split(" ")
					elem = [e.strip(",") for e in elem]
					sigisIndex=0
					dirIndex=0
					for e in range(0,len(elem)):
						if elem[e]=="SIGIS": sigisIndex=e+2
						elif elem[e]=="DIR": dirIndex=e+2
					if sigisIndex!=0 and dirIndex!=0:					
						tempInstance.ports.append(Port(elem[1],elem[sigisIndex],elem[dirIndex],""))
					elif sigisIndex!=0 and dirIndex==0:
						tempInstance.ports.append(Port(elem[1],elem[sigisIndex],"",""))
					elif sigisIndex==0 and dirIndex!=0:
						tempInstance.ports.append(Port(elem[1],"",elem[dirIndex],""))
					else: tempInstance.ports.append(Port(elem[1],"","",""))

			# insert the instance into the component list
			components.append(copy.deepcopy(tempInstance))

		elif node.getAttribute("class")=="lmb_v10":
			# assign instance name
			tempInstance = Component("lmb_v10",node.getAttribute("id"),list(),list(),list())
			tempInstance.bus = "LMB"

			# go into the component folder and fetch BUS_INTERFACEs and PORTS
			tmpFile = open('./hw/XilinxProcessorIPLib/pcores/lmb_v10_v1_00_a/data/lmb_v10_v2_1_0.mpd','r')
			tmpFileLines = tmpFile.readlines()
			# fetch bus interfaces
			for line in range(0,len(tmpFileLines)):
				if tmpFileLines[line].find("BUS_INTERFACE")>=0:
					elem=tmpFileLines[line].rstrip().split(" ")
					elem = [e.strip(",") for e in elem]
					stdIndex = elem.index("BUS_STD") + 2
					nameIndex = elem.index("BUS") + 2
					typeIndex = elem.index("BUS_TYPE") +2
					tempInstance.businterfaces.append(BusInterface(elem[nameIndex],elem[stdIndex],elem[typeIndex],""))

			# fetch ports which do not belong to a bus
			for line in range(0,len(tmpFileLines)):
				if tmpFileLines[line].find("PORT")>=0 and tmpFileLines[line].find("BUS")<0:
					elem=tmpFileLines[line].rstrip().split(" ")
					elem = [e.strip(",") for e in elem]
					sigisIndex=0
					dirIndex=0
					for e in range(0,len(elem)):
						if elem[e]=="SIGIS": sigisIndex=e+2
						elif elem[e]=="DIR": dirIndex=e+2
					if sigisIndex!=0 and dirIndex!=0:					
						tempInstance.ports.append(Port(elem[1],elem[sigisIndex],elem[dirIndex],""))
					elif sigisIndex!=0 and dirIndex==0:
						tempInstance.ports.append(Port(elem[1],elem[sigisIndex],"",""))
					elif sigisIndex==0 and dirIndex!=0:
						tempInstance.ports.append(Port(elem[1],"",elem[dirIndex],""))
					else: tempInstance.ports.append(Port(elem[1],"","",""))


			# insert the instance into the component list
			components.append(copy.deepcopy(tempInstance))


		elif node.getAttribute("class")=="lmb_bram_if_cntlr":
			# assign instance name
			tempInstance = Component("lmb_bram_if_cntlr",node.getAttribute("id"),list(),list(),list())

			
			# assign addresses
			for child in node.childNodes:
				if child.nodeType == 1 and child.tagName=="addrs":
					for addresses in child.childNodes:
						if (addresses.nodeType == 1 and addresses.tagName=="addr"):
							tempInstance.parameters.append(Parameter("C_BASEADDR",addresses.getAttribute("base")))
							tempInstance.parameters.append(Parameter("C_HIGHADDR",addresses.getAttribute("high")))
			

			# go into the component folder and fetch BUS_INTERFACEs and PORTS
			tmpFile = open('./hw/XilinxProcessorIPLib/pcores/lmb_bram_if_cntlr_v2_10_b/data/lmb_bram_if_cntlr_v2_1_0.mpd','r')
			tmpFileLines = tmpFile.readlines()
			# fetch bus interfaces
			for line in range(0,len(tmpFileLines)):
				if tmpFileLines[line].find("BUS_INTERFACE")>=0:
					elem=tmpFileLines[line].rstrip().split(" ")
					elem = [e.strip(",") for e in elem]
					stdIndex = elem.index("BUS_STD") + 2
					nameIndex = elem.index("BUS") + 2
					typeIndex = elem.index("BUS_TYPE") +2
					tempInstance.businterfaces.append(BusInterface(elem[nameIndex],elem[stdIndex],elem[typeIndex],""))

			# fetch ports which do not belong to a bus
			for line in range(0,len(tmpFileLines)):
				if tmpFileLines[line].find("PORT")>=0 and tmpFileLines[line].find("BUS")<0:
					elem=tmpFileLines[line].rstrip().split(" ")
					elem = [e.strip(",") for e in elem]
					sigisIndex=0
					dirIndex=0
					for e in range(0,len(elem)):
						if elem[e]=="SIGIS": sigisIndex=e+2
						elif elem[e]=="DIR": dirIndex=e+2
					if sigisIndex!=0 and dirIndex!=0:					
						tempInstance.ports.append(Port(elem[1],elem[sigisIndex],elem[dirIndex],""))
					elif sigisIndex!=0 and dirIndex==0:
						tempInstance.ports.append(Port(elem[1],elem[sigisIndex],"",""))
					elif sigisIndex==0 and dirIndex!=0:
						tempInstance.ports.append(Port(elem[1],"",elem[dirIndex],""))
					else: tempInstance.ports.append(Port(elem[1],"","",""))


			# insert the instance into the component list
			components.append(copy.deepcopy(tempInstance))


		elif node.getAttribute("class")=="mpmc":
			
			# assign instance name
			tempInstance = Component("mpmc",node.getAttribute("id"),list(),list(),list())
			
			# assign addresses
			for child in node.childNodes:
				if child.nodeType == 1 and child.tagName=="addrs":
					for addresses in child.childNodes:
						if (addresses.nodeType == 1 and addresses.tagName=="addr"):
							tempInstance.parameters.append(Parameter("C_BASEADDR",addresses.getAttribute("base")))
							tempInstance.parameters.append(Parameter("C_HIGHADDR",addresses.getAttribute("high")))
			

			# go into the component folder and fetch BUS_INTERFACEs and PORTS
			tmpFile = open('./hw/XilinxProcessorIPLib/pcores/mpmc_v6_00_a/data/mpmc_v2_1_0.mpd','r')
			tmpFileLines = tmpFile.readlines()
			# fetch bus interfaces
			for line in range(0,len(tmpFileLines)):
				if tmpFileLines[line].find("BUS_INTERFACE")>=0:
					elem=tmpFileLines[line].rstrip().split(" ")
					elem = [e.strip(",") for e in elem]
					stdIndex = elem.index("BUS_STD") + 2
					nameIndex = elem.index("BUS") + 2
					typeIndex = elem.index("BUS_TYPE") +2
					tempInstance.businterfaces.append(BusInterface(elem[nameIndex],elem[stdIndex],elem[typeIndex],""))

			# fetch ports which do not belong to a bus
			for line in range(0,len(tmpFileLines)):
				if tmpFileLines[line].find("PORT")>=0 and tmpFileLines[line].find("BUS")<0:
					elem=tmpFileLines[line].rstrip().split(" ")
					elem = [e.strip(",") for e in elem]
					sigisIndex=0
					dirIndex=0
					for e in range(0,len(elem)):
						if elem[e]=="SIGIS": sigisIndex=e+2
						elif elem[e]=="DIR": dirIndex=e+2
					if sigisIndex!=0 and dirIndex!=0:					
						tempInstance.ports.append(Port(elem[1],elem[sigisIndex],elem[dirIndex],""))
					elif sigisIndex!=0 and dirIndex==0:
						tempInstance.ports.append(Port(elem[1],elem[sigisIndex],"",""))
					elif sigisIndex==0 and dirIndex!=0:
						tempInstance.ports.append(Port(elem[1],"",elem[dirIndex],""))
					else: tempInstance.ports.append(Port(elem[1],"","",""))


			# insert the instance into the component list
			components.append(copy.deepcopy(tempInstance))

			
		elif node.getAttribute("class")=="xps_intc":
			# assign instance name
			tempInstance = Component("xps_intc",node.getAttribute("id"),list(),list(),list())

			# assign addresses
			for child in node.childNodes:
				if child.nodeType == 1 and child.tagName=="addrs":
					for addresses in child.childNodes:
						if (addresses.nodeType == 1 and addresses.tagName=="addr"):
							tempInstance.parameters.append(Parameter("C_BASEADDR",addresses.getAttribute("base")))
							tempInstance.parameters.append(Parameter("C_HIGHADDR",addresses.getAttribute("high")))
			

			# go into the component folder and fetch BUS_INTERFACEs and PORTS
			tmpFile = open('./hw/XilinxProcessorIPLib/pcores/xps_intc_v2_01_a/data/xps_intc_v2_1_0.mpd','r')
			tmpFileLines = tmpFile.readlines()
			# fetch bus interfaces
			for line in range(0,len(tmpFileLines)):
				if tmpFileLines[line].find("BUS_INTERFACE")>=0:
					elem=tmpFileLines[line].rstrip().split(" ")
					elem = [e.strip(",") for e in elem]
					stdIndex = elem.index("BUS_STD") + 2
					nameIndex = elem.index("BUS") + 2
					typeIndex = elem.index("BUS_TYPE") +2
					tempInstance.businterfaces.append(BusInterface(elem[nameIndex],elem[stdIndex],elem[typeIndex],""))

			# fetch ports which do not belong to a bus
			for line in range(0,len(tmpFileLines)):
				if tmpFileLines[line].find("PORT")>=0 and tmpFileLines[line].find("BUS")<0:
					elem=tmpFileLines[line].rstrip().split(" ")
					elem = [e.strip(",") for e in elem]
					sigisIndex=0
					dirIndex=0
					for e in range(0,len(elem)):
						if elem[e]=="SIGIS": sigisIndex=e+2
						elif elem[e]=="DIR": dirIndex=e+2
					if sigisIndex!=0 and dirIndex!=0:					
						tempInstance.ports.append(Port(elem[1],elem[sigisIndex],elem[dirIndex],""))
					elif sigisIndex!=0 and dirIndex==0:
						tempInstance.ports.append(Port(elem[1],elem[sigisIndex],"",""))
					elif sigisIndex==0 and dirIndex!=0:
						tempInstance.ports.append(Port(elem[1],"",elem[dirIndex],""))
					else: tempInstance.ports.append(Port(elem[1],"","",""))


			# insert the instance into the component list
			components.append(copy.deepcopy(tempInstance))


		elif node.getAttribute("class")=="mdm":
			# assign instance name
			tempInstance = Component("mdm",node.getAttribute("id"),list(),list(),list())

			# assign addresses
			for child in node.childNodes:
				if child.nodeType == 1 and child.tagName=="addrs":
					for addresses in child.childNodes:
						if (addresses.nodeType == 1 and addresses.tagName=="addr"):
							tempInstance.parameters.append(Parameter("C_BASEADDR",addresses.getAttribute("base")))
							tempInstance.parameters.append(Parameter("C_HIGHADDR",addresses.getAttribute("high")))
			

			# go into the component folder and fetch BUS_INTERFACEs and PORTS
			tmpFile = open('./hw/XilinxProcessorIPLib/pcores/mdm_v1_00_g/data/mdm_v2_1_0.mpd','r')
			tmpFileLines = tmpFile.readlines()
			# fetch bus interfaces
			for line in range(0,len(tmpFileLines)):
				if tmpFileLines[line].find("BUS_INTERFACE")>=0:
					elem=tmpFileLines[line].rstrip().split(" ")
					elem = [e.strip(",") for e in elem]
					stdIndex = elem.index("BUS_STD") + 2
					nameIndex = elem.index("BUS") + 2
					typeIndex = elem.index("BUS_TYPE") +2
					tempInstance.businterfaces.append(BusInterface(elem[nameIndex],elem[stdIndex],elem[typeIndex],""))

			# fetch ports which do not belong to a bus
			for line in range(0,len(tmpFileLines)):
				if tmpFileLines[line].find("PORT")>=0 and tmpFileLines[line].find("BUS")<0:
					elem=tmpFileLines[line].rstrip().split(" ")
					elem = [e.strip(",") for e in elem]
					sigisIndex=0
					dirIndex=0
					for e in range(0,len(elem)):
						if elem[e]=="SIGIS": sigisIndex=e+2
						elif elem[e]=="DIR": dirIndex=e+2
					if sigisIndex!=0 and dirIndex!=0:					
						tempInstance.ports.append(Port(elem[1],elem[sigisIndex],elem[dirIndex],""))
					elif sigisIndex!=0 and dirIndex==0:
						tempInstance.ports.append(Port(elem[1],elem[sigisIndex],"",""))
					elif sigisIndex==0 and dirIndex!=0:
						tempInstance.ports.append(Port(elem[1],"",elem[dirIndex],""))
					else: tempInstance.ports.append(Port(elem[1],"","",""))


			# insert the instance into the component list
			components.append(copy.deepcopy(tempInstance))


		elif node.getAttribute("class")=="npi_coreE":

			# assign instance name
			tempInstance = Component("npi_coreE",node.getAttribute("id"),list(),list(),list())

			# assign addresses
			for child in node.childNodes:
				if child.nodeType == 1 and child.tagName=="addrs":
					for addresses in child.childNodes:
						if (addresses.nodeType == 1 and addresses.tagName=="addr"):
							tempInstance.parameters.append(Parameter("C_BASEADDR",addresses.getAttribute("base")))
							tempInstance.parameters.append(Parameter("C_HIGHADDR",addresses.getAttribute("high")))
			

			# go into the component folder and fetch BUS_INTERFACEs and PORTS
			tmpFile = open('./pcores/npi_coreE_v1_00_a/data/npi_coreE_v2_1_0.mpd','r')
			tmpFileLines = tmpFile.readlines()
			# fetch bus interfaces
			for line in range(0,len(tmpFileLines)):
				if tmpFileLines[line].find("BUS_INTERFACE")>=0:
					elem=tmpFileLines[line].rstrip().split(" ")
					elem = [e.strip(",") for e in elem]
					stdIndex = elem.index("BUS_STD") + 2
					nameIndex = elem.index("BUS") + 2
					typeIndex = elem.index("BUS_TYPE") +2
					tempInstance.businterfaces.append(BusInterface(elem[nameIndex],elem[stdIndex],elem[typeIndex],""))

			# fetch ports which do not belong to a bus
			for line in range(0,len(tmpFileLines)):
				if tmpFileLines[line].find("PORT")>=0 and tmpFileLines[line].find("BUS")<0:
					elem=tmpFileLines[line].rstrip().split(" ")
					elem = [e.strip(",") for e in elem]
					sigisIndex=0
					dirIndex=0
					for e in range(0,len(elem)):
						if elem[e]=="SIGIS": sigisIndex=e+2
						elif elem[e]=="DIR": dirIndex=e+2
					if sigisIndex!=0 and dirIndex!=0:					
						tempInstance.ports.append(Port(elem[1],elem[sigisIndex],elem[dirIndex],""))
					elif sigisIndex!=0 and dirIndex==0:
						tempInstance.ports.append(Port(elem[1],elem[sigisIndex],"",""))
					elif sigisIndex==0 and dirIndex!=0:
						tempInstance.ports.append(Port(elem[1],"",elem[dirIndex],""))
					else: tempInstance.ports.append(Port(elem[1],"","",""))


			# insert the instance into the component list
			components.append(copy.deepcopy(tempInstance))


		elif node.getAttribute("class")=="npi_coreD":

			# assign instance name
			tempInstance = Component("npi_coreD",node.getAttribute("id"),list(),list(),list())

			# assign addresses
			for child in node.childNodes:
				if child.nodeType == 1 and child.tagName=="addrs":
					for addresses in child.childNodes:
						if (addresses.nodeType == 1 and addresses.tagName=="addr"):
							tempInstance.parameters.append(Parameter("C_BASEADDR",addresses.getAttribute("base")))
							tempInstance.parameters.append(Parameter("C_HIGHADDR",addresses.getAttribute("high")))
			

			# go into the component folder and fetch BUS_INTERFACEs and PORTS
			tmpFile = open('./pcores/npi_coreD_v1_00_a/data/npi_coreD_v2_1_0.mpd','r')
			tmpFileLines = tmpFile.readlines()
			# fetch bus interfaces
			for line in range(0,len(tmpFileLines)):
				if tmpFileLines[line].find("BUS_INTERFACE")>=0:
					elem=tmpFileLines[line].rstrip().split(" ")
					elem = [e.strip(",") for e in elem]
					stdIndex = elem.index("BUS_STD") + 2
					nameIndex = elem.index("BUS") + 2
					typeIndex = elem.index("BUS_TYPE") +2
					tempInstance.businterfaces.append(BusInterface(elem[nameIndex],elem[stdIndex],elem[typeIndex],""))

			# fetch ports which do not belong to a bus
			for line in range(0,len(tmpFileLines)):
				if tmpFileLines[line].find("PORT")>=0 and tmpFileLines[line].find("BUS")<0:
					elem=tmpFileLines[line].rstrip().split(" ")
					elem = [e.strip(",") for e in elem]
					sigisIndex=0
					dirIndex=0
					for e in range(0,len(elem)):
						if elem[e]=="SIGIS": sigisIndex=e+2
						elif elem[e]=="DIR": dirIndex=e+2
					if sigisIndex!=0 and dirIndex!=0:					
						tempInstance.ports.append(Port(elem[1],elem[sigisIndex],elem[dirIndex],""))
					elif sigisIndex!=0 and dirIndex==0:
						tempInstance.ports.append(Port(elem[1],elem[sigisIndex],"",""))
					elif sigisIndex==0 and dirIndex!=0:
						tempInstance.ports.append(Port(elem[1],"",elem[dirIndex],""))
					else: tempInstance.ports.append(Port(elem[1],"","",""))


			# insert the instance into the component list
			components.append(copy.deepcopy(tempInstance))

		

#########################################################################################################################################

# sys.exit()



print "\nIMPORTED ARCH"
for item1 in components:
	print "BEGIN "+item1.cls
	print "PARAMETER INSTANCE "+item1.instance
	print "BUS "+item1.bus
	if item1.cls=="microblaze":
		for item2 in item1.parameters:
			print "PARAMETER "+item2.name+" "+item2.value
		for item3 in item1.ports:
			print "PORT "+item3.name+" "+item3.value
		for item4 in item1.businterfaces:
			print "BUS_INTERFACE "+item4.name+" "+item4.value+" "+item4.std+" "+item4.type
	print "END"


################################################ XML Import and interconnect generation ##################################################
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
	
print "#microblaze:"+str(nnmicroblaze)+" #plb:"+str(nnplb)+" #bram:"+str(nnbram)+" #lmb:"+str(nnlmb)+" #bram_cntrl:"+str(nnlmb_bram_if_cntlr)

#### building architecture

count = 0;
for node in connectionNode.childNodes:
	if node.nodeType == 1 and node.tagName=="virtual":
		#print "virtual group found"
		for vlink in node.childNodes:
			if vlink.nodeType == 1 and vlink.tagName=="link":
				#print "found virtual link"
				src = vlink.getAttribute("src")
				tgt = vlink.getAttribute("tgt")
				srcInstance=0
				tgtInstance=0
				for c in components:
					if c.instance == src: srcInstance = c 
					elif c.instance == tgt: tgtInstance = c
				
				if srcInstance==0 or tgtInstance==0:
					print "ERROR LINKS CONTAINS A COMPONENT INSTANCE NOT FOUND"
					break
				else:
					print srcInstance.instance
					print tgtInstance.instance
				

				#the target is a component of type bus
				if tgtInstance.bus!="":
					#print "target is a bus!"+tgtInstance.bus
					for i in srcInstance.businterfaces:
						if i.std == tgtInstance.bus and i.value=="":
							i.value = tgtInstance.instance
							break

				#point-to-point bus connection
				elif vlink.getAttribute("type")!="PORT":
					done = 0
					for srcinter in srcInstance.businterfaces:
						if (srcinter.type=="INITIATOR" or srcinter.type=="TARGET") and done==0:
							for tgtinter in tgtInstance.businterfaces:
								if tgtinter.type=="INITIATOR" or tgtinter.type=="TARGET":
									if srcinter.std==tgtinter.std and srcinter.value=="" and \
														tgtinter.value=="":
										srcinter.value="conn_"+str(count)
										tgtinter.value="conn_"+str(count)
										count+=1
										done=1
				#port connection e.g. interrupt
				else:
					done = 0
					for srcport in srcInstance.ports:
						for tgtport in tgtInstance.ports:
							if srcport.sigis==tgtport.sigis and done==0:
								if srcport.dir=="O" and tgtport.dir=="I" and srcport.value=="":
									#commented in this way if only one connection can be assigned to an
									#output port. If a device has two output ports of the same type,
									#eg the mailbox with interrupts, you have to tell me which out port to
									#use, otherwise I choose!
									#if  srcport.value=="":
									srcport.value="conn_"+str(count)
									if tgtport.value=="":
										tgtport.value="conn_"+str(count)
									else:
										tgtport.value=tgtport.value+"&conn_"+str(count)
									#else:
									#	temp = srcport.value
									#	if tgtport.value=="":
									#		tgtport.value=srcport.value
									#	else:
									#		tgtport.value=tgtport.value+"&"+srcport.value
										
									count+=1
									done=1
								elif srcport.dir=="I" and tgtport=="O" and tgtport.value=="":
									if  tgtport.value=="":
										tgtport.value="conn_"+str(count)
										if srcport.value=="":
											srcport.value="conn_"+str(count)
										else:
											srcport.value=srcport.value+"&conn_"+str(count)
									else:
										temp = tgtport.value
										if srcport.value=="":
											srcport.value=tgtport.value
										else:
											srcport.value=srcport.value+"&"+tgtport.value
										
									count+=1
									done=1
	
									"""
									tgtport.value="conn_"+str(count)
									if srcport.value=="":
										srcport.value="conn_"+str(count)
									else:
										srcport.value=srcport.value+"&conn_"+str(count)
									count+=1
									done=1
									"""
								elif srcport.dir=="IO" or tgtport.dir=="IO":
									if srcport.value=="":
										srcport.value="conn_"+str(count)
									else: srcport.value=srcport.value+"&conn_"+str(count)
									if tgtport.value=="":
										tgtport.value="conn_"+str(count)
									else: tgtport.value=tgtport.value+"&conn_"+str(count)
									count+=1
									done=1
					
					

"""
# clean unassgned values
for c in components:
	for pa in components.parameters:
		if p.value=="":
			p.del
	for po in components.ports:
		if po.value=="":
			po.del
	for bu in components.:
		if bu.value=="":
			bu.del

"""

"""
print "\nIMPORTED ARCH"
for item1 in components:
	#if item1.cls=="microblaze":
		print "\n"
		print "BEGIN "+item1.cls
		print "PARAMETER INSTANCE "+item1.instance
		print "BUS "+item1.bus
		for item2 in item1.parameters:
			print "PARAMETER "+item2.name+" "+item2.value
		if item1.cls!="mpmc":
			for item3 in item1.ports:
				print "PORT "+item3.name+" "+item3.value
		for item4 in item1.businterfaces:
			print "BUS_INTERFACE "+item4.name+" "+item4.value+" "+item4.std+" "+item4.type
		print "END"
"""
f = open('res','w')
print "\nIMPORTED ARCH"
for item1 in components:
		#print "\n"
		f.write("BEGIN "+item1.cls+"\n")
		f.write("PARAMETER INSTANCE "+item1.instance+"\n")
		f.write("BUS "+item1.bus+"\n")
		for item2 in item1.parameters:
			if item2.value!="":
				f.write("PARAMETER "+item2.name+" "+item2.value+"\n")
		#if item1.cls!="mpmc":
		for item3 in item1.ports:
			#if item3.value!="":
				f.write("PORT "+item3.name+" "+item3.value+" "+item3.sigis+" "+item3.dir+"\n")
		for item4 in item1.businterfaces:
			if item4.value!="":
				f.write("BUS_INTERFACE "+item4.name+" "+item4.value+" "+item4.std+" "+item4.type+"\n")
		f.write("END"+"\n")
		f.write("\n")



# how many masters on each bus?
# bus with only slaves doesn't make much sense

# assign processor-memory cluster
#if nnmicroblaze==2:
#	assert nnlmb==4
#	assert nnlmb_bram_if_cntlr==4
	
# check if all mandatory parameters are assigned
# remember to clean the unused parameters/ports/busint at the end
