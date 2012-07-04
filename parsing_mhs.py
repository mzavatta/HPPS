#!/usr/bin/env python
import sys

input_mhs=sys.argv[1]
input_xml=sys.argv[2]

PR=["microblaze"]
PRt=["MICROBLAZE"]

CO=["plb_v46","lmb_v10"]
COt=["BUS_PLB","BUS"]

ST=["lmb_bram_if_cntlr","bram_block","mpmc","xps_spi"]
STt=["MEMORY_CONTROLLER","BRAM","TODEFINE","TODEFINE"]

IP=["xps_uartlite","xps_gpio","mdm","proc_sys_reset","xps_ethernetlite","xps_mailbox"]
IPt=["IP","IP","IP","IP","IP","IP"]

CL=["clock_generator"]
CLt=["CLOCK_GENERATOR"]

lines=list()
mhs=open(input_mhs)
edk=open(input_xml)

#lines=f.readlines()
edkLines=edk.readlines()
mhsLines=mhs.readlines()

fpgaFamily="";
fpgaDevice="";
fpgaPackage="";
fpgaSpeedGrade="";

curUnit="";

lines.append("<faster>")
lines.append("<architecture>")

for l in range(0,len(mhsLines)):
	mhsLines[l]=mhsLines[l].strip()

	if(mhsLines[l].find("# Family:")>=0):
		elem=mhsLines[l].split(" ");
		for i in range(2,len(elem)):
			if(elem[i]!=""):
				fpgaFamily=str(elem[i]);
				break;

	if(mhsLines[l].find("# Device:")>=0):
		elem=mhsLines[l].split(" ");
		for i in range(2,len(elem)):
			if(elem[i]!=""):
				fpgaDevice=str(elem[i]);
				break;

	if(mhsLines[l].find("# Package:")>=0):
		elem=mhsLines[l].split(" ");
		for i in range(2,len(elem)):
			if(elem[i]!=""):
				fpgaPackage=str(elem[i]);
				break;

	if(mhsLines[l].find("# Speed Grade:")>=0):
		elem=mhsLines[l].split(" ");
		for i in range(3,len(elem)):
			if(elem[i]!=""):
				fpgaSpeedGrade=str(elem[i]);
				lines.append("<system id=\"fpga_0\" friendly_name=\"fpga_0\">")
				break;

	if(mhsLines[l].find("BASEADDR")>=0):
		addr=list()
		elem=mhsLines[l].split(" ");
		tag=elem[1].split("_")
		if(len(tag)==3):
			name=tag[1]
		else:
			name=curName
		base=elem[3]

	if(mhsLines[l].find("HIGHADDR")>=0):
		elem=mhsLines[l].split(" ");
		tag=elem[1].split("_")
		if(len(tag)==3):
			name2=tag[1]
		else:
			name2=curName
		high=elem[3]		
		if(name==name2):
			addr.append(name)
			addr.append(base)
			addr.append(high)
			addressLines.append(addr)

	if(mhsLines[l].find("BEGIN")>=0):
		addressLines=list()
		supportLines=list()
		elem=mhsLines[l].split(" ");
		curUnit=elem[1];

	if(mhsLines[l].find("PARAMETER INSTANCE")>=0):
		elem=mhsLines[l].split(" ");
		curName=elem[3];
		if(PR.count(curUnit)>0):
			supportLines.append("<processingElement id=\""+curName+"\" type=\""+PRt[PR.index(curUnit)]+"\" name=\""+curName+"\">")
			supportLines.append("<interface>")
			supportLines.append("</interface>")
			supportLines.append("</processingElement>")
		if(CO.count(curUnit)>0):
			supportLines.append("<communication id=\""+curName+"\" type=\""+COt[CO.index(curUnit)]+"\" name=\""+curName+"\">")
			supportLines.append("<interface>")
			supportLines.append("</interface>")
			supportLines.append("</communication>")
		if(ST.count(curUnit)>0):
			supportLines.append("<memory id=\""+curName+"\" type=\""+STt[ST.index(curUnit)]+"\" name=\""+curName+"\">")
			supportLines.append("<interface>")
			supportLines.append("</interface>")
			supportLines.append("</memory>")
		if(IP.count(curUnit)>0):
			supportLines.append("<ipCore id=\""+curName+"\" type=\""+IPt[IP.index(curUnit)]+"\" name=\""+curName+"\">")
			supportLines.append("<interface>")
			supportLines.append("</interface>")
			supportLines.append("</ipCore>")
		if(CL.count(curUnit)>0):
			supportLines.append("<clock id=\""+curName+"\" type=\""+CLt[CL.index(curUnit)]+"\" name=\""+curName+"\">")
			supportLines.append("<interface>")
			supportLines.append("</interface>")
			supportLines.append("</clock>")

	if(mhsLines[l].find("END")>=0):
		for l in supportLines:
			if(l=="<interface>" and len(addressLines)!=0):
				lines.append("<addrs>")
				for a in addressLines:
					lines.append("<addr id=\""+a[0]+"\" base=\""+a[1]+"\" high=\""+a[2]+"\" />")
				lines.append("</addrs>")
			lines.append(l)

lines.append("<connection>")
lines.append("<physical>")
lines.append("</physical>")
lines.append("<virtual>")
lines.append("</virtual>")
lines.append("</connection>")
lines.append("</system>")
lines.append("</architecture>")
lines.append("</faster>")


for l in range(0,len(edkLines)):
	edkLines[l]=edkLines[l].strip()

curLevel=0;
interfacePrefix=""

getFromEdk=False;
edkLevel=0;

getCurrentUnit=False;

lastUnit="";
curUnit="";

xml=list()

portsList=list()
portNameList=list()
portSigList=list()
portDirection=list()
portSize=list()
portParsed=list()

for l in lines:
	xml.append(l)
	
	tag=l.split(" ")
	if(tag[0].strip()=="<system"):
#		print "Found SYSTEM"
		curLevel=curLevel+1
		if(tag[1].strip()=="id=\"fpga_0\""):
#			print "Found FPGA with EDK file"
			getFromEdk=True;
			edkLevel=curLevel;
	
	if(getFromEdk):
		if(tag[0].strip()=="</system>"):
#			print "End of EDK Parsing"
			if(curLevel==edkLevel):
				getFromEdk=False
			curLevel=curLevel-1
		
		if(tag[0].strip()=="<processingElement"):
			for n in range(0,len(tag)):
				t=tag[n].split("=")
				if(t[0]=="id"):
					curUnit=t[1]
#					print curUnit

		if(tag[0].strip()=="<ipCore"):
			for n in range(0,len(tag)):
				t=tag[n].split("=")
				if(t[0]=="id"):
					curUnit=t[1]
#					print curUnit
		
		if(tag[0].strip()=="<memory"):
			for n in range(0,len(tag)):
				t=tag[n].split("=")
				if(t[0]=="id"):
					curUnit=t[1]
#					print curUnit
		
		if(tag[0].strip()=="<communication"):
			for n in range(0,len(tag)):
				t=tag[n].split("=")
				if(t[0]=="id"):
					curUnit=t[1]
#					print curUnit
					
		if(tag[0].strip()=="<reconfigurableArea"):
			for n in range(0,len(tag)):
				t=tag[n].split("=")
				if(t[0]=="id"):
					curUnit=t[1].replace(">","").strip()
#					print "Rec Area: "+curUnit
#			print "Found a processor with name "+curUnit

		if(tag[0].strip()=="</processingElement>"):
			portsList.append([lastUnit,portSigList,portNameList,portDirection,portSize,portParsed])
			portSigList=list()
			portNameList=list()
			portParsed=list()
			portDirection=list()
			portSize=list()

		if(tag[0].strip()=="</ipCore>"):
			portsList.append([lastUnit,portSigList,portNameList,portDirection,portSize,portParsed])
			portSigList=list()
			portNameList=list()
			portParsed=list()
			portDirection=list()
			portSize=list()			
					
		if(tag[0].strip()=="</memory>"):
			portsList.append([lastUnit,portSigList,portNameList,portDirection,portSize,portParsed])
			portSigList=list()
			portNameList=list()
			portParsed=list()
			portDirection=list()
			portSize=list()
					
		if(tag[0].strip()=="</communication>"):
			portsList.append([lastUnit,portSigList,portNameList,portDirection,portSize,portParsed])
			portSigList=list()
			portNameList=list()
			portParsed=list()
			portDirection=list()
			portSize=list()
			
		if(tag[0].strip()=="</reconfigurableArea>"):
			portsList.append([lastUnit,portSigList,portNameList,portDirection,portSize,portParsed])
			portSigList=list()
			portNameList=list()
			portParsed=list()
			portDirection=list()
			portSize=list()

		if(tag[0].strip()=="</interface>"):
			lastUnit=curUnit.replace("\"","").replace("/>","").replace(">","")
			curUnit=""
			
		
		if(tag[0].strip()=="<interface>"):
				interfacePrefix=""
				for idx in range(0,tag[0].count("\t")+1):
					interfacePrefix=interfacePrefix+"\t"
#				print "Parsing interface of "+curUnit
				for edkL in edkLines:
					status=0;
					edkLL=list(edkL)
					for x in range(0,len(edkL)):
#						print "Index "+str(x)
						if(edkLL[x]=="["):
							status=1
						if(edkLL[x]=="]"):
							status=0
						if(edkLL[x]==" " and status==1):
							edkLL[x]=""
					edkL="".join(edkLL)
					mod=edkL.split(" ")
					if (mod[0].strip()=="<MODULE"):
#						print "Found module in EDK file"
						for n in range(0,len(mod)):
							t=mod[n].split("=");
							if(t[0]=="INSTANCE"):
#								print t[1]+" "+curUnit
								if(t[1]==curUnit):
#									print "Found right module! " + curUnit
									getCurrentUnit=True;
					
					if(getCurrentUnit):
						if(mod[0].strip()=="</MODULE>"):
#							print "End of EDK file parsing"
							getCurrentUnit=False
						
						if(mod[0].strip()=="<PARAMETER"):
#							print "Found a parameter"
							goodType=False
							varName=""
							value=0
							for n in range(0,len(mod)):
								t=mod[n].split("=");
								if(t[0].strip()=="NAME"):
									varName=t[1].replace("\"","");
								if(t[0].strip()=="TYPE"):
									if(t[1].strip().upper()=="\"INTEGER\""):
										goodType=True
							if(goodType):
								for n in range(0,len(mod)):
									t=mod[n].split("=");
									if(t[0].strip()=="VALUE"):
#										print t[1]
										value=t[1].strip().replace("\"","").replace("/>","").replace(">","")
								exec '%s = %s' %(varName,value)
						
						if(mod[0].strip()=="<PORT"):	
							s="";
							s=interfacePrefix+mod[0]+" ";
							lsb=0
							msb=0
							doIt=True

							for n in range(0,len(mod)):
								t=mod[n].split("=")
								if(t[0]=="SIGNAME"):
										sigName=t[1].replace("\"","").replace("/>","").replace(">","")
#										print "Checking "+sigName+" aganis __NOC__"
										if(sigName.strip()=="__NOC__"):
											doIt=False

							if(not doIt):
#								print "Avoiding PORT: "+edkL
								continue
								
#							print "Parsing PORT: "+edkL

							for n in range(0,len(mod)):
								t=mod[n].split("=")
								if(t[0]=="NAME"):
										s=s+"id="+t[1]+" ";
										portNameList.append(t[1].replace("\"","").replace("/>","").replace(">",""))
							
							for n in range(0,len(mod)):
								t=mod[n].split("=")
								if(t[0]=="SIGNAME"):
										portSigList.append(t[1].replace("\"","").replace("/>","").replace(">",""))
										portParsed.append(False)

							for n in range(0,len(mod)):
								t=mod[n].split("=")
								if(t[0]=="LSB"):
										lsb=int(t[1].strip("\""))

							for n in range(0,len(mod)):
								t=mod[n].split("=")
								if(t[0]=="MSB"):
										msb=int(t[1].strip("\""))
						
							for n in range(0,len(mod)):
								t=mod[n].split("=")
								if(t[0]=="VECFORMULA"):
									t[1]=t[1].replace("[","")
									t[1]=t[1].replace("]","")
									t[1]=t[1].replace("/>","").replace(">","")
									t[1]=t[1].replace("\"","")
									t[1]=t[1].replace(" ","")
									dim=t[1].split(":")
#									print dim[0]
#									print dim[1]
									msb=int(eval(dim[0]))
									lsb=int(eval(dim[1]))

							s=s+"size=\""+str(lsb-msb+1)+"\" "
							portSize.append(str(lsb-msb+1))

							for n in range(0,len(mod)):
								t=mod[n].split("=")
								if(t[0]=="DIR"):
									s=s+"direction=\""
									if(t[1]=="\"I\""):
										s=s+"IN\" ";
									if(t[1]=="\"O\""):
										s=s+"OUT\" ";
									if(t[1]=="\"IO\""):
										s=s+"INOUT\" ";
									portDirection.append(t[1].replace("\"","").replace("/>","").replace(">",""))

							s=s+"/>"

							xml.append(s)

app=open("../application.xml")
appLines=app.readlines()

addCores=open("../addedCores.xml")
addLines=addCores.readlines()

for l in xml:
	
	tag=l.split(" ")
	
	if(tag[0].strip()=="</system>"):
		for addL in addLines:
			if(addL.strip()!="<faster>" and addL.strip()!="</faster>"):
				print addL


	print l
	
	
	if(tag[0].strip()=="<physical>"):
		interfacePrefix=""
		for idx in range(0,tag[0].count("\t")+1):
			interfacePrefix=interfacePrefix+"\t"
#		print "Parsing physical connection for "+curUnit
		for p in portsList:
			[u,sn,n,d,s,v]=p
			for i in range(0,len(n)):
#				print "Connection for signal: "+sn[i]
				if(v[i]==False):
					for p2 in portsList:
						[u2,sn2,n2,d2,s2,v2]=p2
						if(u!=u2):
							for i2 in range(0,len(n2)):
								if(sn[i]==sn2[i2]):
									if((d[i]=="O" or d[i]=="IO") and d2[i2]=="I"):
										s=interfacePrefix+"<link src=\""+u+"."+n[i]+"\" tgt=\""+u2+"."+n2[i2]+"\" size=\""+s2[i2]+"\"/>"
										v[i]=True
										v2[i2]=True
										print s
									if((d[i]=="I" or d[i]=="IO") and d2[i2]=="O"):
										s=interfacePrefix+"<link src=\""+u2+"."+n2[i2]+"\" tgt=\""+u+"."+n[i]+"\" size=\""+s2[i2]+"\"/>"
										v[i]=True
										v2[i2]=True
										print s
									if(d[i]=="IO" and d2[i2]=="IO"):
										s=interfacePrefix+"<link src=\""+u+"."+n[i]+"\" tgt=\""+u2+"."+n2[i2]+"\" size=\""+s2[i2]+"\"/>"
										s1=interfacePrefix+"<link src=\""+u2+"."+n2[i2]+"\" tgt=\""+u+"."+n[i]+"\" size=\""+s2[i2]+"\"/>"
										v[i]=True
										v2[i2]=True
										print s
										print s1

	if(tag[0].strip()=="</architecture>"):
		for appL in appLines:
			if(appL.strip()!="<faster>" and appL.strip()!="</faster>"):
				print appL
								



#for p in portsList:
#	[u,sn,n,d,s,v]=p
#	print u
#	for i in range(0,len(n)):
#		if(v[i]==False):
#			print "\t"+sn[i]+"\t"+n[i]+"\t"+d[i]+"\t"+s[i]+"\t"+str(v[i])
