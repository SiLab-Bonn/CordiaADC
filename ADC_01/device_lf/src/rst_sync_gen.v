/**
 * ------------------------------------------------------------
 * Copyright (c) All rights reserved 
 * SiLab, Institute of Physics, University of Bonn
 * ------------------------------------------------------------
 */
 
 `timescale 1ps / 1ps

  module rst_sync_gen(
    input CLK,
    input RST,  
    output wire RST_SYNC_BUF
    );


reg RST_SYNC;

  always @(posedge CLK or posedge RST) begin
	 if (RST)     
      RST_SYNC <= 1'b1 ;
   else
      RST_SYNC <= 1'b0 ;          
     
  end


BUFG SOFT_RST_INST (.I(RST_SYNC), .O(RST_SYNC_BUF));
  

endmodule
