module growing_pulse (
    input  logic clk,
    input  logic resetn,
    output logic pulse
);

    logic [31:0] count;   // cycles remaining in current interval after this one
    logic [31:0] target;  // length of the current interval

    always_ff @(posedge clk) begin
        if (!resetn) begin
            pulse  <= 1'b0;
            count  <= 32'd1;   // was 0: first low interval starts after reset release
            target <= 32'd1;
        end else if (count == 32'd0) begin
            pulse <= ~pulse;
            if (pulse) begin               // high -> low: length grows by 1
                target <= target + 32'd1;
                count  <= target;          // (target + 1) - 1
            end else begin                 // low -> high: same length as the low
                count  <= target - 32'd1;
            end
        end else begin
            count <= count - 32'd1;
        end
    end

endmodule