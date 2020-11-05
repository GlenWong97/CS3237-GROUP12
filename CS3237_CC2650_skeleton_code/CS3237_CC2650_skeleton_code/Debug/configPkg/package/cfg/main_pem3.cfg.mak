# invoke SourceDir generated makefile for main.pem3
main.pem3: .libraries,main.pem3
.libraries,main.pem3: package/cfg/main_pem3.xdl
	$(MAKE) -f /home/zhaoying/workspace/CS3237/ccs_workspace/cs3237_CC2650_template/src/makefile.libs

clean::
	$(MAKE) -f /home/zhaoying/workspace/CS3237/ccs_workspace/cs3237_CC2650_template/src/makefile.libs clean

