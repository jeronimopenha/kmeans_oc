

module kmeans_k2n2_top #
(
  parameter mem_d0_init_file = "./db/d0.txt",
  parameter mem_d1_init_file = "./db/d1.txt",
  parameter data_width = 16,
  parameter n_input_data_b_depth = 8,
  parameter n_input_data = 256,
  parameter [data_width-1:0] p_k0_0 = 0,
  parameter [data_width-1:0] p_k0_1 = 0,
  parameter [data_width-1:0] p_k1_0 = 1,
  parameter [data_width-1:0] p_k1_1 = 1
)
(
  input clk,
  input rst,
  input start
);

  //Centroids regs - begin
  reg [data_width-1:0] k0_0;
  reg [data_width-1:0] k0_1;
  reg [data_width-1:0] k1_0;
  reg [data_width-1:0] k1_1;
  //Centroids regs - end

  //input data memories regs and wires - begin
  wire [n_input_data_b_depth-1:0] mem_d0_rd_addr;
  wire [data_width-1:0] mem_d0_out;
  wire [n_input_data_b_depth-1:0] mem_d1_rd_addr;
  wire [data_width-1:0] mem_d1_out;
  //input data memories regs and wires - end

  //kmeans pipeline (kp) wires and regs - begin
  //data input
  wire [data_width-1:0] kp_d0;
  wire [data_width-1:0] kp_d1;
  //centroids
  wire [data_width-1:0] kp_k0_0;
  wire [data_width-1:0] kp_k0_1;
  wire [data_width-1:0] kp_k1_0;
  wire [data_width-1:0] kp_k1_1;
  //st1 outputs - sub data kx
  reg [data_width-1:0] kp_st0_sub00;
  reg [data_width-1:0] kp_st0_sub01;
  reg [data_width-1:0] kp_st0_sub10;
  reg [data_width-1:0] kp_st0_sub11;
  reg [data_width-1:0] kp_st0_d0;
  reg [data_width-1:0] kp_st0_d1;
  //st1 outputs - sqr
  reg [data_width*2-1:0] kp_st1_sqr00;
  reg [data_width*2-1:0] kp_st1_sqr01;
  reg [data_width*2-1:0] kp_st1_sqr10;
  reg [data_width*2-1:0] kp_st1_sqr11;
  reg [data_width-1:0] kp_st1_d0;
  reg [data_width-1:0] kp_st1_d1;
  //st2 outputs - add
  reg [data_width*2+1-1:0] kp_st2_add0;
  reg [data_width*2+1-1:0] kp_st2_add1;
  reg [data_width-1:0] kp_st2_d0;
  reg [data_width-1:0] kp_st2_d1;
  //st3 outputs - kmeans decision
  reg [data_width-1:0] kp_st3_d0_out;
  reg [data_width-1:0] kp_st3_d1_out;
  reg kp_st3_k_out;
  //kmeans pipeline (kp) wires and regs - end

  //Implementation - begin

  //centroids values control - begin

  always @(posedge clk) begin
    if(rst) begin
      k0_0 <= p_k0_0;
      k0_1 <= p_k0_1;
      k1_0 <= p_k1_0;
      k1_1 <= p_k1_1;
    end 
  end

  //centroids values control - end

  //kmeans pipeline (kp) implementation - begin
  assign kp_k0_0 = k0_0;
  assign kp_k0_1 = k0_1;
  assign kp_k1_0 = k1_0;
  assign kp_k1_1 = k1_1;
  assign kp_d0 = mem_d0_out;
  assign kp_d1 = mem_d1_out;

  always @(posedge clk) begin
    kp_st0_sub00 <= kp_d0 - kp_k0_0;
    kp_st0_sub01 <= kp_d1 - kp_k0_1;
    kp_st0_sub10 <= kp_d0 - kp_k1_0;
    kp_st0_sub11 <= kp_d1 - kp_k1_1;
    kp_st0_d0 <= kp_d0;
    kp_st0_d1 <= kp_d1;
    kp_st1_sqr00 <= kp_st0_sub00 * kp_st0_sub00;
    kp_st1_sqr01 <= kp_st0_sub01 * kp_st0_sub01;
    kp_st1_sqr10 <= kp_st0_sub10 * kp_st0_sub10;
    kp_st1_sqr11 <= kp_st0_sub11 * kp_st0_sub11;
    kp_st1_d0 <= kp_st0_d0;
    kp_st1_d1 <= kp_st0_d1;
    kp_st2_add0 <= kp_st1_sqr00 + kp_st1_sqr01;
    kp_st2_add1 <= kp_st1_sqr10 + kp_st1_sqr11;
    kp_st2_d0 <= kp_st1_d0;
    kp_st2_d1 <= kp_st1_d1;
    kp_st3_k_out <= (kp_st2_add0 < kp_st2_add1)? 0 : 1;
    kp_st3_d0_out <= kp_st2_d0;
    kp_st3_d1_out <= kp_st2_d1;
  end

  //kmeans pipeline (kp) implementation - end

  //Implementation - end

  //Modules instantiation - begin

  //kmeans input data memories - begin
  //d0 memory

  RAM
  #(
    .init_file(mem_d0_init_file),
    .write_f(1'b0),
    .depth(n_input_data_b_depth),
    .width(data_width)
  )
  RAM_d0
  (
    .clk(clk),
    .rd_addr(mem_d0_rd_addr),
    .out(mem_d0_out)
  );

  //d1 memory

  RAM
  #(
    .init_file(mem_d1_init_file),
    .write_f(1'b0),
    .depth(n_input_data_b_depth),
    .width(data_width)
  )
  RAM_d1
  (
    .clk(clk),
    .rd_addr(mem_d1_rd_addr),
    .out(mem_d1_out)
  );


  //kmeans input data memories - end

  //Modules instantiation - end

  initial begin
    k0_0 = 0;
    k0_1 = 0;
    k1_0 = 0;
    k1_1 = 0;
    kp_st0_sub00 = 0;
    kp_st0_sub01 = 0;
    kp_st0_sub10 = 0;
    kp_st0_sub11 = 0;
    kp_st0_d0 = 0;
    kp_st0_d1 = 0;
    kp_st1_sqr00 = 0;
    kp_st1_sqr01 = 0;
    kp_st1_sqr10 = 0;
    kp_st1_sqr11 = 0;
    kp_st1_d0 = 0;
    kp_st1_d1 = 0;
    kp_st2_add0 = 0;
    kp_st2_add1 = 0;
    kp_st2_d0 = 0;
    kp_st2_d1 = 0;
    kp_st3_d0_out = 0;
    kp_st3_d1_out = 0;
    kp_st3_k_out = 0;
  end


endmodule



module RAM #
(
  parameter read_f = 0,
  parameter init_file = "mem_file.txt",
  parameter write_f = 0,
  parameter output_file = "mem_out_file.txt",
  parameter depth = 8,
  parameter width = 16
)
(
  input clk,
  input [depth-1:0] rd_addr,
  output [width-1:0] out,
  input wr,
  input [depth-1:0] wr_addr,
  input [width-1:0] wr_data
);

  reg [width-1:0] mem [0:2**depth-1];
  assign out = mem[rd_addr];

  always @(posedge clk) begin
    if(wr) begin
      mem[wr_addr] <= wr_data;
    end 
  end


  always @(posedge clk) begin
    if(wr && write_f) begin
      $writememh(output_file, mem);
    end 
  end


  initial begin
    if(read_f) begin
      $readmemh(init_file, mem);
    end 
  end


endmodule

