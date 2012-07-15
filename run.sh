#!/bin/bash
OUT_DIR="./tmp/edk"
rm -rf int_arch $OUT_DIR output.c *.xml
mkdir -p $OUT_DIR
echo ""
echo "*** "
echo ""

int_arch_TGZ=$1
APPLICATION=$2
if [ -d $int_arch_TGZ ]; then
  echo "ERROR: Please specify the archive of the base architecture!"
  exit -1;
fi
if [ -d $APPLICATION ]; then
  echo "ERROR: Please specify the input source code!"
  exit -1;
fi

if [ -f $int_arch_TGZ ]; then
  echo " * Base architecture: $int_arch_TGZ"
else
  echo "ERROR: Input architecture not found!"
  exit -1;
fi

echo ""
echo "Creating base architecture"
tar xf $int_arch_TGZ

if [ -f "./int_arch/edk/system.mhs" ]; then
  echo " * Initial system MHS: ./int_arch/edk/system.mhs";
else
  echo "ERROR!!"
  exit -1;
fi

#if [ ! -f "../architecture.xml" ]; then
#  touch ../architecture.xml
#fi 
#if [ ! -f "../addedCores.xml" ]; then
#  touch ../addedCores.xml
#fi 

#echo ""
#echo "Creating architecture file"
#python ../int_scripts/parsing_mhs.py ./int_arch/edk/system.mhs ./int_arch/edk/system.xml > $OUT_DIR/architecture.xml


cp ../../application.xml $OUT_DIR/application.xml
cp ../../$APPLICATION $OUT_DIR/$APPLICATION

echo ""
echo "Analyzing the application to create the HW/SW cores"
zebu -M $OUT_DIR/application.xml --pragma-parse --platform-generation=$OUT_DIR --without-transformation $OUT_DIR/$APPLICATION >& $OUT_DIR/zebu.log

cp -r $OUT_DIR/pcores/* ./int_arch/edk/pcores

cp $OUT_DIR/Software/* ./int_arch/edk/Software

echo ""
echo "Patching system.xmp file"
python ../int_scripts/patch_systemxmp.py ./int_arch/edk/system.xmp

echo ""
echo "Patching system.mss file"
python ../int_scripts/patch_mss.py int_arch/edk/system.mss $OUT_DIR/core.list

echo ""
echo "Patching system.mhs file"
python ../int_scripts/patch_mhs.py int_arch/edk/system.mhs $OUT_DIR/core.list
python ../int_scripts/patch_mpmc.py int_arch/edk/system.mhs $OUT_DIR/core.list

echo ""
echo "*** "
echo ""


