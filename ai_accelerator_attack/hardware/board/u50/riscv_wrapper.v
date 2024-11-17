//Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
//--------------------------------------------------------------------------------
//Tool Version: Vivado v.2022.2 (lin64) Build 3671981 Fri Oct 14 04:59:54 MDT 2022
//Date        : Fri Feb  2 12:46:48 2024
//Host        : chguo-desktop running 64-bit Ubuntu 22.04.3 LTS
//Command     : generate_target riscv_wrapper.bd
//Design      : riscv_wrapper
//Purpose     : IP block netlist
//--------------------------------------------------------------------------------
`timescale 1 ps / 1 ps

module riscv_wrapper
   (CLK_IN1_D_0_clk_n,
    CLK_IN1_D_0_clk_p,
    DRAM_0_STAT_CATTRIP_0,
	
	
	
	/* QSFP28 */
	
	qsfp0_tx1_p,
      qsfp0_tx1_n,
    qsfp0_rx1_p,
    qsfp0_rx1_n,
	qsfp0_mgt_refclk_1_p,
    qsfp0_mgt_refclk_1_n,
	
	/* PCIe */
	
//    pci_express_x4_rxn,
//    pci_express_x4_rxp,
//    pci_express_x4_txn,
//    pci_express_x4_txp,
//    pcie_perstn,
//    pcie_refclk_clk_n,
//    pcie_refclk_clk_p,
	
	
	/* UART */
    usb_uart_rxd,
    usb_uart_txd);
	
	/*************************************************************/
	
	output          qsfp0_tx1_p;
    output          qsfp0_tx1_n;
    input         qsfp0_rx1_p;
    input          qsfp0_rx1_n;
	input         qsfp0_mgt_refclk_1_p;
    input           qsfp0_mgt_refclk_1_n;
	
	wire          qsfp0_tx1_p;
    wire          qsfp0_tx1_n;
    wire         qsfp0_rx1_p;
    wire          qsfp0_rx1_n;
	wire         qsfp0_mgt_refclk_1_p;
    wire           qsfp0_mgt_refclk_1_n;

    /*************************************************************/
	
  input CLK_IN1_D_0_clk_n;
  input CLK_IN1_D_0_clk_p;
  output DRAM_0_STAT_CATTRIP_0;
 
  
//  input [3:0]pci_express_x4_rxn;
//  input [3:0]pci_express_x4_rxp;
//  output [3:0]pci_express_x4_txn;
//  output [3:0]pci_express_x4_txp;
//  input pcie_perstn;
//  input pcie_refclk_clk_n;
//  input pcie_refclk_clk_p;
  
  input usb_uart_rxd;
  output usb_uart_txd;

  wire CLK_IN1_D_0_clk_n;
  wire CLK_IN1_D_0_clk_p;
  wire DRAM_0_STAT_CATTRIP_0;
  wire eth_clock;
  wire eth_clock_ok;
  wire eth_gt_user_clock;
 wire [63:0] eth_rx_axis_tdata;
  wire [7:0]eth_rx_axis_tkeep;
 wire eth_rx_axis_tlast;
 wire eth_rx_axis_tready;
  wire eth_rx_axis_tuser;
 wire eth_rx_axis_tvalid;
  wire [15:0]eth_status;
 wire [63:0] eth_tx_axis_tdata;
  wire [7:0] eth_tx_axis_tkeep;
 wire eth_tx_axis_tlast;
 wire eth_tx_axis_tready;
  wire eth_tx_axis_tuser;
 wire eth_tx_axis_tvalid;
  wire [3:0]pci_express_x4_rxn;
  wire [3:0]pci_express_x4_rxp;
  wire [3:0]pci_express_x4_txn;
  wire [3:0]pci_express_x4_txp;
  wire pcie_perstn;
  wire pcie_refclk_clk_n;
  wire pcie_refclk_clk_p;
  wire usb_uart_rxd;
  wire usb_uart_txd;

  riscv riscv_i
       (.CLK_IN1_D_0_clk_n(CLK_IN1_D_0_clk_n),
        .CLK_IN1_D_0_clk_p(CLK_IN1_D_0_clk_p),
 
 	.DRAM_0_STAT_CATTRIP_0(DRAM_0_STAT_CATTRIP_0),
		
        
        .eth_clock(eth_clock),
        .eth_clock_ok(eth_clock_ok),
        .eth_gt_user_clock(eth_gt_user_clock),
        .eth_rx_axis_tdata(eth_rx_axis_tdata),
        .eth_rx_axis_tkeep(eth_rx_axis_tkeep),
        .eth_rx_axis_tlast(eth_rx_axis_tlast),
        .eth_rx_axis_tready(eth_rx_axis_tready),
        .eth_rx_axis_tuser(eth_rx_axis_tuser),
        .eth_rx_axis_tvalid(eth_rx_axis_tvalid),
        .eth_status(eth_status),
        .eth_tx_axis_tdata(eth_tx_axis_tdata),
        .eth_tx_axis_tkeep(eth_tx_axis_tkeep),
        .eth_tx_axis_tlast(eth_tx_axis_tlast),
        .eth_tx_axis_tready(eth_tx_axis_tready),
        .eth_tx_axis_tuser(eth_tx_axis_tuser),
        .eth_tx_axis_tvalid(eth_tx_axis_tvalid),

		
//        .pci_express_x4_rxn(pci_express_x4_rxn),
//        .pci_express_x4_rxp(pci_express_x4_rxp),
//        .pci_express_x4_txn(pci_express_x4_txn),
//        .pci_express_x4_txp(pci_express_x4_txp),
//        .pcie_perstn(pcie_perstn),
//        .pcie_refclk_clk_n(pcie_refclk_clk_n),
//        .pcie_refclk_clk_p(pcie_refclk_clk_p),
        
        
        .usb_uart_rxd(usb_uart_rxd),
        .usb_uart_txd(usb_uart_txd));

ethernet_u50 ethernet_u50_i (
    .clock_ok(eth_clock_ok),
    .clock(eth_clock),

    .eth_gt_user_clock(eth_gt_user_clock),

    .eth_rx_axis_tdata(eth_rx_axis_tdata),
    .eth_rx_axis_tkeep(eth_rx_axis_tkeep),
    .eth_rx_axis_tlast(eth_rx_axis_tlast),
    .eth_rx_axis_tready(eth_rx_axis_tready),
    .eth_rx_axis_tuser(eth_rx_axis_tuser),
    .eth_rx_axis_tvalid(eth_rx_axis_tvalid),
    .eth_status(eth_status),
    .eth_tx_axis_tdata(eth_tx_axis_tdata),
    .eth_tx_axis_tkeep(eth_tx_axis_tkeep),
    .eth_tx_axis_tlast(eth_tx_axis_tlast),
    .eth_tx_axis_tready(eth_tx_axis_tready),
    .eth_tx_axis_tuser(eth_tx_axis_tuser),
    .eth_tx_axis_tvalid(eth_tx_axis_tvalid),

    .sfp_tx_p(qsfp0_tx1_p),
    .sfp_tx_n(qsfp0_tx1_n),
    .sfp_rx_p(qsfp0_rx1_p),
    .sfp_rx_n(qsfp0_rx1_n),
    .sfp_mgt_refclk_p(qsfp0_mgt_refclk_1_p),
    .sfp_mgt_refclk_n(qsfp0_mgt_refclk_1_n),
    .sfp_modsel(),
    .sfp_reset(),
    .sfp_modprs(),
    .sfp_int(),
    .sfp_lpmode(),
    .sfp_refclk_reset(),
    .sfp_fs()
);

endmodule

