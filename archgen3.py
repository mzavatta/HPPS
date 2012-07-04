#! /usr/bin/python
"""
Author: Marco Zavatta
Date: July 2012
Xilinx EDK files generation from a custom XML specification
"""

import sys
import os
import subprocess
import xml.dom
import copy
import time
import datetime
from xml.dom.minidom import parseString


########### Output files definitions
mhsoutput = "restemp"
xmlinput = "architecture_custom.xml"
########### Classes definitions



class ComponentClass:
	def __init__(self,className,mpdPath):
		self.className=className
		self.mpdPath=mpdPath

class GlobalPort:
	def __init__(self,name,value,attributes):
		self.name=name
		self.attributes=attributes
		self.value=value

class Attribute:
	def __init__(self,name,value):
		self.name=name
		self.value=value

class Component:
	bus = "" 
	def __init__(self,cls,instance,parameters,ports,businterfaces):
		self.cls=cls
		self.instance=instance	#instance should be into the parameters list but it is kept outside for convenience
					#as it is often a search objective
		self.parameters=parameters
		self.ports=ports
		self.businterfaces=businterfaces

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
###########


########### Component classes definitions
xps_mailbox = ComponentClass("xps_mailbox","./hw/XilinxProcessorIPLib/pcores/xps_mailbox_v2_00_b/data/xps_mailbox_v2_1_0.mpd")
plb_v46 = ComponentClass("plb_v46","./hw/XilinxProcessorIPLib/pcores/plb_v46_v1_04_a/data/plb_v46_v2_1_0.mpd")
microblaze = ComponentClass("microblaze","./hw/XilinxProcessorIPLib/pcores/microblaze_v7_30_a/data/microblaze_v2_1_0.mpd")
bram_block = ComponentClass("bram_block","./hw/XilinxProcessorIPLib/pcores/bram_block_v1_00_a/data/bram_block_v2_1_0.mpd")
lmb_v10 = ComponentClass("lmb_v10","./hw/XilinxProcessorIPLib/pcores/lmb_v10_v1_00_a/data/lmb_v10_v2_1_0.mpd")
lmb_bram_if_cntlr = ComponentClass("lmb_bram_if_cntlr","./hw/XilinxProcessorIPLib/pcores/lmb_bram_if_cntlr_v2_10_b/data/lmb_bram_if_cntlr_v2_1_0.mpd")
mpmc = ComponentClass("mpmc","./hw/XilinxProcessorIPLib/pcores/mpmc_v6_00_a/data/mpmc_v2_1_0.mpd")
xps_intc = ComponentClass("xps_intc","./hw/XilinxProcessorIPLib/pcores/xps_intc_v2_01_a/data/xps_intc_v2_1_0.mpd")
mdm = ComponentClass("mdm","./hw/XilinxProcessorIPLib/pcores/mdm_v1_00_g/data/mdm_v2_1_0.mpd")
npi_coreE = ComponentClass("npi_coreE","./pcores/npi_coreE_v1_00_a/data/npi_coreE_v2_1_0.mpd")
npi_coreD = ComponentClass("npi_coreD","./pcores/npi_coreD_v1_00_a/data/npi_coreD_v2_1_0.mpd")
npi_coreA = ComponentClass("npi_coreA","./pcores/npi_coreA_v1_00_a/data/npi_coreA_v2_1_0.mpd")
npi_coreC = ComponentClass("npi_coreC","./pcores/npi_coreC_v1_00_a/data/npi_coreC_v2_1_0.mpd")
proc_sys_reset = ComponentClass("proc_sys_reset","./hw/XilinxProcessorIPLib/pcores/proc_sys_reset_v2_00_a/data/proc_sys_reset_v2_1_0.mpd")
clock_generator = ComponentClass("clock_generator","./hw/XilinxProcessorIPLib/pcores/clock_generator_v4_00_a/data/clock_generator_v2_1_0.mpd")

componentClasses = list()

componentClasses.append(xps_mailbox)
componentClasses.append(plb_v46)
componentClasses.append(microblaze)
componentClasses.append(bram_block)
componentClasses.append(lmb_v10)
componentClasses.append(lmb_bram_if_cntlr)
componentClasses.append(mpmc)
componentClasses.append(xps_intc)
componentClasses.append(mdm)
componentClasses.append(npi_coreE)
componentClasses.append(npi_coreD)
componentClasses.append(npi_coreA)
componentClasses.append(npi_coreC)
componentClasses.append(proc_sys_reset)
componentClasses.append(clock_generator)
##########

##########
mpspecsFile = "./mpspecs"
mpspecLines = open('mpspecs','r').readlines()
##########


##########
componentSpecs=list()
components=list()
globalports=list()
##########



#class BusPLB:
#	def __init__(self,parameters,ports,businterfaces):
#		self.parameters=parameters
#		self.ports=ports
#		self.businterfaces=businterfaces



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
archFile = open(xmlinput,'r')
data = archFile.read()
archFile.close()
dom = parseString(data)

for node in dom.documentElement.childNodes:
	if node.nodeType == 1 and node.tagName=="architecture":
		architectureNode = node

for node in architectureNode.childNodes:
	if node.nodeType == 1 and node.tagName=="system":
		systemNode = node

for node in dom.documentElement.childNodes:
	if node.nodeType == 1 and node.tagName=="connection":
		connectionNode = node

for node in connectionNode.childNodes:
	if node.nodeType == 1 and node.tagName=="physical":
		physicalNode = node

for node in connectionNode.childNodes:
	if node.nodeType == 1 and node.tagName=="virtual":
		virtualNode = node

for node in physicalNode.childNodes:
	if node.nodeType == 1 and node.tagName=="pinout":
		pinoutNode = node


############### Component Import from xml, mpspecs, mpd

#given and XML node (component to be instanciated) and a list of components
#instanciate the component, fill in the information about it and append the newly instanciated component to the list

def importComponent(node, components):
	
	print "import component entered"
	# instanciate based on xml
	id = node.getAttribute("id")
	cls = node.getAttribute("class")
	tempInstance = Component(cls,id,list(),list(),list())
	print "current xml node is id:"+id+" class:"+cls
	
	####### TO BE CHANGED GOING INTO THE mpd ######
	if cls=="plb_v46":
		tempInstance.bus = "PLBV46"
	elif cls=="lmb_v10":
		tempInstance.bus = "LMB"
	
	#fetch default parameters in mpspecs
	valid = 0
	for l in range(0,len(mpspecLines)):
		elem = mpspecLines[l].rstrip().split(" ")
		if "BEGIN" and cls in elem: # trigger valid =1 when the class is found
			valid=1
		elif "PARAMETER" in elem and valid==1: # if valid and if it is a parameter line, append a new parameter
			for e in range(0,len(elem)):
					if elem[e]=="PARAMETER":
						tempInstance.parameters.append(Parameter(elem[e+1],elem[e+3]))
						break
		elif "END" in elem:
			valid=0	# clear valid when END block is found

	
	#add/overwrite parameters from XML and add addresses
	found=0
	for child in node.childNodes: 
		if child.nodeType == 1 and child.tagName=="param": #for every parameter in the xml
			found=0
			new_param_name = child.getAttribute("name")
			new_param_value = child.getAttribute("val")
			for old_param in tempInstance.parameters: #check in every parameter of the temporary instance
				if old_param.name == new_param_name: #if parameter already defined, overwrite
					old_param.value = new_param_value
					found=1
					break #only useful to save up iterations as there cannot be two parameters with the same name
			if found == 0:	#if not already defined, append
				tempInstance.parameters.append(Parameter(new_param_name,new_param_value))



	#go into the mpd and take bus interfaces and ports which do not belong to a bus
	for clas in componentClasses:
		if clas.className == cls:
			temp_mpd_path = clas.mpdPath
			break
	tmpFile = open(temp_mpd_path,'r')
	tmpFileLines = tmpFile.readlines()
	for line in range(0,len(tmpFileLines)): # fetch bus interfaces
		if tmpFileLines[line].find("BUS_INTERFACE")>=0:
			elem=tmpFileLines[line].rstrip().split(" ")
			elem = [e.strip(",") for e in elem]
			stdIndex = elem.index("BUS_STD") + 2
			nameIndex = elem.index("BUS") + 2
			typeIndex = elem.index("BUS_TYPE") +2
			tempInstance.businterfaces.append(BusInterface(elem[nameIndex],elem[stdIndex],elem[typeIndex],""))
	for line in range(0,len(tmpFileLines)): # fetch ports which do not belong to a bus
		if tmpFileLines[line].find("PORT")>=0 and tmpFileLines[line].find("BUS")<0:
			elem = tmpFileLines[line].rstrip().split(' ')
			elem = [e.strip(",").strip("\t\t=") for e in elem]
			#SIGIS and DIR attributes might not be present
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

############### Global ports import
#given an XML node (port to be instanciated) and a list of global ports
#instanciate the global port, fill in the information about it and append the newly instanciated global port to the list

def importGlobalPort(node, globalports):

	ide = node.getAttribute("id")
	print ide+"\n"
	tempInstance = GlobalPort(ide,"",list())
	print tempInstance.name
	if node.attributes:
		for a in range(0,len(node.attributes)):
			if node.attributes.item(a).name != "id":
				name = node.attributes.item(a).name
				#print name
				value = node.attributes.item(a).value
				#print value
				tempInstance.attributes.append(Attribute(name, value))

	for a in tempInstance.attributes:
		print a.value+" "+a.name
	print "finish\n"
	
	# insert the instance into the global port list
	globalports.append(copy.deepcopy(tempInstance))

############### Interconnections
#given an XML node (link to be instanciated). Link can be physical or virtual
#instanciate the link



def connect(link, components, globalports):

	global count

	src = link.getAttribute("src")
	tgt = link.getAttribute("tgt")

	srcInstance=0
	tgtInstance=0

	src_isGlobalPort=0
	tgt_isGlobalPort=0

	for c in components:
		if c.instance == src: srcInstance = c 
		elif c.instance == tgt: tgtInstance = c
		
	for p in globalports:
		if p.name == src: 
			srcInstance = p
			src_isGlobalPort = 1
		elif p.name == tgt:
			tgtInstance = p
			tgt_isGlobalPort = 1
	
	for l in link.childNodes:
		if l.nodeType==1 and l.tagName=="srcint":
			srcInterfaceName=l.getAttribute("id")
	for l in link.childNodes:
		if l.nodeType==1 and l.tagName=="tgtint":
			tgtInterfaceName=l.getAttribute("id")
	
	if srcInstance==0 or tgtInstance==0:
		print "ERROR LINKS CONTAINS A COMPONENT INSTANCE or PORT NOT FOUND"
		sys.exit()

	
	if src_isGlobalPort and not tgt_isGlobalPort: 
		# usual connection global port to device
		# not consider the case that the device is a bus

		print "Source is a Global Port, Target is a Component intance"
		print srcInstance.name+" on "+srcInterfaceName
		print tgtInstance.instance+" on "+tgtInterfaceName

		# fetch the interface in the component with that name, being it a bus or a port
		# contained in tgtInterface
		found = 0
		for i in tgtInstance.businterfaces:
			if i.name == tgtInterfaceName:
				found = 1
				tgtInterface = i
		
		if not found:
			for i in tgtInstance.ports:
				if i.name == tgtInterfaceName:
					found = 1
					tgtInterface = i

		assert found == 1

		assert srcInterfaceName == "self"
				
		# assign the name to both
		if srcInstance.value=="" and tgtInterface.value=="": #assign a new name
			srcInstance.value = "ext_port_conn_"+str(count)
			tgtInterface.value = "ext_port_conn_"+str(count)
			count+=1
		elif srcInstance.value=="" and tgtInterface.value!="": #copy to the other one
			srcInstance.value=tgtInterface.value
		elif srcInstance.value!="" and tgtInterface.value=="": #copy to the other one
			tgtInterface.value=srcInstance.value
		elif srcInstance.value!="" and tgtInterface.value!="" and srcInstance.value==tgtInterface.value:
			print "WARNING: LINK ALREADY PRESENT, LIKELY SPECIFIED TWICE IN THE XML" ## ok anyway, already matching
		else: 
			print "ERROR: the two interfaces are already assigned to different components"
			sys.exit()
			

	elif not src_isGlobalPort and not tgt_isGlobalPort:
		# device to device connection, either bus or port
		# device might be a bus device e.g. plb, need to check bus attribute of the device instance
		# srcInstance and srcInterface
		print ""
		print "-------"
		print "device to device connection"
		print srcInstance.instance+" on "+srcInterfaceName
		print tgtInstance.instance+" on "+tgtInterfaceName
		found = 0

		src_isBus = 0
		tgt_isBus = 0

		src_isBusDevice = 0
		tgt_isBusDevice = 0

		# discover if the source is a bus device, otherwise get the interface, either bus or port
		if srcInstance.bus=="":
			for i in srcInstance.businterfaces:
				if i.name == srcInterfaceName:
					found = 1
					srcInterface = i
					src_isBus = 1				
		
			if not found:
				for i in srcInstance.ports:
					if i.name == srcInterfaceName:
						found = 1
						srcInterface = i
		else:
			src_isBusDevice = 1
			found = 1

		assert found==1

		found = 0

		# discover if the target is a bus device, otherwise get the interface, either bus or port
		if tgtInstance.bus=="":
			for i in tgtInstance.businterfaces:
				if i.name == tgtInterfaceName:
					found = 1
					tgtInterface = i
					tgt_isBus = 1
		
			if not found:
				for i in tgtInstance.ports:
					if i.name == tgtInterfaceName:
						found = 1
						tgtInterface = i
		else:
			tgt_isBusDevice = 1
			found=1

		assert found==1

		assert not src_isBusDevice or not tgt_isBusDevice

		if src_isBusDevice: #device to bus connection
			# assign the target interface to the bus instance
			print "device to bus connection"
			assert (tgtInterface.value=="" or tgtInterface==srcInstance.instance) and tgtInterface.std==srcInstance.bus
			tgtInterface.value = srcInstance.instance

		elif tgt_isBusDevice: #device to bus connection
			# assign the target interface to the bus instance
			print "device to bus connection"
			assert (srcInterface.value==""  or srcInterface==tgtInstance.instance) and srcInterface.std==tgtInstance.bus
			srcInterface.value = tgtInstance.instance	

		elif src_isBus and tgt_isBus:  #point-to-point bus connection
			print "point to point bus connection"
			assert srcInterface.std == tgtInterface.std
			assert (srcInterface.type=="INITIATOR" and tgtInterface.type=="TARGET") or \
			(srcInterface.type=="TARGET" and tgtInterface.type=="INITIATOR")
			srcInterface.value="pp_bus_conn_"+str(count)
			tgtInterface.value="pp_bus_conn_"+str(count)
			count+=1
			
		elif not src_isBus and not tgt_isBus: #port to port connection
			# beware of the interrupt manager that enables &-ing of the signals

			print "port to port connection"
			print srcInterface.value
			print tgtInterface.value
			assert srcInterface.sigis==tgtInterface.sigis
			
			if srcInterface.value=="" and tgtInterface.value=="":
				srcInterface.value="pp_port_conn_"+str(count)
				tgtInterface.value="pp_port_conn_"+str(count)
				print "both assigned to "+srcInterface.value
			elif srcInterface.value=="" and tgtInterface.value!="":
				#what if it is an interrupt and int needs to be &-ed?
				#srcInterface.value=tgtInterface.value
				print "destination interface name already assigned"
				if tgtInterface.sigis=="INTERRUPT" and srcInterface.sigis=="INTERRUPT":
					print "\tbut it is an interrupt, therefore compound"
					srcInterface.value="interrupt_conn_"+str(count)
					tgtInterface.value=tgtInterface.value+"&interrupt_conn_"+str(count)
				else: srcInterface.value=tgtInterface.value
			elif srcInterface.value!="" and tgtInterface.value=="":
				print "destination source name already assigned"
				tgtInterface.value=srcInterface.value
			elif srcInterface.value!="" and tgtInterface.value!="" and (srcInterface.value==tgtInterface.value):
				print "WARNING: LINK ALREADY PRESENT, LIKELY SPECIFIED TWICE IN THE XML"
			else:
				print "ERROR: the two interfaces are already assigned to different components"
				sys.exit()
			count+=1
		
		else:
			print "ERROR: trying to connect two components from bus to port or vice versa"
			print "Source: "+srcInstance.instance+" on: "+srcInterface.name
			print "Target: "+tgtInstance.instance+" on: "+tgtInterface.name
			sys.exit()
			
		print "-------------------"

	"""	
	else: 
		print "Source is a component instance"
		print srcInstance.instance+" on "+srcInterface
		
	if tgt_isPort: 
		print "Target is a Global Port"
		print tgtInstance.name+" on "+tgtInterface
	else:
		print "Target is a component instance"
		print tgtInstance.instance+" on "+tgtInterface

	"""

	



###### Check not only slaves on the buses?

#############################################################



############### Components import

for node in systemNode.childNodes:
	if node.nodeType == 1:
		importComponent(node, components)

###############

############### Pinout import

for node in pinoutNode.childNodes:
	if node.nodeType == 1:
		importGlobalPort(node, globalports)



############### Interconnects connection

count = 0
for node in physicalNode.childNodes:
	if node.nodeType == 1 and node.tagName == "link":
		connect(node, components, globalports)
for node in virtualNode.childNodes:
	if node.nodeType == 1 and node.tagName == "link":
		connect(node, components, globalports)


######### Print out all the database in mhs syntax
def printall():
	f = open(mhsoutput,'w')
	print "\nIMPORTED ARCH PRINTED ON "+mhsoutput+"\n"
	f.write("################\n")
	f.write("# Automatically generated by archgen, Polimi HPPS project 2012\n")
	f.write("# Author: Marco Zavatta (marco.zavatta@mail.polimi.it)\n")
	f.write("# "+str(datetime.date.today())+"\n")
	f.write("# Generated from "+xmlinput+"\n")
	f.write("################\n\n")

	for item1 in globalports:
			f.write("PORT "+item1.name+" = "+item1.value)
			for item2 in item1.attributes:
				f.write(", "+item2.name+" = "+item2.value)
			f.write("\n")
	f.write("\n")

	for item1 in components:
			#print "\n"
			f.write("BEGIN "+item1.cls+"\n")
			f.write("PARAMETER INSTANCE "+item1.instance+"\n")
			f.write("BUS "+item1.bus+"\n")
			for item2 in item1.parameters:
				f.write("PARAMETER "+item2.name+" "+item2.value+"\n")
			for item3 in item1.ports:
				f.write("PORT "+item3.name+" "+item3.value+" "+item3.sigis+" "+item3.dir+"\n")
			for item4 in item1.businterfaces:
				f.write("BUS_INTERFACE "+item4.name+" "+item4.value+" "+item4.std+" "+item4.type+"\n")
			f.write("END"+"\n")
			f.write("\n")

	sys.exit()
###########

######### Print out the final mhs file
def printmhs():
	f = open(mhsoutput,'w')
	print "\nIMPORTED ARCH PRINTED ON "+mhsoutput
	f.write("################\n")
	f.write("# Automatically generated by archgen, Polimi HPPS project 2012\n")
	f.write("# Author: Marco Zavatta (marco.zavatta@mail.polimi.it)\n")
	f.write("# "+str(datetime.date.today())+"\n")
	f.write("# Generated from "+xmlinput+"\n")
	f.write("################\n\n")

	for item1 in globalports:
			f.write("PORT "+item1.name+" = "+item1.value)
			for item2 in item1.attributes:
				f.write(", "+item2.name+" = "+item2.value)
			f.write("\n")
	f.write("\n")

	for item1 in components:
			#print "\n"
			f.write("BEGIN "+item1.cls+"\n")
			f.write("PARAMETER INSTANCE = "+item1.instance+"\n")
			#f.write("BUS "+item1.bus+"\n")
			for item2 in item1.parameters:
				if item2.value!="":
					f.write("PARAMETER "+item2.name+" = "+item2.value+"\n")
			for item3 in item1.ports:
				if item3.value!="":
					f.write("PORT "+item3.name+" = "+item3.value+"\n")
			for item4 in item1.businterfaces:
				if item4.value!="":
					f.write("BUS_INTERFACE "+item4.name+" = "+item4.value+"\n")
			f.write("END"+"\n")
			f.write("\n")

	sys.exit()
###########

printmhs()
"""
print "\nIMPORTED ARCH"
for item1 in components:
	print "BEGIN "+item1.cls
	print "PARAMETER INSTANCE "+item1.instance
	print "BUS "+item1.bus
	#if item1.cls=="microblaze":
	for item2 in item1.parameters:
		print "PARAMETER "+item2.name+" "+item2.value
	for item3 in item1.ports:
		print "PORT "+item3.name+" "+item3.value
	for item4 in item1.businterfaces:
		print "BUS_INTERFACE "+item4.name+" "+item4.value+" "+item4.std+" "+item4.type
	print "END"
"""




################################################ Interconnect generation ##################################################
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




	












"""
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
"""
	
