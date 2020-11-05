# invoke SourceDir generated makefile for i2ctmp007.pem3
i2ctmp007.pem3: .libraries,i2ctmp007.pem3
.libraries,i2ctmp007.pem3: package/cfg/i2ctmp007_pem3.xdl
	$(MAKE) -f /home/zhaoying/workspace/CS3237/ccs_workspace/cs3237_CC2650_template/src/makefile.libs

clean::
	$(MAKE) -f /home/zhaoying/workspace/CS3237/ccs_workspace/cs3237_CC2650_template/src/makefile.libs clean

