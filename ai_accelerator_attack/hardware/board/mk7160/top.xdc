set_property BITSTREAM.GENERAL.COMPRESS true [current_design]

## Clock Signal
create_clock -period 10.000 -name clk100m_i -waveform {0.000 5.000} [get_ports sys_clock]
set_property PACKAGE_PIN AA3 [get_ports sys_clock]
set_property IOSTANDARD SSTL135 [get_ports sys_clock]

#create_clock -period 6.400 -name GT_DIFF_REFCLK_clk_p -waveform {0.000 4.000} [get_ports GT_DIFF_REFCLK_clk_p]
#set_property PACKAGE_PIN D6 [get_ports GT_DIFF_REFCLK_clk_p]

#set_property LOC GTXE2_CHANNEL_X0Y4 [get_cells riscv_i/IO/axi_chip2chip_0_aurora64/inst/riscv_axi_chip2chip_0_aurora64_0_core_i/riscv_axi_chip2chip_0_aurora64_0_wrapper_i/riscv_axi_chip2chip_0_aurora64_0_multi_gt_i/riscv_axi_chip2chip_0_aurora64_0_gtx_inst/gtxe2_i]

## Reset button
set_property -dict { PACKAGE_PIN J13 IOSTANDARD LVCMOS33 } [get_ports reset];



