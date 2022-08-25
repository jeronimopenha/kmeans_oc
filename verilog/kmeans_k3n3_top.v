

module kmeans_k3n3_top #
(
  parameter input_data_width = 8,
  parameter input_data_qty_bit_width = 8,
  parameter input_data_qty = 256,
  parameter mem_d0_init_file = "./db/d0.txt",
  parameter mem_d1_init_file = "./db/d1.txt",
  parameter mem_d2_init_file = "./db/d2.txt",
  parameter k0_d0_initial = 0,
  parameter k0_d1_initial = 0,
  parameter k0_d2_initial = 0,
  parameter k1_d0_initial = 1,
  parameter k1_d1_initial = 1,
  parameter k1_d2_initial = 1,
  parameter k2_d0_initial = 2,
  parameter k2_d1_initial = 2,
  parameter k2_d2_initial = 2
)
(
  input clk,
  input rst,
  input start
);


  //Centroids regs
  reg [input_data_width-1:0] k0d0;
  reg [input_data_width-1:0] k0d1;
  reg [input_data_width-1:0] k0d2;
  reg [input_data_width-1:0] k1d0;
  reg [input_data_width-1:0] k1d1;
  reg [input_data_width-1:0] k1d2;
  reg [input_data_width-1:0] k2d0;
  reg [input_data_width-1:0] k2d1;
  reg [input_data_width-1:0] k2d2;

  //New centroids regs
  reg [input_data_width-1:0] new_k0d0;
  reg [input_data_width-1:0] new_k0d1;
  reg [input_data_width-1:0] new_k0d2;
  reg [input_data_width-1:0] new_k1d0;
  reg [input_data_width-1:0] new_k1d1;
  reg [input_data_width-1:0] new_k1d2;
  reg [input_data_width-1:0] new_k2d0;
  reg [input_data_width-1:0] new_k2d1;
  reg [input_data_width-1:0] new_k2d2;

  //Input data block

  //In this block we have N RAM memories. Each one contains data for one dimension
  wire [input_data_qty_bit_width-1:0] input_ram_rd_address;
  wire [input_data_width-1:0] d0;
  wire [input_data_width-1:0] d1;
  wire [input_data_width-1:0] d2;

  kmeans_input_data_block_3dim
  #(
    .input_data_width(input_data_width),
    .memory_depth_bits(input_data_qty_bit_width),
    .mem_d0_init_file(mem_d0_init_file),
    .mem_d1_init_file(mem_d1_init_file),
    .mem_d2_init_file(mem_d2_init_file)
  )
  kmeans_input_data_block_3dim
  (
    .clk(clk),
    .rd_address(input_ram_rd_address),
    .output_data0(d0),
    .output_data1(d1),
    .output_data2(d2)
  );


  //kmeans main pipeline
  wire [input_data_width-1:0] d0_to_acc;
  wire [input_data_width-1:0] d1_to_acc;
  wire [input_data_width-1:0] d2_to_acc;
  wire [2-1:0] selected_centroid;

  kmeans_pipeline_k3_d3
  kmeans_pipeline_k3_d3
  (
    .clk(clk),
    .centroid0_d0(k0d0),
    .centroid0_d1(k0d1),
    .centroid0_d2(k0d2),
    .centroid1_d0(k1d0),
    .centroid1_d1(k1d1),
    .centroid1_d2(k1d2),
    .centroid2_d0(k2d0),
    .centroid2_d1(k2d1),
    .centroid2_d2(k2d2),
    .input_data0(d0),
    .input_data1(d1),
    .input_data2(d2)
  );


  initial begin
    k0d0 = 0;
    k0d1 = 0;
    k0d2 = 0;
    k1d0 = 0;
    k1d1 = 0;
    k1d2 = 0;
    k2d0 = 0;
    k2d1 = 0;
    k2d2 = 0;
    new_k0d0 = 0;
    new_k0d1 = 0;
    new_k0d2 = 0;
    new_k1d0 = 0;
    new_k1d1 = 0;
    new_k1d2 = 0;
    new_k2d0 = 0;
    new_k2d1 = 0;
    new_k2d2 = 0;
  end


endmodule



module kmeans_input_data_block_3dim #
(
  parameter input_data_width = 8,
  parameter memory_depth_bits = 8,
  parameter mem_d0_init_file = "./db/d0.txt",
  parameter mem_d1_init_file = "./db/d1.txt",
  parameter mem_d2_init_file = "./db/d2.txt"
)
(
  input clk,
  input [memory_depth_bits-1:0] rd_address,
  output [input_data_width-1:0] output_data0,
  output [input_data_width-1:0] output_data1,
  output [input_data_width-1:0] output_data2
);


  RAM
  #(
    .read_f(1),
    .init_file(mem_d0_init_file),
    .write_f(0),
    .output_file("mem_out_file.txt"),
    .depth(memory_depth_bits),
    .width(input_data_width)
  )
  RAM_0
  (
    .clk(clk),
    .rd_addr(rd_address),
    .out(output_data0),
    .wr(1'd0),
    .wr_addr(8'd0),
    .wr_data(8'd0)
  );


  RAM
  #(
    .read_f(1),
    .init_file(mem_d1_init_file),
    .write_f(0),
    .output_file("mem_out_file.txt"),
    .depth(memory_depth_bits),
    .width(input_data_width)
  )
  RAM_1
  (
    .clk(clk),
    .rd_addr(rd_address),
    .out(output_data1),
    .wr(1'd0),
    .wr_addr(8'd0),
    .wr_data(8'd0)
  );


  RAM
  #(
    .read_f(1),
    .init_file(mem_d2_init_file),
    .write_f(0),
    .output_file("mem_out_file.txt"),
    .depth(memory_depth_bits),
    .width(input_data_width)
  )
  RAM_2
  (
    .clk(clk),
    .rd_addr(rd_address),
    .out(output_data2),
    .wr(1'd0),
    .wr_addr(8'd0),
    .wr_data(8'd0)
  );


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

    //synthesis translate_off

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

    //synthesis translate_on

endmodule



module kmeans_pipeline_k3_d3 #
(
  parameter input_data_width = 8
)
(
  input clk,
  input [input_data_width-1:0] centroid0_d0,
  input [input_data_width-1:0] centroid0_d1,
  input [input_data_width-1:0] centroid0_d2,
  input [input_data_width-1:0] centroid1_d0,
  input [input_data_width-1:0] centroid1_d1,
  input [input_data_width-1:0] centroid1_d2,
  input [input_data_width-1:0] centroid2_d0,
  input [input_data_width-1:0] centroid2_d1,
  input [input_data_width-1:0] centroid2_d2,
  input [input_data_width-1:0] input_data0,
  input [input_data_width-1:0] input_data1,
  input [input_data_width-1:0] input_data2,
  output [input_data_width-1:0] output_data0,
  output [input_data_width-1:0] output_data1,
  output [input_data_width-1:0] output_data2,
  output [2-1:0] selected_centroid
);

  //Latency delay
  //1(sub) + 1(sqr) + ceil(log2(dimensions_qty)) (add) + ceil(log2(centroids_qty)) (comp)
  //for this one it is 6

  //pipeline stage 0 - Sub
  reg [input_data_width-1:0] sub_k0_d0_st0;
  reg [input_data_width-1:0] sub_k0_d1_st0;
  reg [input_data_width-1:0] sub_k0_d2_st0;
  reg [input_data_width-1:0] sub_k1_d0_st0;
  reg [input_data_width-1:0] sub_k1_d1_st0;
  reg [input_data_width-1:0] sub_k1_d2_st0;
  reg [input_data_width-1:0] sub_k2_d0_st0;
  reg [input_data_width-1:0] sub_k2_d1_st0;
  reg [input_data_width-1:0] sub_k2_d2_st0;

  //pipeline stage 1 - Sqr
  reg [input_data_width*2-1:0] sqr_k0_d0_st1;
  reg [input_data_width*2-1:0] sqr_k0_d1_st1;
  reg [input_data_width*2-1:0] sqr_k0_d2_st1;
  reg [input_data_width*2-1:0] sqr_k1_d0_st1;
  reg [input_data_width*2-1:0] sqr_k1_d1_st1;
  reg [input_data_width*2-1:0] sqr_k1_d2_st1;
  reg [input_data_width*2-1:0] sqr_k2_d0_st1;
  reg [input_data_width*2-1:0] sqr_k2_d1_st1;
  reg [input_data_width*2-1:0] sqr_k2_d2_st1;

  //pipeline Add reduction - 2 stages
  //we needed to add 2b to the add witdh because we need ceil(log2(reduction_stages)) + 1 to don´t have overflow
  reg [input_data_width*2+2-1:0] add0_k0_st2;
  reg [input_data_width*2+2-1:0] add1_k0_st2;
  reg [input_data_width*2+2-1:0] add2_k0_st3;
  reg [input_data_width*2+2-1:0] add0_k1_st2;
  reg [input_data_width*2+2-1:0] add1_k1_st2;
  reg [input_data_width*2+2-1:0] add2_k1_st3;
  reg [input_data_width*2+2-1:0] add0_k2_st2;
  reg [input_data_width*2+2-1:0] add1_k2_st2;
  reg [input_data_width*2+2-1:0] add2_k2_st3;

  //pipeline comp reduction - 2 stages. Centroid idx propagation
  reg [2-1:0] cmp0_idx_st4;
  reg [2-1:0] cmp1_idx_st4;
  reg [2-1:0] cmp2_idx_st5;

  //pipeline comp reduction - 2 stages. Centroid add reduction propagation
  //The last stage of these regs are only for depuration. When in synthesys they will be automatically removed
  reg [input_data_width*2+2-1:0] cmp0_data_st4;
  reg [input_data_width*2+2-1:0] cmp1_data_st4;
  reg [input_data_width*2+2-1:0] cmp2_data_st5;

  //Output assigns
  assign selected_centroid = cmp2_idx_st5;

  always @(posedge clk) begin
    sub_k0_d0_st0 <= centroid0_d0 - input_data0;
    sub_k0_d1_st0 <= centroid0_d1 - input_data1;
    sub_k0_d2_st0 <= centroid0_d2 - input_data2;
    sub_k1_d0_st0 <= centroid1_d0 - input_data0;
    sub_k1_d1_st0 <= centroid1_d1 - input_data1;
    sub_k1_d2_st0 <= centroid1_d2 - input_data2;
    sub_k2_d0_st0 <= centroid2_d0 - input_data0;
    sub_k2_d1_st0 <= centroid2_d1 - input_data1;
    sub_k2_d2_st0 <= centroid2_d2 - input_data2;
    sqr_k0_d0_st1 <= sub_k0_d0_st0 * sub_k0_d0_st0;
    sqr_k0_d1_st1 <= sub_k0_d1_st0 * sub_k0_d1_st0;
    sqr_k0_d2_st1 <= sub_k0_d2_st0 * sub_k0_d2_st0;
    sqr_k1_d0_st1 <= sub_k1_d0_st0 * sub_k1_d0_st0;
    sqr_k1_d1_st1 <= sub_k1_d1_st0 * sub_k1_d1_st0;
    sqr_k1_d2_st1 <= sub_k1_d2_st0 * sub_k1_d2_st0;
    sqr_k2_d0_st1 <= sub_k2_d0_st0 * sub_k2_d0_st0;
    sqr_k2_d1_st1 <= sub_k2_d1_st0 * sub_k2_d1_st0;
    sqr_k2_d2_st1 <= sub_k2_d2_st0 * sub_k2_d2_st0;
    add0_k0_st2 <= sqr_k0_d0_st1 + sqr_k0_d1_st1;
    add0_k1_st2 <= sqr_k1_d0_st1 + sqr_k1_d1_st1;
    add0_k2_st2 <= sqr_k2_d0_st1 + sqr_k2_d1_st1;
    add1_k0_st2 <= sqr_k0_d2_st1;
    add1_k1_st2 <= sqr_k1_d2_st1;
    add1_k2_st2 <= sqr_k2_d2_st1;
    add2_k0_st3 <= add0_k0_st2 + add1_k0_st2;
    add2_k1_st3 <= add0_k1_st2 + add1_k1_st2;
    add2_k2_st3 <= add0_k2_st2 + add1_k2_st2;
    cmp0_idx_st4 <= (add2_k0_st3 < add2_k1_st3)? 2'd0 : 2'd1;
    cmp0_data_st4 <= (add2_k0_st3 < add2_k1_st3)? add2_k0_st3 : add2_k1_st3;
    cmp1_idx_st4 <= 2'd2;
    cmp1_data_st4 <= add2_k2_st3;
    cmp2_idx_st5 <= (cmp0_data_st4 < cmp1_data_st4)? cmp0_idx_st4 : cmp1_idx_st4;
    cmp2_data_st5 <= (cmp0_data_st4 < cmp1_data_st4)? cmp0_data_st4 : cmp1_data_st4;
  end


  //Input data propagation pipeline
  reg [input_data_width-1:0] data_prop_d0_st0;
  reg [input_data_width-1:0] data_prop_d1_st0;
  reg [input_data_width-1:0] data_prop_d2_st0;
  reg [input_data_width-1:0] data_prop_d0_st1;
  reg [input_data_width-1:0] data_prop_d1_st1;
  reg [input_data_width-1:0] data_prop_d2_st1;
  reg [input_data_width-1:0] data_prop_d0_st2;
  reg [input_data_width-1:0] data_prop_d1_st2;
  reg [input_data_width-1:0] data_prop_d2_st2;
  reg [input_data_width-1:0] data_prop_d0_st3;
  reg [input_data_width-1:0] data_prop_d1_st3;
  reg [input_data_width-1:0] data_prop_d2_st3;
  reg [input_data_width-1:0] data_prop_d0_st4;
  reg [input_data_width-1:0] data_prop_d1_st4;
  reg [input_data_width-1:0] data_prop_d2_st4;
  reg [input_data_width-1:0] data_prop_d0_st5;
  reg [input_data_width-1:0] data_prop_d1_st5;
  reg [input_data_width-1:0] data_prop_d2_st5;

  //Output assigns
  assign output_data0 = data_prop_d0_st5;
  assign output_data1 = data_prop_d1_st5;
  assign output_data2 = data_prop_d2_st5;

  always @(posedge clk) begin
    data_prop_d0_st0 <= input_data0;
    data_prop_d1_st0 <= input_data1;
    data_prop_d2_st0 <= input_data2;
    data_prop_d0_st1 <= data_prop_d0_st0;
    data_prop_d1_st1 <= data_prop_d1_st0;
    data_prop_d2_st1 <= data_prop_d2_st0;
    data_prop_d0_st2 <= data_prop_d0_st1;
    data_prop_d1_st2 <= data_prop_d1_st1;
    data_prop_d2_st2 <= data_prop_d2_st1;
    data_prop_d0_st3 <= data_prop_d0_st2;
    data_prop_d1_st3 <= data_prop_d1_st2;
    data_prop_d2_st3 <= data_prop_d2_st2;
    data_prop_d0_st4 <= data_prop_d0_st3;
    data_prop_d1_st4 <= data_prop_d1_st3;
    data_prop_d2_st4 <= data_prop_d2_st3;
    data_prop_d0_st5 <= data_prop_d0_st4;
    data_prop_d1_st5 <= data_prop_d1_st4;
    data_prop_d2_st5 <= data_prop_d2_st4;
  end


  initial begin
    sub_k0_d0_st0 = 0;
    sub_k0_d1_st0 = 0;
    sub_k0_d2_st0 = 0;
    sub_k1_d0_st0 = 0;
    sub_k1_d1_st0 = 0;
    sub_k1_d2_st0 = 0;
    sub_k2_d0_st0 = 0;
    sub_k2_d1_st0 = 0;
    sub_k2_d2_st0 = 0;
    sqr_k0_d0_st1 = 0;
    sqr_k0_d1_st1 = 0;
    sqr_k0_d2_st1 = 0;
    sqr_k1_d0_st1 = 0;
    sqr_k1_d1_st1 = 0;
    sqr_k1_d2_st1 = 0;
    sqr_k2_d0_st1 = 0;
    sqr_k2_d1_st1 = 0;
    sqr_k2_d2_st1 = 0;
    add0_k0_st2 = 0;
    add1_k0_st2 = 0;
    add2_k0_st3 = 0;
    add0_k1_st2 = 0;
    add1_k1_st2 = 0;
    add2_k1_st3 = 0;
    add0_k2_st2 = 0;
    add1_k2_st2 = 0;
    add2_k2_st3 = 0;
    cmp0_idx_st4 = 0;
    cmp1_idx_st4 = 0;
    cmp2_idx_st5 = 0;
    cmp0_data_st4 = 0;
    cmp1_data_st4 = 0;
    cmp2_data_st5 = 0;
    data_prop_d0_st0 = 0;
    data_prop_d1_st0 = 0;
    data_prop_d2_st0 = 0;
    data_prop_d0_st1 = 0;
    data_prop_d1_st1 = 0;
    data_prop_d2_st1 = 0;
    data_prop_d0_st2 = 0;
    data_prop_d1_st2 = 0;
    data_prop_d2_st2 = 0;
    data_prop_d0_st3 = 0;
    data_prop_d1_st3 = 0;
    data_prop_d2_st3 = 0;
    data_prop_d0_st4 = 0;
    data_prop_d1_st4 = 0;
    data_prop_d2_st4 = 0;
    data_prop_d0_st5 = 0;
    data_prop_d1_st5 = 0;
    data_prop_d2_st5 = 0;
  end


endmodule
