/**
 * ------------------------------------------------------------
 * Copyright (c) All rights reserved 
 * SiLab, Institute of Physics, University of Bonn
 * ------------------------------------------------------------
 */
 
 `timescale 1ns / 1ps
module clk_gen(
    input CLKIN,
    output wire BUS_CLK,
    output CLK160, 
    output SPI_CLK
    );

    wire GND_BIT;
    assign GND_BIT = 0;
    
		wire CLK0, CLK0_BUF;
		wire CLKDV, CLKFX, CLKFB_BUF;
		wire CLKIN_BUF;
		
    BUFG CLKIN_BUFG_INST (.I(CLKIN), .O(CLKIN_BUF));
    BUFG CLK0_BUFG_INST  (.I(CLK0),  .O(CLK0_BUF));
    BUFG CLKFB_BUFG_INST (.I(CLK0),  .O(CLKFB_BUF));
    BUFG CLKDV_BUFG_INST (.I(CLKDV), .O(SPI_CLK));
    BUFG CLKFX_BUFG_INST (.I(CLKFX), .O(CLK160));
		
		assign BUS_CLK = CLK0_BUF;
       
   
   DCM #(
         .CLKDV_DIVIDE(4.0), // Divide by: 1.5,2.0,2.5,3.0,3.5,4.0,4.5,5.0,5.5,6.0,6.5
         // 7.0,7.5,8.0,9.0,10.0,11.0,12.0,13.0,14.0,15.0 or 16.0
         .CLKFX_DIVIDE(3), // Can be any Integer from 1 to 32
         .CLKFX_MULTIPLY(10), // Can be any Integer from 2 to 32
         .CLKIN_DIVIDE_BY_2("FALSE"), // TRUE/FALSE to enable CLKIN divide by two feature
         .CLKIN_PERIOD(20.833), // Specify period of input clock
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
         ) DCM_BUS (
         .CLKFB(CLKFB_BUF), 
         .CLKIN(CLKIN_BUF), 
         .DSSEN(GND_BIT), 
         .PSCLK(GND_BIT), 
         .PSEN(GND_BIT), 
         .PSINCDEC(GND_BIT), 
         .RST(GND_BIT),
         .CLKDV(CLKDV),
         .CLKFX(CLKFX), 
         .CLKFX180(), 
         .CLK0(CLK0), 
         .CLK2X(), 
         .CLK2X180(), 
         .CLK90(), 
         .CLK180(), 
         .CLK270(), 
         .LOCKED(), 
         .PSDONE(), 
         .STATUS());
  

   
 
endmodule
