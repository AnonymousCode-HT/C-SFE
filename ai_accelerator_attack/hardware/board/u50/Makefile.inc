BOARD_PART  ?= xilinx.com:au50:part0:1.3
XILINX_PART ?= xcu50-fsvh2104-2-e
CFG_DEVICE  ?= SPIx4 -size 512
CFG_PART    ?= mt25qu01g-spi-x1_x2_x4
CFG_BOOT    ?= # -loaddata {up 0x08000000 workspace/boot.elf}
MEMORY_SIZE ?= 0x80000000
#JTAG_BOOT = 1
ROOTFS      ?= NFS
