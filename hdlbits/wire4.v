module top_module( 
    input a,b,c,
    output w,x,y,z );

wire w1, w2, w3;

assign w1 = a;
assign w2 = b;
assign w3 = c;

assign w = w1;
assign x = w2;
assign y = w2;
assign z = w3;

endmodule
