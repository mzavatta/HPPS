#! /usr/bin/python
"""
Author: Marco Zavatta
Date: July 2012
Xilinx EDK files generation from a custom XML specification
"""

########## Imports
import sys
import os
import subprocess
import xml.dom
import copy
import time
import datetime
from xml.dom.minidom import parseString

########### Global parameters
psfversion = "2.1.0"	# Platform Specification Format version (PSF)
edkversionLong = "12.1 Build EDK_MS1.53d"	# EDK version verbose
edkversionShort = "12.1"			# EDK version short

########### Output files definitions
mhsoutput = "restemp.mhs"
mssoutput = "restemp.mss"
xmpoutput = "restemp.xmp"
logoutput = "psgen_log.txt"

########### Input files definitions
xmlinput = "architecture_custom.xml"
mhsdefaultsFile = "./mhsdefaults"
mssdefaultsFile = "./mssdefaults"
xmpdefaultsFile = "./xmpdefaults"
# beware of .mpd input files explicited in component classes definitions
hwIPbasepath = "/home/hwdesign"
customIPbasepath = "/home/hwdesign/archgen"

########### Classes definitions
class ComponentClass:
	def __init__(self,className,mpdPath):
		self.className=className # e.g. xps_mailbox
		self.mpdPath=mpdPath




class GlobalPort:
	def __init__(self,name,value,attributes):
		self.name=name			# external name
		self.attributes=attributes	# attribute list of class Attribute
		self.value=value		# internal name, used for internal connections

class Attribute:	# as a list belonging to GlobalPort e.g. DIR = I, SIGIS = CLK, CLK_FREQ = 100000000 ...
	def __init__(self,name,value):
		self.name=name		# e.g. SIGIS
		self.value=value	# e.g. CLK




class Component:
	bus = ""	# will be filled if the component itself is a bus, e.g. if it is a plb_v46 or lmb_v10
	def __init__(self,cls,instance,parameters,ports,businterfaces):
		self.cls=cls		# e.g. xps_mailbox
		self.instance=instance	# instance should be into the parameters list but it is kept outside for convenience
					# as it is often a search objective
		self.parameters=parameters	# parameter list of class Parameter
		self.ports=ports		# port list of class Port
		self.businterfaces=businterfaces	# bus interfaces list of class BusInterface

class Parameter:
	def __init__(self,name,value):
		self.name=name		# e.g. C_SPLB0_BASEADDR
		self.value=value	# e.g. 0x81e00000

class Port:
	def __init__(self,name,sigis,dir,value):
		self.name=name		# e.g. PLB_Clk
		self.sigis=sigis	# e.g. CLK, INTERRUPT, RST
		self.dir=dir		# e.g. I, O
		self.value=value	# assignment name in the internal interconnection

class BusInterface:
	def __init__(self,name,std,type,value):
		self.name=name		# e.g. SPLB
		self.std=std 		# e.g. PLBV46, XIL_BRAM...
		self.type=type		# e.g. SLAVE, TARGET, INITIATOR...
		self.value=value 	# assignment name in the internal interconnection





class DriverAssignment: # associates a component class (or, optionally, a single instance) to a particular driver configuration
	text = ""	# driver configuration
	def __init__(self,componentClass,componentInstance):
		self.componentClass=componentClass		# must not be empty
		self.componentInstance=componentInstance 	# may be empty

class OsAssignment: # associates a processor class (or, optionally, a single instance) to a particular OS configuration
	text = ""	# OS configuration
	def __init__(self,componentClass,componentInstance):
		self.componentClass=componentClass		# must not be empty
		self.componentInstance=componentInstance	# may be empty

class MssProcessorDeclaration: # associates a proc class (or, optionally, a single instance) to a particular processor sw build configuration
	text = ""	# processor sw build configuration
	def __init__(self,componentClass,componentInstance):
		self.componentClass=componentClass		# must not be empty
		self.componentInstance=componentInstance	# may be empty


class SwProj:
	def __init__(self,name,proc,linkerscript,sources,headers,includepaths):
		self.name = name
		self.proc = proc
		self.linkerscript = linkerscript		
		self.sources = sources
		self.headers = headers
		self.includepaths = includepaths
		


########### Component classes instanciation
xps_mailbox = ComponentClass("xps_mailbox",hwIPbasepath+"/hw/XilinxProcessorIPLib/pcores/xps_mailbox_v2_00_b/data/xps_mailbox_v2_1_0.mpd")
plb_v46 = ComponentClass("plb_v46",hwIPbasepath+"/hw/XilinxProcessorIPLib/pcores/plb_v46_v1_04_a/data/plb_v46_v2_1_0.mpd")
microblaze = ComponentClass("microblaze",hwIPbasepath+"/hw/XilinxProcessorIPLib/pcores/microblaze_v7_30_a/data/microblaze_v2_1_0.mpd")
bram_block = ComponentClass("bram_block",hwIPbasepath+"/hw/XilinxProcessorIPLib/pcores/bram_block_v1_00_a/data/bram_block_v2_1_0.mpd")
lmb_v10 = ComponentClass("lmb_v10",hwIPbasepath+"/hw/XilinxProcessorIPLib/pcores/lmb_v10_v1_00_a/data/lmb_v10_v2_1_0.mpd")
lmb_bram_if_cntlr = ComponentClass("lmb_bram_if_cntlr",hwIPbasepath+"/hw/XilinxProcessorIPLib/pcores/lmb_bram_if_cntlr_v2_10_b/data/lmb_bram_if_cntlr_v2_1_0.mpd")
mpmc = ComponentClass("mpmc",hwIPbasepath+"/hw/XilinxProcessorIPLib/pcores/mpmc_v6_00_a/data/mpmc_v2_1_0.mpd")
xps_intc = ComponentClass("xps_intc",hwIPbasepath+"/hw/XilinxProcessorIPLib/pcores/xps_intc_v2_01_a/data/xps_intc_v2_1_0.mpd")
mdm = ComponentClass("mdm",hwIPbasepath+"/hw/XilinxProcessorIPLib/pcores/mdm_v1_00_g/data/mdm_v2_1_0.mpd")
npi_coreE = ComponentClass("npi_coreE",customIPbasepath+"/pcores/npi_coreE_v1_00_a/data/npi_coreE_v2_1_0.mpd")
npi_coreD = ComponentClass("npi_coreD",customIPbasepath+"/pcores/npi_coreD_v1_00_a/data/npi_coreD_v2_1_0.mpd")
npi_coreA = ComponentClass("npi_coreA",customIPbasepath+"/pcores/npi_coreA_v1_00_a/data/npi_coreA_v2_1_0.mpd")
npi_coreC = ComponentClass("npi_coreC",customIPbasepath+"/pcores/npi_coreC_v1_00_a/data/npi_coreC_v2_1_0.mpd")
proc_sys_reset = ComponentClass("proc_sys_reset",hwIPbasepath+"/hw/XilinxProcessorIPLib/pcores/proc_sys_reset_v2_00_a/data/proc_sys_reset_v2_1_0.mpd")
clock_generator = ComponentClass("clock_generator",hwIPbasepath+"/hw/XilinxProcessorIPLib/pcores/clock_generator_v4_00_a/data/clock_generator_v2_1_0.mpd")

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


########## File handles
mhsoutputHandle = open(mhsoutput,'w')
mssoutputHandle = open(mssoutput,'w')
xmpoutputHandle = open(xmpoutput,'w')
mhsdefaultsLinesHandle = open(mhsdefaultsFile,'r').readlines()
mssdefaultsLinesHandle = open(mssdefaultsFile,'r').readlines()
xmpdefaultsLinesHandle = open(xmpdefaultsFile,'r').readlines()
archFileHandle = open(xmlinput,'r')
logoutputHandle = open(logoutput,'w')


########## Initialization of the system components lists
components=list()	# HW system, root
globalports=list()	# "
driverassignments=list()		# SW system, dependent on HW system
osassignments=list()			# "
mssprocessordeclarations=list()		# "

swprojs=list()

########## Project and system generics
systemId = ""
fpgaArchitecture = ""
fpgaDevice = ""
fpgaPackage = ""
ucfFile = "data/system.ucf"

########## XML parsing and tree search
dom = parseString(archFileHandle.read())
archFileHandle.close()

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

for node in dom.documentElement.childNodes:
	if node.nodeType == 1 and node.tagName=="applications":
		applicationsNode = node


########## XOR helper
def xor(op1, op2):
    return bool(op1) ^ bool(op2)

########## Warnings list
warnings = ""

########## Error helper
error = False
def exit():
	if error:
		print "psgen interrupted by error, see log file "+logoutput+" for details"
	else: print "psgen successfully terminated, log file "+logoutput
	sys.exit()


########## Import system and device data
def importgenerics():
	
	global fpgaArchitecture, fpgaDevice, fpgaPackage, systemId
	global error

	systemId = systemNode.getAttribute("id")
	temp = systemNode.getAttribute("device")
	elem = temp.rstrip().split("-")
	if len(elem)!=2:
		error = True
		logoutputHandle.write("UNKNOWN DEVICE CODE, CHECK XML's SYSTEM NODE ATTRIBUTES FOR MISSING "+'"-"'+"\n")
		print "UNKNOWN DEVICE CODE, CHECK XML's SYSTEM NODE ATTRIBUTES FOR MISSING "+'"-"'
		exit()


	symbols = list(elem[0])
	if symbols[3]=="v" or symbols[3]=="V":
		fpgaArchitecture = "virtex"
	elif symbols[3]=="k" or symbols[3]=="K":
		fpgaArchitecture = "kintex"
	elif symbols[3]=="a" or symbols[3]=="A":
		fpgaArchitecture = "artix"
	elif symbols[3]=="s" or symbols[3]=="S":
		fpgaArchitecture = "spartan"
	else:
		error = True
		logoutputHandle.write("UNKNOWN DEVICE CODE, CHECK XML's SYSTEM NODE ATTRIBUTES FOR ERRORS\n")
		print "UNKNOWN DEVICE CODE, CHECK XML's SYSTEM NODE ATTRIBUTES FOR ERRORS"
		exit()

	fpgaArchitecture+=symbols[2]
	fpgaDevice = elem[0]
	fpgaPackage = elem[1]

	

############### Component Import from xml, mpspecs, mpd
# given and XML node (component to be instanciated) and a list of components
# instanciate the component, fill in the information about it and append the newly instanciated component to the list
def importComponent(node, components):
	
	global warnings

	
	logoutputHandle.write("importComponent entered\n")
	# instanciate based on xml
	id = node.getAttribute("id")
	cls = node.getAttribute("class")
	tempInstance = Component(cls,id,list(),list(),list())
	logoutputHandle.write("current xml node is id:"+id+" class:"+cls+"\n")
	
	####### TO BE CHANGED GOING INTO THE mpd ######
	if cls=="plb_v46":
		tempInstance.bus = "PLBV46"
	elif cls=="lmb_v10":
		tempInstance.bus = "LMB"
	
	#fetch default parameters in mpspecs
	valid = 0
	for l in range(0,len(mhsdefaultsLinesHandle)):
		elem = mhsdefaultsLinesHandle[l].rstrip().split(" ")
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
		if tmpFileLines[line].find("PORT")>=0 and tmpFileLines[line].find("BUS =")<0:
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

	global error

	logoutputHandle.write("importGlobalPort entered\n")
	
	ide = node.getAttribute("id")
	logoutputHandle.write(ide+"\n")
	tempInstance = GlobalPort(ide,"",list())
	logoutputHandle.write(tempInstance.name+"\n")
	if node.attributes:
		for a in range(0,len(node.attributes)):
			if node.attributes.item(a).name != "id":
				name = node.attributes.item(a).name.upper()
				#print name
				value = node.attributes.item(a).value
				#print value
				tempInstance.attributes.append(Attribute(name, value))

	for a in tempInstance.attributes:
		logoutputHandle.write(a.value+" "+a.name+"\n")
	#print "finish\n"
	
	# insert the instance into the global port list
	globalports.append(copy.deepcopy(tempInstance))


############### Interconnections
#given an XML node (link to be instanciated). Link can be physical or virtual
#instanciate the link
def connect(link, components, globalports):

	global count
	global warnings
	global error

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
		error = True
		logoutputHandle.write("----\nERROR LINKS CONTAINS A COMPONENT INSTANCE or GLOBAL PORT NOT FOUND.\n")
		logoutputHandle.write("Check the xml for mistaken naming or components not defined.\nLink says:\n")
		logoutputHandle.write("\t"+src+" on "+srcInterfaceName+"\n"+"\t"+tgt+" on "+tgtInterfaceName+"\n----\n")
		print "----"
		print "ERROR LINKS CONTAINS A COMPONENT INSTANCE or GLOBAL PORT NOT FOUND."
		print "Check the xml for mistaken naming or components not defined."
		print "Link says:"
		print "\t"+src+" on "+srcInterfaceName
		print "\t"+tgt+" on "+tgtInterfaceName
		print "----"
		exit()
	
	# can have many cases now:
	# - source is a global port, destination is a component
	# - destination is a component, source is a global port
	# - component to component connection
		
	if src_isGlobalPort and not tgt_isGlobalPort: 
		# usual connection global port to device
		# not consider the case that the device is a bus

		logoutputHandle.write("Source is a Global Port, Target is a Component intance\n")
		logoutputHandle.write(srcInstance.name+" on "+srcInterfaceName+"\n"+tgtInstance.instance+" on "+tgtInterfaceName+"\n")

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

		assert srcInterfaceName == "self" or srcInterfaceName == ""
				
		# assign the name to both
		# temporary guard for debugging
		if tgtInstance.cls == "mpmc":
			srcInstance.value = srcInstance.name
			tgtInterface.value = srcInstance.value
		elif srcInstance.value=="" and tgtInterface.value=="": #assign a new name
			srcInstance.value = "ext_port_conn_"+str(count)
			tgtInterface.value = "ext_port_conn_"+str(count)
			count+=1
		elif srcInstance.value=="" and tgtInterface.value!="": #copy to the other one
			srcInstance.value=tgtInterface.value
		elif srcInstance.value!="" and tgtInterface.value=="": #copy to the other one
			tgtInterface.value=srcInstance.value
		elif srcInstance.value!="" and tgtInterface.value!="" and srcInstance.value==tgtInterface.value:
			warnings+="WARNING: LINK LIKELY SPECIFIED TWICE IN THE XML" ## ok anyway, already matching
		else: 
			error = True
			logoutputHandle.write("ERROR: the two interfaces are already assigned to different components\n")
			print "ERROR: the two interfaces are already assigned to different components"
			exit()
	
	elif not src_isGlobalPort and tgt_isGlobalPort:
		# usual connection device to global port
		# not consider the case that the device is a bus

		logoutputHandle.write("Source is a Component intance, Target is a Global Port\n")
		logoutputHandle.write(srcInstance.name+" on "+srcInterfaceName+"\n"+tgtInstance.instance+" on "+tgtInterfaceName+"\n")

		# fetch the interface in the component with that name, being it a bus or a port
		# contained in tgtInterface
		found = 0
		for i in srcInstance.businterfaces:
			if i.name == srcInterfaceName:
				found = 1
				srcInterface = i
		
		if not found:
			for i in srcInstance.ports:
				if i.name == srcInterfaceName:
					found = 1
					srcInterface = i
		assert found == 1

		assert tgtInterfaceName == "self" or tgtInterfaceName == ""
				
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
			warnings+="WARNING: LINK LIKELY SPECIFIED TWICE IN THE XML\n" ## ok anyway, already matching
		else: 
			error = True
			logoutputHandle.write("ERROR: the two interfaces are already assigned to different components\n")
			print "ERROR: the two interfaces are already assigned to different components"
			exit()
		
		

	elif not src_isGlobalPort and not tgt_isGlobalPort:
		# device to device connection, either bus or port
		# device might be a bus device e.g. plb, need to check bus attribute of the device instance
		
		logoutputHandle.write("\n-------\n")
		logoutputHandle.write("device to device connection")
		logoutputHandle.write(srcInstance.instance+" on "+srcInterfaceName+"\n")
		logoutputHandle.write(tgtInstance.instance+" on "+tgtInterfaceName+"\n")
		found = 0

		# whether it is a bus device
		src_isBusDevice = 0
		tgt_isBusDevice = 0

		# whether it is a bus interface within a normal (non-bus) device
		src_isBus = 0
		tgt_isBus = 0

		# discover if the source is a bus device
		if srcInstance.bus!="":
			src_isBusDevice = 1
			# get the source interface whose name is specified in the xml
			# though when the connection is towards the bus itself,
			# the interface name specified in the xml is be "" or "self"
			# so in that case it will not find it (see assert)
			if srcInterfaceName!="self" and srcInterfaceName!="":
				src_isBusDevice = 0	# redirect to a simple device to device case	

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
		assert found==1 or src_isBusDevice
					
		found = 0

		# discover if the target is a bus device
		if tgtInstance.bus!="":
			tgt_isBusDevice = 1
			# get the target interface whose name is specified in the xml
			# though when the connection is towards the bus itself,
			# the interface name specified in the xml is be "" or "self"
			# so in that case it will not find it (see assert)
			if tgtInterfaceName!="self" and tgtInterfaceName!="":
				tgt_isBusDevice = 0  # redirect to a simple device to device case

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
		assert found==1 or tgt_isBusDevice


		# (optional) ensure we're not connecting a bus with a bus directly
		# assert not src_isBusDevice or not tgt_isBusDevice

		# can have many cases now:
		# - source is a normal component, destination is a bus component's bus
		# - vice versa (in both cases the connection name must be the same as the instance name of the bus)
		# - point to point bus connection (i.e. when there is no bus component that intermediates e.g. NPI)
		# - port to port connection
		# (in the last two cases the same connection name must be assigned to both bus interfaces or ports)

		if src_isBusDevice: #device to bus connection
			# assign the target interface to the bus instance
			# depending on whether the target is actually the bus or a port of the bus
			logoutputHandle.write("bus to device connection\n")
			assert (tgtInterface.value=="" or tgtInterface==srcInstance.instance) and tgtInterface.std==srcInstance.bus
			tgtInterface.value = srcInstance.instance
			logoutputHandle.write("assigned to "+tgtInterface.value+"\n")	
			
		elif tgt_isBusDevice: #device to bus connection
			# assign the target interface to the bus instance
			# depending on whether the target is actually the bus or a port of the bus
			logoutputHandle.write("device to bus connection\n")
			assert (srcInterface.value==""  or srcInterface==tgtInstance.instance) and srcInterface.std==tgtInstance.bus
			srcInterface.value = tgtInstance.instance
			logoutputHandle.write("assigned to "+srcInterface.value+"\n")

		elif src_isBus and tgt_isBus:  #point-to-point bus connection
			logoutputHandle.write("point to point bus connection\n")
			assert srcInterface.std == tgtInterface.std
			assert (srcInterface.type=="INITIATOR" and tgtInterface.type=="TARGET") or \
			(srcInterface.type=="TARGET" and tgtInterface.type=="INITIATOR")

			# what about already assigned names? for the moment guard in this way
			assert srcInterface.value=="" and tgtInterface.value==""

			srcInterface.value="pp_bus_conn_"+str(count)
			tgtInterface.value="pp_bus_conn_"+str(count)
			logoutputHandle.write("assigned to "+srcInterface.value+"\n")
			count+=1
			
		elif not src_isBus and not tgt_isBus: #port to port connection
			# beware of the interrupt manager that enables &-ing of the signals
			# it ends up in here also the case where one of the two devices is a bus device \
			# and the connection on the bus device in on a port (e.g. plb_v46's clock port)

			logoutputHandle.write("port to port connection\n")
			logoutputHandle.write("sigis: "+srcInterface.sigis+"\n")
			logoutputHandle.write("sigis: "+tgtInterface.sigis+"\n")

			assert (srcInterface.sigis==tgtInterface.sigis) or srcInterface.sigis=="" or tgtInterface.sigis==""
			
			# on either port a name might have already been assigned (a previously assigned connection on the same port \
			# on one side and a different port on the other side). Need to take care of this
			if srcInterface.value=="" and tgtInterface.value=="":
				srcInterface.value="pp_port_conn_"+str(count)
				tgtInterface.value="pp_port_conn_"+str(count)
				logoutputHandle.write("both assigned to "+srcInterface.value+"\n")
			elif srcInterface.value=="" and tgtInterface.value!="":
				#what if it is an interrupt and int needs to be &-ed?
				#srcInterface.value=tgtInterface.value
				logoutputHandle.write("destination interface name already assigned to "+tgtInterface.value+"\n")
				if tgtInterface.sigis=="INTERRUPT" and srcInterface.sigis=="INTERRUPT":
					logoutputHandle.write("\tbut it is an interrupt, therefore compound\n")
					srcInterface.value="interrupt_conn_"+str(count)
					tgtInterface.value=tgtInterface.value+"&interrupt_conn_"+str(count)
				else: srcInterface.value=tgtInterface.value
			elif srcInterface.value!="" and tgtInterface.value=="":
				logoutputHandle.write("source interface name already assigned to "+srcInterface.value+"\n")
				tgtInterface.value=srcInterface.value
			elif srcInterface.value!="" and tgtInterface.value!="" and srcInterface.value==tgtInterface.value:
				warnings+="WARNING: LINK ALREADY PRESENT "+src+":"+srcInterfaceName+" " \
					+tgt+":"+tgtInterfaceName+" LIKELY SPECIFIED TWICE IN THE XML"
			else:
				error = True
				logoutputHandle.write("ERROR: the two interfaces are already assigned to different components\n")
				logoutputHandle.write("       cannot assign this link without breaking another one\n")
				print "ERROR: the two interfaces are already assigned to different components"
				print "       cannot assign this link without breaking another one"
				exit()
			count+=1
		
		else:
			error = True
			logoutputHandle.write("ERROR: trying to connect two components from bus to port or vice versa. Incriminated link:\n")
			logoutputHandle.write("Source: "+srcInstance.instance+" on: "+srcInterface.name+"\n")
			logoutputHandle.write("Target: "+tgtInstance.instance+" on: "+tgtInterface.name+"\n")
			print "ERROR: trying to connect two components from bus to port or vice versa. Incriminated link:"
			print "Source: "+srcInstance.instance+" on: "+srcInterface.name
			print "Target: "+tgtInstance.instance+" on: "+tgtInterface.name
			exit()
			
		logoutputHandle.write("----------------\n")



###### Check not only slaves on the buses?
#############################################################


def importmssdefaults():
		
		global error

		logoutputHandle.write("importsmssdefaults entered")
		print "importmssdefaults entered"

		valid = 0
		for l in range(0,len(mssdefaultsLinesHandle)):
			elem = mssdefaultsLinesHandle[l].rstrip().split(" ")
			if "BEGIN" in elem and valid == 0: # trigger valid =1 when begin of a block
				if "OS" in elem:
					valid = "O"
					# create tempinstance of class osassignment and assign to the instance the class name
					tempInstance = OsAssignment(elem[2],"")
				elif "PROCESSOR" in elem:
					valid = "P"
					# create tempinstance of class processor and assign to the instance the class name
					tempInstance = MssProcessorDeclaration(elem[2],"")
				elif "DRIVER" in elem:
					valid = "D"
					# create tempinstance of class driverassignment and assign to the instance the class name
					tempInstance = DriverAssignment(elem[2],"")
				else:
					error = True
					logoutputHandle.write("ERROR, UNKNOWN BEGIN STATEMENT IN "+mssdefaultsFile+"\n")
					print "ERROR, UNKNOWN BEGIN STATEMENT IN "+mssdefaultsFile
					exit()
			elif "PARAMETER" in elem and valid!=0: # if valid and if it is a parameter line, append a new parameter
				if valid == "O":
					if "PROC_INSTANCE" in elem:
						# assign instance name to the assignment
						tempInstance.componentInstance = elem[4]
					else:
						# just append text
						tempInstance.text = tempInstance.text+mssdefaultsLinesHandle[l] 

				if valid == "P":
					if "HW_INSTANCE" in elem:
						# assign instance name to the assignment
						tempInstance.componentInstance = elem[4]
					else:
						# just append text
						tempInstance.text = tempInstance.text+mssdefaultsLinesHandle[l] 

				if valid == "D":
					if "HW_INSTANCE" in elem:
						# assign instance name to the assignment
						tempInstance.componentInstance = elem[4]
					else:
						# just append text
						tempInstance.text = tempInstance.text+mssdefaultsLinesHandle[l] 


			elif "END" in elem and valid != 0:
				if valid == "O": osassignments.append(copy.deepcopy(tempInstance))
				if valid == "P": mssprocessordeclarations.append(copy.deepcopy(tempInstance))
				if valid == "D": driverassignments.append(copy.deepcopy(tempInstance))
				valid=0	# clear valid when END block is found

			

########## print mss. for each component in the HW print a driver or a os+processor pair
def printmss(components):
	
	logoutputHandle.write("printing mss...\n")
	print "printing mss..."

	logoutputHandle.write("mss file printed on "+mssoutput+"\n")
	print "mss file printed on "+mssoutput

	mssoutputHandle.write("################\n")
	mssoutputHandle.write("# Automatically generated by psgen, Polimi HPPS project 2012\n")
	mssoutputHandle.write("# Author: Marco Zavatta (marco.zavatta@mail.polimi.it)\n")
	mssoutputHandle.write("# Generated on "+str(datetime.date.today())+"\n")
	mssoutputHandle.write("# Generated from "+xmlinput+"\n")
	mssoutputHandle.write("# Platform Specification Format version "+psfversion+"\n")
	mssoutputHandle.write("# EDK version "+edkversionLong+"\n")
	mssoutputHandle.write("################\n\n")

	for component in components:
		cls = component.cls
		instance = component.instance
		tempInstance = 0
		#isbus = 0
		#if component.bus!="": isbus = 1
		customInstanceFound = 0
		genericInstanceFound = 0	
		
		if component.bus=="":
			if component.cls=="microblaze": # processor, which needs a PROCESSOR block + OS block
				for mp in mssprocessordeclarations:
					if mp.componentInstance == instance:
						tempInstance = mp
						customInstanceFound = 1
						break
				if not customInstanceFound:
					for mp in mssprocessordeclarations:
						if mp.componentClass == cls and mp.componentInstance=="":
							tempInstance = mp
							genericInstanceFound = 1

				assert xor(customInstanceFound, genericInstanceFound)
	
				mssoutputHandle.write("BEGIN PROCESSOR\n")
				mssoutputHandle.write(" PARAMETER HW_INSTANCE = "+instance+"\n")
				mssoutputHandle.write(tempInstance.text)
				mssoutputHandle.write("END\n")
				mssoutputHandle.write("\n")

				customInstanceFound = 0
				genericInstanceFound = 0

				for os in osassignments:
					if os.componentInstance == instance:
						tempInstance = os
						customInstanceFound = 1
						break
				if not customInstanceFound:
					for os in osassignments:
						if os.componentClass == cls and os.componentInstance=="":
							tempInstance = os
							genericInstanceFound = 1

				assert xor(customInstanceFound, genericInstanceFound)

				mssoutputHandle.write("BEGIN OS\n")
				mssoutputHandle.write(" PARAMETER PROC_INSTANCE = "+instance+"\n")
				mssoutputHandle.write(tempInstance.text)
				mssoutputHandle.write("END\n")
				mssoutputHandle.write("\n")
			
			else: # component which needs a simple driver
				for da in driverassignments:
					if da.componentInstance == instance:
						tempInstance = da
						customInstanceFound = 1
						break
				if not customInstanceFound:
					for da in driverassignments:
						if da.componentClass == cls and da.componentInstance=="":
							tempInstance = da
							genericInstanceFound = 1

				assert xor(customInstanceFound, genericInstanceFound)

				mssoutputHandle.write("BEGIN DRIVER\n")
				mssoutputHandle.write(" PARAMETER HW_INSTANCE = "+instance+"\n")
				mssoutputHandle.write(tempInstance.text)
				mssoutputHandle.write("END\n")
				mssoutputHandle.write("\n")

########## Import Software Projects

def importswproj(swprojs):
	
	global error
	
	for node in applicationsNode.childNodes:
		if node.nodeType == 1 and node.tagName=="application":
			
			name = node.getAttribute("name")

			# get processor and verifies that it esists
			procExists = False
			proc = node.getAttribute("proc")
			for c in components:
				if c.instance == proc: procExists = True
			assert procExists

			ls = node.getAttribute("linkerscript")
		
			tempSources = list()
			tempHeaders = list()
			tempIncludePaths = list()
			# get sources, headers, include paths
			for n in node.childNodes:
				if n.nodeType==1:
					if n.tagName=="source":
						tempSources.append(n.getAttribute("path"))
					elif n.tagName=="header":
						tempHeaders.append(n.getAttribute("path"))
					elif n.tagName=="path":
						tempIncludePaths.append(n.getAttribute("path"))
					else:
						error = True
						logoutputHandle.write("ERROR XML non identified tag. Error in application tag "+name+"\n")
						print "ERROR XML non identified tag. Error in application tag "+name
						exit()

			swprojs.append(SwProj(name,proc,ls,copy.deepcopy(tempSources),copy.deepcopy(tempHeaders), \
						copy.deepcopy(tempIncludePaths)))
					


########## Print xmp (xps project configuration)

def printxmp(swprojs):

	global xmpoutputHandle, error

	logoutputHandle.write("printing xmp..\n")
	logoutputHandle.write("\timporting defaults for processor..\n")
	print "printing xmp.."

	processorDefaultText = ""
	swprojDefaultText = ""
	processorFinalText = ""
	swprojFinalText = ""

	# make a copy of everything outside multiple-lines chunks
	# copy placeholders for processors and swprojs
	valid = 0
	for l in xmpdefaultsLinesHandle:
		if l.find("$begin:processor$")>=0:
			valid = 1
			xmpoutputHandle.write("$processors$\n")
		elif l.find("$begin:swproj$")>=0:
			valid = 1
			xmpoutputHandle.write("$swprojs$\n")
		elif l.find("$end:processor$")>=0 or l.find("$end:swproj$")>=0:
			valid = 0
		elif not valid:
			xmpoutputHandle.write(l)
		
	# memorize the default processors text
	valid = 0
	for l in xmpdefaultsLinesHandle:
		if l.find("$begin:processor$")>=0:
			if valid == 1:
				error = True
				logoutputHandle.write(xmpdefaultsFile+" syntax error\n")
				exit()	
			else: valid=1
		elif l.find("$end:processor$")>=0:
			if valid == 0:
				error = True
				logoutputHandle.write(xmpdefaultsFile+" syntax error\n")
				exit()	
			else: valid=0
		elif valid:
			processorDefaultText = processorDefaultText + l

	# memorize the default swproj text
	valid = 0
	for l in xmpdefaultsLinesHandle:
		if l.find("$begin:swproj$")>=0:
			if valid == 1:
				error = True
				logoutputHandle.write(xmpdefaultsFile+" syntax error\n")
				exit()	
			else: valid=1
		elif l.find("$end:swproj$")>=0:
			if valid == 0:
				error = True
				logoutputHandle.write(xmpdefaultsFile+" syntax error\n")
				exit()
			else: valid=0
		elif valid:
			swprojDefaultText = swprojDefaultText + l
	
	# for every processor, add the default lines
	for c in components:
		if c.cls == "microblaze":
			processorFinalText = processorFinalText+"Processor: "+c.instance+"\n"+processorDefaultText
	
	
	# for every sw project, add the default lines
	for s in swprojs:
		swprojFinalText+="SwProj: "+s.name+"\n"
		swprojFinalText+="Processor: "+s.proc+"\n"
		swprojFinalText+="Executable: "+s.name+"/executable.elf\n"
		swprojFinalText+="LinkerScript: "+s.linkerscript+"\n"
		for s1 in s.headers:
			swprojFinalText+="Header: "+s1+"\n"
		for s1 in s.sources:
			swprojFinalText+="Source: "+s1+"\n"
		for s1 in s.includepaths:
			swprojFinalText+="SearchIncl: "+s1+"\n"
		swprojFinalText+=swprojDefaultText
	
	logoutputHandle.write(swprojFinalText+"\n")
		
	xmpoutputHandle.close()
	xmppointerLines = open(xmpoutput).readlines()
	xmpoutputHandle = open(xmpoutput,'w')

	for l in xmppointerLines:
		if l.find("$versions$")>=0:
			xmpoutputHandle.write("XmpVersion: "+edkversionShort+"\n" \
						+"VerMgmt: "+edkversionShort+"\n")
		elif l.find("$psfiles$")>=0:
			xmpoutputHandle.write("MHS File: "+mhsoutput+"\n" \
						+"MSS File: "+mssoutput+"\n")
		elif l.find("$device$")>=0:
			xmpoutputHandle.write("Architecture: "+fpgaArchitecture+"\n" \
						+"Device: "+fpgaDevice+"\n" \
						+"Package: "+fpgaPackage+"\n")
		elif l.find("$ucf$")>=0:
			xmpoutputHandle.write("UcfFile: "+ucfFile+"\n")
		elif l.find("$processors$")>=0:
			xmpoutputHandle.write(processorFinalText)
		elif l.find("$swprojs$")>=0:
			xmpoutputHandle.write(swprojFinalText)
		else: xmpoutputHandle.write(l)
	

	# clean swprojs
	print "swprojects imported"
	logoutputHandle.write("swprojects imported\n")


########## Print out all the components database in mhs syntax
def printall():
	logoutputHandle.write("\nIMPORTED ARCH PRINTED ON "+mhsoutput+"\n")
	print "\nIMPORTED ARCH PRINTED ON "+mhsoutput+"\n"
	mhsoutputHandle.write("################\n")
	mhsoutputHandle.write("# Automatically generated by psgen, Polimi HPPS project 2012\n")
	mhsoutputHandle.write("# Author: Marco Zavatta (marco.zavatta@mail.polimi.it)\n")
	mhsoutputHandle.write("# Generated on "+str(datetime.date.today())+"\n")
	mhsoutputHandle.write("# Generated from "+xmlinput+"\n")
	mhsoutputHandle.write("# Platform Specification Format version "+psfversion+"\n")
	mhsoutputHandle.write("# EDK version "+edkversionLong+"\n")
	mhsoutputHandle.write("################\n\n")

	for item1 in globalports:
			mhsoutputHandle.write("PORT "+item1.name+" = "+item1.value)
			for item2 in item1.attributes:
				mhsoutputHandle.write(", "+item2.name+" = "+item2.value)
			mhsoutputHandle.write("\n")
	mhsoutputHandle.write("\n")

	for item1 in components:
			#print "\n"
			mhsoutputHandle.write("BEGIN "+item1.cls+"\n")
			mhsoutputHandle.write("PARAMETER INSTANCE "+item1.instance+"\n")
			mhsoutputHandle.write("BUS "+item1.bus+"\n")
			for item2 in item1.parameters:
				mhsoutputHandle.write("PARAMETER "+item2.name+" "+item2.value+"\n")
			for item3 in item1.ports:
				mhsoutputHandle.write("PORT "+item3.name+" "+item3.value+" "+item3.sigis+" "+item3.dir+"\n")
			for item4 in item1.businterfaces:
				mhsoutputHandle.write("BUS_INTERFACE "+item4.name+" "+item4.value+" "+item4.std+" "+item4.type+"\n")
			mhsoutputHandle.write("END"+"\n")
			mhsoutputHandle.write("\n")



########## Print out the final mhs file
def printmhs():
	logoutputHandle.write("\nIMPORTED ARCH PRINTED ON "+mhsoutput+"\n")
	print "\nIMPORTED ARCH PRINTED ON "+mhsoutput
	mhsoutputHandle.write("################\n")
	mhsoutputHandle.write("# Automatically generated by psgen, Polimi HPPS project 2012\n")
	mhsoutputHandle.write("# Author: Marco Zavatta (marco.zavatta@mail.polimi.it)\n")
	mhsoutputHandle.write("# Generated on "+str(datetime.date.today())+"\n")
	mhsoutputHandle.write("# Generated from "+xmlinput+"\n")
	mhsoutputHandle.write("# Platform Specification Format version "+psfversion+"\n")
	mhsoutputHandle.write("# EDK version "+edkversionLong+"\n")
	mhsoutputHandle.write("################\n\n")

	mhsoutputHandle.write("PARAMETER VERSION = "+psfversion+"\n")

	for item1 in globalports:
			mhsoutputHandle.write("PORT "+item1.name+" = "+item1.value)
			for item2 in item1.attributes:
				mhsoutputHandle.write(", "+item2.name+" = "+item2.value)
			mhsoutputHandle.write("\n")
	mhsoutputHandle.write("\n")

	for item1 in components:
			mhsoutputHandle.write("BEGIN "+item1.cls+"\n")
			mhsoutputHandle.write("PARAMETER INSTANCE = "+item1.instance+"\n")
			#mhsoutputHandle.write("BUS "+item1.bus+"\n")
			for item2 in item1.parameters:
				if item2.value!="":
					mhsoutputHandle.write("PARAMETER "+item2.name+" = "+item2.value+"\n")
			for item3 in item1.ports:
				if item3.value!="":
					mhsoutputHandle.write("PORT "+item3.name+" = "+item3.value+"\n")
			for item4 in item1.businterfaces:
				if item4.value!="":
					mhsoutputHandle.write("BUS_INTERFACE "+item4.name+" = "+item4.value+"\n")
			mhsoutputHandle.write("END"+"\n")
			mhsoutputHandle.write("\n")

	


########### Execution flow
## Import generic parameters like device code, project name etc..
importgenerics()

## Components import (for each component in the xml: fetch defaults (mhsdefaults) + fetch mpd information + instanciate)
for node in systemNode.childNodes:
	if node.nodeType == 1:
		importComponent(node, components)

## Global port import (for each global port in the xml instanciate one)
for node in pinoutNode.childNodes:
	if node.nodeType == 1:
		importGlobalPort(node, globalports)

## Interconnects connection (links from xml)
count = 0	# global variable needed for naming of interconnections
for node in physicalNode.childNodes:
	if node.nodeType == 1 and node.tagName == "link":
		connect(node, components, globalports)
for node in virtualNode.childNodes:
	if node.nodeType == 1 and node.tagName == "link":
		connect(node, components, globalports)

## SW (drivers) system defaults import (from mssdefaults)
importmssdefaults()

## Import applications to be assigned to the processors (for each application in xml instanciate one)
importswproj(swprojs)

## Print platform specification files
printmhs() # uses information in memory generated by importComponent() and importGlobalPort() and connect()
printmss(components)	# uses information in memory from importmssdefaults
printxmp(swprojs) # uses xmpdefaults and applications loaded by importswproj()

exit()
###########
