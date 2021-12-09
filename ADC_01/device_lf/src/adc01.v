/**
 * ------------------------------------------------------------
 * Copyright (c) All rights reserved 
 * SiLab, Institute of Physics, University of Bonn
 * ------------------------------------------------------------
 */

 // Fs frequency up to 1MHZ !!!**
 
`timescale 1ps / 1ps
//`default_nettype none


module adc01 (

    input wire FCLK_IN, 

    //full speed 
    inout wire [7:0] BUS_DATA,
    input wire [15:0] ADD,
    input wire RD_B,
    input wire WR_B,

    //high speed
    inout wire [7:0] FD,
    input wire FREAD,
    input wire FSTROBE,
    input wire FMODE,

    //debug
    output wire LED1,
    output wire LED2,
    output wire LED3,
    output wire LED4,
    output wire LED5,

    inout SDA,
    inout SCL,

    //SRAM
    output wire [19:0] SRAM_A,
    inout wire [15:0] SRAM_IO,
    output wire SRAM_BHE_B,
    output wire SRAM_BLE_B,
    output wire SRAM_CE1_B,
    output wire SRAM_OE_B,
    output wire SRAM_WE_B,
		
	 // ADC01 chip
 	 output wire SEL0,
	 output wire SEL1,
	 output wire SEL2,
	 output wire EN_OPA,
	 output wire CLK_COMP,
	 output wire CLK_SR,
	 output wire RST_B,
	 output wire SAMPLE,
	 input  wire ADC_DATA,
	 		
		// misc
	 input wire LCK1,
	 output wire [9:0] MULTI_IO

);   
    parameter ABUSWIDTH = 16;
	  
	wire FIFO_READ, FIFO_EMPTY, FIFO_NOT_EMPTY, FIFO_FULL, FIFO_NEAR_FULL, FIFO_READ_ERROR;
    wire [31:0] FIFO_DATA;
	wire USB_READ;
	  
	assign USB_READ = FREAD && FSTROBE;

	
	
	//assign LED3 = 0;

    assign SDA = 1'bz;
    assign SCL = 1'bz;

    (* KEEP = "{TRUE}" *) 
    wire CLK160;
    (* KEEP = "{TRUE}" *) 
    wire CLK80;
    (* KEEP = "{TRUE}" *) 
    wire BUS_CLK;
    (* KEEP = "{TRUE}" *) 
    wire SPI_CLK;
    (* KEEP = "{TRUE}" *) 
	  wire LCK1_BUF;   		
		
	wire [7:0] SEQ_OUT;
	wire EN_SEQ;
	

	
    
    wire CLK_LOCKED;
    wire BUS_RST;
    wire  RX_EN; // Enable ADC data INPUT / ! internal siganl !
    
	assign CLK_COMP = SEQ_OUT[0];
    assign CLK_SR   = SEQ_OUT[1];   
    assign SAMPLE   = SEQ_OUT[2];   
    assign RST_B    = SEQ_OUT[3];  
	assign RX_EN    = SEQ_OUT[4]; // Enable ADC data INPUT / ! internal siganl !  

    reset_gen i_reset_gen(.CLK(BUS_CLK), .RST(BUS_RST));

    clk_gen i_clkgen(
        .CLKIN(FCLK_IN),
        .BUS_CLK(BUS_CLK),
        .CLK160(CLK160),
        .SPI_CLK(SPI_CLK)
    ); 

	BUFG LCK1_BUFG_INST (.I(LCK1), .O(LCK1_BUF));  // clock from external PLL chip
    
	wire CLK_SPI;
	wire CLK_EN_SEQ;
	reg EN_SEQ_SYNC;	   
	clock_divider #(.DIVISOR(2)) div1 ( .CLK(~LCK1_BUF), .RESET(1'b0), .CLOCK(CLK_SPI) );
    assign CLK_EN_SEQ= ~CLK_SPI & LCK1_BUF;

	always @(posedge CLK_EN_SEQ) begin
     EN_SEQ_SYNC <= EN_SEQ;
     end

	//assign LCK1_BUF = BUS_CLK;

 // -------  MODULE ADREESSES  ------- //
    localparam GPIO_BASEADDR = 16'h0000;
    localparam GPIO_HIGHADDR = 16'h000f;

    localparam SEQ_GEN_BASEADDR = 16'h1000;                      //0x1000
    localparam SEQ_GEN_HIGHADDR = SEQ_GEN_BASEADDR + 15 + 16'h1fff;   //0x300f

    localparam SPI_RX_BASEADDR = 16'h4000;                      //0x1000
    localparam SPI_RX_HIGHADDR = SPI_RX_BASEADDR + 15;   //0x300f
	localparam SPI_RX_IDENTIFIER = 4'b1011;
    
	localparam FIFO_BASEADDR      = 16'h8000;
    localparam FIFO_HIGHADDR      = FIFO_BASEADDR + 15;		
    
 // -------  BUS SIGNALING  ------- //
    wire [15:0] BUS_ADD;
    wire BUS_RD, BUS_WR;
    fx2_to_bus i_fx2_to_bus (
        .ADD(ADD),
        .RD_B(RD_B),
        .WR_B(WR_B),

        .BUS_CLK(BUS_CLK),
        .BUS_ADD(BUS_ADD),
        .BUS_RD(BUS_RD),
        .BUS_WR(BUS_WR),
        .CS_FPGA()
    );

 // -------  USER MODULES  ------- //

        
      	   
    seq_gen 
    #( 
        .BASEADDR(SEQ_GEN_BASEADDR), 
        .HIGHADDR(SEQ_GEN_HIGHADDR),
        .MEM_BYTES(8*1024), 
        .OUT_BITS(8) 
    ) i_seq_gen
    (
        .BUS_CLK(BUS_CLK),
        .BUS_RST(BUS_RST),
        .BUS_ADD(BUS_ADD),
        .BUS_DATA(BUS_DATA),
        .BUS_RD(BUS_RD),
        .BUS_WR(BUS_WR),
        
		.SEQ_EXT_START(EN_SEQ_SYNC),
        .SEQ_CLK(LCK1_BUF),
        .SEQ_OUT(SEQ_OUT)  
    );
    
      
		
	fast_spi_rx
	#(
			.BASEADDR(SPI_RX_BASEADDR),
			.HIGHADDR(SPI_RX_HIGHADDR),
			.ABUSWIDTH(ABUSWIDTH),
			.IDENTIFIER(SPI_RX_IDENTIFIER)
	) i_fast_spi_rx
	(
			.BUS_CLK(BUS_CLK),
			.BUS_ADD(BUS_ADD),
			.BUS_DATA(BUS_DATA),
			.BUS_RST(BUS_RST),
			.BUS_WR(BUS_WR),
			.BUS_RD(BUS_RD),
			
			.SCLK(CLK_SPI),
			.SDI(ADC_DATA),
			.SEN(RX_EN),//.SEN(1'b1),

			.FIFO_READ(FIFO_READ),
			.FIFO_EMPTY(FIFO_EMPTY),
			.FIFO_DATA(FIFO_DATA)
			
	); 
	

	sram_fifo #(
			.BASEADDR(FIFO_BASEADDR),
			.HIGHADDR(FIFO_HIGHADDR)
	) i_out_fifo (
			.BUS_CLK(BUS_CLK),
			.BUS_RST(BUS_RST),
			.BUS_ADD(BUS_ADD),
			.BUS_DATA(BUS_DATA),
			.BUS_RD(BUS_RD),
			.BUS_WR(BUS_WR),

			.SRAM_A(SRAM_A),
			.SRAM_IO(SRAM_IO),
			.SRAM_BHE_B(SRAM_BHE_B),
			.SRAM_BLE_B(SRAM_BLE_B),
			.SRAM_CE1_B(SRAM_CE1_B),
			.SRAM_OE_B(SRAM_OE_B),
			.SRAM_WE_B(SRAM_WE_B),

			.USB_READ(USB_READ),
			.USB_DATA(FD),

			.FIFO_READ_NEXT_OUT(FIFO_READ),
			.FIFO_EMPTY_IN(FIFO_EMPTY),
			.FIFO_DATA(FIFO_DATA),

			.FIFO_NOT_EMPTY(),
			.FIFO_READ_ERROR(),
			.FIFO_FULL(),
			.FIFO_NEAR_FULL(FIFO_NEAR_FULL)
	);
	 
	wire [7:0] IO;
	gpio 
	#( 
			.BASEADDR(GPIO_BASEADDR), 
			.HIGHADDR(GPIO_HIGHADDR),
			.IO_WIDTH(8),
			.IO_DIRECTION(8'hff)
	) i_gpio
	(
			.BUS_CLK(BUS_CLK),
			.BUS_RST(BUS_RST),
			.BUS_ADD(BUS_ADD),
			.BUS_DATA(BUS_DATA),
			.BUS_RD(BUS_RD),
			.BUS_WR(BUS_WR),
			.IO(IO)
	);
     
	// IO 	
	 wire SOFT_RST;

	assign SOFT_RST = IO[6];
	assign EN_SEQ = IO[4];
	assign EN_OPA = IO[3];
	assign SEL2 = IO[2];
	assign SEL1 = IO[1];
	assign SEL0 = IO[0];
	
    // LED

	assign LED1 = 1;
    assign LED2 = IO[5]; 
	assign LED4 = IO[0]; // sel 0 
    assign LED5 = IO[1]; // sel 1 
	clock_divider #(.DIVISOR(40000000)) div2 ( .CLK(LCK1_BUF), .RESET(1'b0), .CLOCK(LED3) );

   // MULTI IOs for testing only 
	assign MULTI_IO[0] = SEQ_OUT[0]; //CLK_COMP
	assign MULTI_IO[1] = SEQ_OUT[1]; //CLK_SR 
	assign MULTI_IO[2] = SEQ_OUT[2]; //SAMPLE
	assign MULTI_IO[3] = SEQ_OUT[3]; //RST_B
	assign MULTI_IO[4] = SEQ_OUT[4]; //EN_RX
	assign MULTI_IO[5] = ADC_DATA;
	assign MULTI_IO[6] = CLK_SPI; 
	assign MULTI_IO[7] = EN_SEQ_SYNC; 
	assign MULTI_IO[8] = LCK1_BUF; 
	assign MULTI_IO[9] = 0; 
	

endmodule
