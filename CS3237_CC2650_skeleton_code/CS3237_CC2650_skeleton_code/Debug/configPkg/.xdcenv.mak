#
_XDCBUILDCOUNT = 
ifneq (,$(findstring path,$(_USEXDCENV_)))
override XDCPATH = /home/zhaoying/workspace/CS3237/ccs1011/tirtos_cc13xx_cc26xx_2_21_00_06/packages;/home/zhaoying/workspace/CS3237/ccs1011/tirtos_cc13xx_cc26xx_2_21_00_06/products/tidrivers_cc13xx_cc26xx_2_21_00_04/packages;/home/zhaoying/workspace/CS3237/ccs1011/tirtos_cc13xx_cc26xx_2_21_00_06/products/bios_6_46_01_37/packages;/home/zhaoying/workspace/CS3237/ccs1011/tirtos_cc13xx_cc26xx_2_21_00_06/products/uia_2_01_00_01/packages
override XDCROOT = /home/zhaoying/workspace/CS3237/xdctools_3_32_00_06_core_linux/xdctools_3_32_00_06_core
override XDCBUILDCFG = ./config.bld
endif
ifneq (,$(findstring args,$(_USEXDCENV_)))
override XDCARGS = 
override XDCTARGETS = 
endif
#
ifeq (0,1)
PKGPATH = /home/zhaoying/workspace/CS3237/ccs1011/tirtos_cc13xx_cc26xx_2_21_00_06/packages;/home/zhaoying/workspace/CS3237/ccs1011/tirtos_cc13xx_cc26xx_2_21_00_06/products/tidrivers_cc13xx_cc26xx_2_21_00_04/packages;/home/zhaoying/workspace/CS3237/ccs1011/tirtos_cc13xx_cc26xx_2_21_00_06/products/bios_6_46_01_37/packages;/home/zhaoying/workspace/CS3237/ccs1011/tirtos_cc13xx_cc26xx_2_21_00_06/products/uia_2_01_00_01/packages;/home/zhaoying/workspace/CS3237/xdctools_3_32_00_06_core_linux/xdctools_3_32_00_06_core/packages;..
HOSTOS = Linux
endif
