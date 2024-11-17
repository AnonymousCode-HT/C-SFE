# RGMMI
set_property PACKAGE_PIN G11  [get_ports rgmii_rxc] 
set_property PACKAGE_PIN G12  [get_ports rgmii_rx_ctl]
### -----------------RX------------------###
set_property PACKAGE_PIN H12  [get_ports {rgmii_rd[0]}]
set_property PACKAGE_PIN H11  [get_ports {rgmii_rd[1]}]
set_property PACKAGE_PIN F14  [get_ports {rgmii_rd[2]}]
set_property PACKAGE_PIN F13  [get_ports {rgmii_rd[3]}]
### -----------------TX------------------###
set_property PACKAGE_PIN G10  [get_ports rgmii_txc]
set_property PACKAGE_PIN F12  [get_ports rgmii_tx_ctl]
set_property PACKAGE_PIN G9  [get_ports {rgmii_td[0]}]
set_property PACKAGE_PIN F9  [get_ports {rgmii_td[1]}]
set_property PACKAGE_PIN F8  [get_ports {rgmii_td[2]}]
set_property PACKAGE_PIN F10  [get_ports {rgmii_td[3]}]
												
set_property SLEW FAST [get_ports rgmii_txc]
set_property SLEW FAST [get_ports rgmii_tx_ctl]
set_property SLEW FAST [get_ports {rgmii_td[*]}]

set_property IOSTANDARD LVCMOS33  [get_ports rgmii_rxc]
set_property IOSTANDARD LVCMOS33  [get_ports rgmii_rx_ctl]												  
set_property IOSTANDARD LVCMOS33  [get_ports {rgmii_rd[*]}]
																														 
set_property IOSTANDARD LVCMOS33  [get_ports rgmii_txc]
set_property IOSTANDARD LVCMOS33  [get_ports rgmii_tx_ctl]
set_property IOSTANDARD LVCMOS33  [get_ports {rgmii_td[*]}]
