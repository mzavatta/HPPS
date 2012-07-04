#!/usr/bin/env python
import os
import sys
import string
import shutil

dsize=9

input_mhs=sys.argv[1]
patch_file=sys.argv[2]

patch=open(patch_file)
patchLines=patch.readlines()

num_cores=int(patchLines[0])

if (num_cores==1):
  print " * Adding 1 core to MHS file"
else:
  print " * Adding "+str(num_cores)+" cores to MHS file"
fileHandle = open (input_mhs, 'a' ) 

interrupt_string=list()

for l in range(0, num_cores):
  print "  - "+patchLines[2+l*dsize+8].strip()
  fileHandle.write("\n")
  fileHandle.write("BEGIN " + patchLines[2+l*dsize+0].strip()+"\n")
  fileHandle.write(" PARAMETER INSTANCE = " + patchLines[2+l*dsize+2].strip()+"\n")
  fileHandle.write(" PARAMETER HW_VER = " + patchLines[2+l*dsize+3].strip()+"\n")
  fileHandle.write(" PARAMETER C_BASEADDR = " + patchLines[2+l*dsize+4].strip()+"\n")
  fileHandle.write(" PARAMETER C_HIGHADDR = " + patchLines[2+l*dsize+5].strip()+"\n")
  fileHandle.write(" BUS_INTERFACE SPLB = " + patchLines[2+l*dsize+6].strip()+"\n")
  if (patchLines[2+l*dsize+7].strip() != ""):
     fileHandle.write(" BUS_INTERFACE XIL_NPI = " + patchLines[2+l*dsize+7].strip()+"\n")
     fileHandle.write(" PORT XIL_NPI_Clk = clk_100_0000MHzPLL0\n")
     fileHandle.write(" PORT XIL_NPI_Rst = net_gnd\n")
  fileHandle.write(" PORT INT_DONE = " + patchLines[2+l*dsize+2].strip()+"_INT_DONE\n");
  interrupt_string.append(patchLines[2+l*dsize+2].strip()+"_INT_DONE")
  fileHandle.write("END\n")
  
  core_name=patchLines[2+l*dsize+0].strip()
  ver=patchLines[2+l*dsize+3].strip()
  ver=string.replace(ver, ".", "_")
  core_dir=core_name+"_v"+ver
  
  coreid=core_name+"_v2_1_0"

  os.makedirs("./int_arch/edk/pcores/"+core_dir+"/data")
  os.makedirs("./int_arch/edk/pcores/"+core_dir+"/netlist")

  os.system("tar xf ./int_arch/edk/templates/vhdl.tgz -C ./int_arch/edk/pcores/"+core_dir+"/hdl/vhdl")
  shutil.copyfile("./int_arch/edk/templates/core.bbd", "./int_arch/edk/pcores/"+core_dir+"/data/"+coreid+".bbd")
  shutil.copyfile("./int_arch/edk/templates/FIFO_2_CLKS.ngc", "./int_arch/edk/pcores/"+core_dir+"/netlist/FIFO_2_CLKS.ngc")

  outmpd = open ("./int_arch/edk/pcores/"+core_dir+"/data/"+coreid+".mpd", 'w') 
  if (patchLines[2+l*dsize+7].strip() != ""): 
     mpd_file = open ("./int_arch/edk/templates/core.mpd") 
  else: 
     mpd_file = open ("./int_arch/edk/templates/core_no_mem.mpd") 
  mpdLines=mpd_file.readlines() 
  for m in range(0, len(mpdLines)):
     line=mpdLines[m]
     if (line.find("$corename")>=0):
        line=string.replace(line, "$corename", core_name)
     if (line.find("$nparameters")>=0):
        line=string.replace(line, "$nparameters", patchLines[2+l*dsize+1].strip())
     if (line.find("$CUPNAME")>=0):
        line=string.replace(line, "$CUPNAME", core_name.upper())
     outmpd.write(line)

  outpao = open ("./int_arch/edk/pcores/"+core_dir+"/data/"+coreid+".pao", 'w') 
  pao_file = open ("./int_arch/edk/templates/core.pao") 
  paoLines=pao_file.readlines() 
  for p in range(0, len(paoLines)):
     line=paoLines[p]
     if (line.find("$coreid")>=0):
        line=string.replace(line, "$coreid", core_dir)
     if (line.find("$funname")>=0):
        line=string.replace(line, "$funname", patchLines[2+l*dsize+8].strip())
     if (line.find("$corename")>=0):
        line=string.replace(line, "$corename", core_name)
     outpao.write(line)

  outvhd = open ("./int_arch/edk/pcores/"+core_dir+"/hdl/vhdl/"+core_name+".vhd", 'w') 
  vhd_file = open ("./int_arch/edk/templates/core.vhd") 
  vhdLines=vhd_file.readlines() 
  for v in range(0, len(vhdLines)):
     line=vhdLines[v]
     if (line.find("$coreid")>=0):
        line=string.replace(line, "$coreid", core_dir)
     if (line.find("$corename")>=0):
        line=string.replace(line, "$corename", core_name)
     if (line.find("$nparameters")>=0):
        line=string.replace(line, "$nparameters", patchLines[2+l*dsize+1].strip())
     outvhd.write(line)

fileHandle.write("\n")
fileHandle.close()
    
mhs=open(input_mhs)
mhsLines=mhs.readlines()

is_intc=False
fileHandle = open (input_mhs, 'w' ) 
for l in range(0, len(mhsLines)):
  if (mhsLines[l].strip().find("BEGIN xps_intc")>=0):
    is_intc=True
  if (is_intc==False):
    fileHandle.write(mhsLines[l])
    continue
  if (mhsLines[l].strip().find("PORT Intr =")>=0):
    if (len(interrupt_string)>0):
       elem=mhsLines[l].split("=");
       name_ints=elem[1].strip()
       string=name_ints.strip()
       for i in range(0, len(interrupt_string)):       
         if (len(string)>0):
            string="&"+string;
         string=interrupt_string[i]+string
       fileHandle.write(" PORT Intr = "+string+"\n")
    else:
       fileHandle.write(mhsLines[l])
  elif (mhsLines[l].find("END")==0 or mhsLines[l].find("INSTANCE = Intr_Access")>=0):
    fileHandle.write(mhsLines[l])
    is_intc=False
  else:
    fileHandle.write(mhsLines[l])


	

