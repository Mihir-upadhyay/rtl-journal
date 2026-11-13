module flippy_bits (
    input  logic clk,
    input  logic resetn,
    output logic bit_out
);

    logic [31:0] count;

    always_ff @(posedge clk) begin
        if (!resetn) begin
            count   <= 32'd0;
            bit_out <= 1'b0;
        end else begin
            bit_out <= ^count;
            count   <= count + 32'd1;
        end
    end

endmodule