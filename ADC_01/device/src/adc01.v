/**
 * ------------------------------------------------------------
 * Copyright (c) All rights reserved 
 * SiLab, Institute of Physics, University of Bonn
 * ------------------------------------------------------------
 */
 
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
	 input wire LCK1, // PLL EXT CLK
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
    wire BUS_CLK;
     		
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
        .CLK160(),
        .SPI_CLK()
    ); 

    // global soft reset 

	    			   

   
    // CLK generation and control 

    wire CLK_SPI; 
	wire CLK_MAIN;
	wire CLK_MAIN_BUF;
	wire CLK_MAIN_180;
	wire CLK_MAIN_DIV_2_OUT;
	wire CLK_MAIN_DIV_2_OUT_BUF;
	wire CLK_MAIN_DIV_2;
	wire CLK_MAIN_DIV_2_BUF;
    wire CLK_SPI_BUF; 
    (* KEEP = "{TRUE}" *)  wire LCK1_BUF;   		
    wire GND_BIT;
    assign GND_BIT = 0;

	BUFG LCK1_BUFG_INST (.I(LCK1), .O(LCK1_BUF));  // clock from external PLL chip
    BUFG LCK2_BUFG_INST (.I(CLK_MAIN), .O(CLK_MAIN_BUF)); 
    BUFG LCK3_BUFG_INST (.I(CLK_SPI), .O(CLK_SPI_BUF));
	BUFG LCK4_BUFG_INST (.I(CLK_MAIN_DIV_2_OUT), .O(CLK_MAIN_DIV_2_OUT_BUF));
    BUFG LCK5_BUFG_INST (.I(CLK_MAIN_DIV_2), .O(CLK_MAIN_DIV_2_BUF));


    wire SOFT_RST;
   

    // Main CLK 

  		 DCM #(
  		.CLKDV_DIVIDE(2), // Divide by: 1.5,2.0,2.5,3.0,3.5,4.0,4.5,5.0,5.5,6.0,6.5
  		// 7.0,7.5,8.0,9.0,10.0,11.0,12.0,13.0,14.0,15.0 or 16.0
  		.CLKFX_DIVIDE(1), // Can be any Integer from 1 to 32
  		.CLKFX_MULTIPLY(2), // Can be any Integer from 2 to 32
  		.CLKIN_DIVIDE_BY_2("FALSE"), // TRUE/FALSE to enable CLKIN divide by two feature
  		.CLKIN_PERIOD(10), // Specify period of input clock
  		.CLKOUT_PHASE_SHIFT("NONE"), // Specify phase shift of NONE, FIXED or VARIABLE
  		.CLK_FEEDBACK("1X"), // Specify clock feedback of NONE, 1X or 2X
  		.DESKEW_ADJUST("SYSTEM_SYNCHRONOUS"), // SOURCE_SYNCHRONOUS, SYSTEM_SYNCHRONOUS or
  		// an Integer from 0 to 15
  		.DFS_FREQUENCY_MODE("LOW"), // HIGH or LOW frequency mode for frequency synthesis
  		.DLL_FREQUENCY_MODE("LOW"), // HIGH or LOW frequency mode for DLL
  		.DUTY_CYCLE_CORRECTION("TRUE"), // Duty cycle correction, TRUE or FALSE
  		.FACTORY_JF(16'h8080), // FACTORY JF values
  		.PHASE_SHIFT(0), // Amount of fixed phase shift from -255 to 255
  		.STARTUP_WAIT("TRUE") // Delay configuration DONE until DCM_SP LOCK, TRUE/FALSE
  		) i_DCM_CLK_MAIN (
  		.CLKFB(CLK_MAIN_BUF), 
  		.CLKIN(LCK1_BUF), 
  		.DSSEN(GND_BIT), 
  		.PSCLK(GND_BIT), 
  		.PSEN(GND_BIT), 
  		.PSINCDEC(GND_BIT), 
  		.RST(SOFT_RST),
  		.CLKDV(CLK_MAIN_DIV_2),
  		.CLKFX(), 
  		.CLKFX180(), // Fout = Fin * MULTIPLY factor / DIVIDE factor 
  		.CLK0(CLK_MAIN), 
  		.CLK2X(), 
  		.CLK2X180(), 
  		.CLK90(), 
  		.CLK180(CLK_MAIN_180), 
  		.CLK270(), 
  		.LOCKED(LED4), 
  		.PSDONE(), 
  		.STATUS()
		 );
   
   // SPI CLK
   
		  DCM #(
		 .CLKDV_DIVIDE(2), // Divide by: 1.5,2.0,2.5,3.0,3.5,4.0,4.5,5.0,5.5,6.0,6.5
		 // 7.0,7.5,8.0,9.0,10.0,11.0,12.0,13.0,14.0,15.0 or 16.0
		 .CLKFX_DIVIDE(1), // Can be any Integer from 1 to 32
		 .CLKFX_MULTIPLY(2), // Can be any Integer from 2 to 32
		 .CLKIN_DIVIDE_BY_2("FALSE"), // TRUE/FALSE to enable CLKIN divide by two feature
		 .CLKIN_PERIOD(10), // Specify period of input clock
		 .CLKOUT_PHASE_SHIFT("NONE"), // Specify phase shift of NONE, FIXED or VARIABLE
		 .CLK_FEEDBACK("1X"), // Specify clock feedback of NONE, 1X or 2X
		 .DESKEW_ADJUST("SYSTEM_SYNCHRONOUS"), // SOURCE_SYNCHRONOUS, SYSTEM_SYNCHRONOUS or
		 // an Integer from 0 to 15
		 .DFS_FREQUENCY_MODE("LOW"), // HIGH or LOW frequency mode for frequency synthesis
		 .DLL_FREQUENCY_MODE("LOW"), // HIGH or LOW frequency mode for DLL
		 .DUTY_CYCLE_CORRECTION("TRUE"), // Duty cycle correction, TRUE or FALSE
		 .FACTORY_JF(16'h8080), // FACTORY JF values
		 .PHASE_SHIFT(0), // Amount of fixed phase shift from -255 to 255
		 .STARTUP_WAIT("TRUE") // Delay configuration DONE until DCM_SP LOCK, TRUE/FALSE
		 ) i_DCM_CLK_SPI (
		 .CLKFB(CLK_MAIN_DIV_2_OUT_BUF), 
		 .CLKIN(CLK_MAIN_DIV_2_BUF), 
		 .DSSEN(GND_BIT), 
		 .PSCLK(GND_BIT), 
		 .PSEN(GND_BIT), 
		 .PSINCDEC(GND_BIT), 
		 .RST(SOFT_RST),
		 .CLKDV(),
		 .CLKFX(), 
		 .CLKFX180(), // Fout = Fin * MULTIPLY factor / DIVIDE factor 
		 .CLK0(CLK_MAIN_DIV_2_OUT), 
		 .CLK2X(), 
		 .CLK2X180(), 
		 .CLK90(CLK_SPI), 
		 .CLK180(), 
		 .CLK270(), 
		 .LOCKED(LED5), 
		 .PSDONE(), 
		 .STATUS()
		); 



   
	
   
    
// end CLK gen. and cntr 

    reg EN_SEQ_SYNC;
	always @(posedge CLK_MAIN_DIV_2_BUF) begin
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
        .SEQ_CLK(CLK_MAIN_BUF),
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
			
			.SCLK(CLK_SPI_BUF),
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
   
	

	assign SOFT_RST = IO[6];
	assign EN_SEQ = IO[4];
	assign EN_OPA = IO[3];
	assign SEL2 = IO[2];
	assign SEL1 = IO[1];
	assign SEL0 = IO[0];
	
    
	

   /*  rst_sync_gen  i_rst_sync_gen( */
   /*   .CLK(LCK1_BUF), */
	/*  .RST(SOFT_RST), */
	/*  .RST_SYNC_BUF(RST_SYNC_BUF) */
   /*  ); */

  
    // LED

	assign LED1 = 1;
    assign LED2 = IO[5]; 
	//assign LED4 = IO[0]; // sel 0 
    //assign LED5 = IO[1]; // sel 1 
	clock_divider #(.DIVISOR(40000000)) div2 ( .CLK(LCK1_BUF), .RESET(1'b0), .CLOCK(LED3) );

   // MULTI IOs for testing only 
	assign MULTI_IO[0] = SEQ_OUT[0]; //CLK_COMP
	assign MULTI_IO[1] = SEQ_OUT[1]; //CLK_SR 
	assign MULTI_IO[2] = SEQ_OUT[2]; //SAMPLE
	assign MULTI_IO[3] = SEQ_OUT[3]; //RST_B
	assign MULTI_IO[4] = SEQ_OUT[4]; //EN_RX
	assign MULTI_IO[5] = ADC_DATA;
	assign MULTI_IO[6] = CLK_SPI_BUF; 
	assign MULTI_IO[7] = EN_SEQ_SYNC; 
	assign MULTI_IO[8] = CLK_MAIN_BUF; 
	assign MULTI_IO[9] = LCK1_BUF; 
	


endmodule
