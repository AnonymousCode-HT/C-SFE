set_property BITSTREAM.CONFIG.UNUSEDPIN pulldown [current_design]
set_property BITSTREAM.GENERAL.COMPRESS true [current_design]
set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]
set_property BITSTREAM.CONFIG.CONFIGRATE 85.0 [current_design]
set_property BITSTREAM.CONFIG.SPI_FALL_EDGE YES [current_design]
set_property CONFIG_VOLTAGE 1.8 [current_design]
set_property CONFIG_MODE SPIx4 [current_design]
set_property CFGBVS GND [current_design]

# user clock
set_property IOSTANDARD LVDS [get_ports CLK_IN1_D_0_clk_n]
set_property PACKAGE_PIN G17 [get_ports CLK_IN1_D_0_clk_p]
set_property PACKAGE_PIN G16 [get_ports CLK_IN1_D_0_clk_n]
set_property IOSTANDARD LVDS [get_ports CLK_IN1_D_0_clk_p]


create_clock -period 10.000 [get_ports CLK_IN1_D_0_clk_p]

set_property PACKAGE_PIN J18 [get_ports DRAM_0_STAT_CATTRIP_0]
set_property IOSTANDARD LVCMOS18 [get_ports DRAM_0_STAT_CATTRIP_0]
set_property PULLDOWN true [get_ports DRAM_0_STAT_CATTRIP_0]


connect_debug_port dbg_hub/clk [get_nets riscv_i/clk_wiz_0/inst/hbm_apb_riscv_clk_wiz_0_0]
set_property C_USER_SCAN_CHAIN 1 [get_debug_cores dbg_hub]







