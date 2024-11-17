#RX TO USB 232 IC TX
set_property PACKAGE_PIN V24 [get_ports rs232_uart_rxd]
#TX TO USB 232 IC RX 
set_property PACKAGE_PIN U22 [get_ports rs232_uart_txd]

set_property IOSTANDARD LVCMOS33 [get_ports rs232_uart_rxd]
set_property IOSTANDARD LVCMOS33 [get_ports rs232_uart_txd]
