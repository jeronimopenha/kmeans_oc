

module kmeans_k2n5_top #
(
  parameter input_data_width = 8,
  parameter input_data_qty_bit_width = 8,
  parameter input_data_qty = 256,
  parameter mem_d0_init_file = "./db/d0.txt",
  parameter mem_d1_init_file = "./db/d1.txt",
  parameter mem_d2_init_file = "./db/d2.txt",
  parameter mem_d3_init_file = "./db/d3.txt",
  parameter mem_d4_init_file = "./db/d4.txt",
  parameter k0_d0_initial = 0,
  parameter k0_d1_initial = 0,
  parameter k0_d2_initial = 0,
  parameter k0_d3_initial = 0,
  parameter k0_d4_initial = 0,
  parameter k1_d0_initial = 1,
  parameter k1_d1_initial = 1,
  parameter k1_d2_initial = 1,
  parameter k1_d3_initial = 1,
  parameter k1_d4_initial = 1
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
  reg [input_data_width-1:0] k0d3;
  reg [input_data_width-1:0] k0d4;
  reg [input_data_width-1:0] k1d0;
  reg [input_data_width-1:0] k1d1;
  reg [input_data_width-1:0] k1d2;
  reg [input_data_width-1:0] k1d3;
  reg [input_data_width-1:0] k1d4;

  //New centroids regs
  reg [input_data_width-1:0] new_k0d0;
  reg [input_data_width-1:0] new_k0d1;
  reg [input_data_width-1:0] new_k0d2;
  reg [input_data_width-1:0] new_k0d3;
  reg [input_data_width-1:0] new_k0d4;
  reg [input_data_width-1:0] new_k1d0;
  reg [input_data_width-1:0] new_k1d1;
  reg [input_data_width-1:0] new_k1d2;
  reg [input_data_width-1:0] new_k1d3;
  reg [input_data_width-1:0] new_k1d4;

  //Input data block

  //In this block we have N RAM memories. Each one contains data for one dimension
  wire [input_data_qty_bit_width-1:0] input_ram_rd_address;
  wire [input_data_width-1:0] d0;
  wire [input_data_width-1:0] d1;
  wire [input_data_width-1:0] d2;
  wire [input_data_width-1:0] d3;
  wire [input_data_width-1:0] d4;

  kmeans_input_data_block_5dim
  #(
    .input_data_width(input_data_width),
    .memory_depth_bits(input_data_qty_bit_width),
    .mem_d0_init_file(mem_d0_init_file),
    .mem_d1_init_file(mem_d1_init_file),
    .mem_d2_init_file(mem_d2_init_file),
    .mem_d3_init_file(mem_d3_init_file),
    .mem_d4_init_file(mem_d4_init_file)
  )
  kmeans_input_data_block_5dim
  (
    .clk(clk),
    .rd_address(input_ram_rd_address),
    .output_data0(d0),
    .output_data1(d1),
    .output_data2(d2),
    .output_data3(d3),
    .output_data4(d4)
  );


  //kmeans main pipeline
  wire [input_data_width-1:0] d0_to_acc;
  wire [input_data_width-1:0] d1_to_acc;
  wire [input_data_width-1:0] d2_to_acc;
  wire [input_data_width-1:0] d3_to_acc;
  wire [input_data_width-1:0] d4_to_acc;
  wire [1-1:0] selected_centroid;

  kmeans_pipeline_k2_d5
  kmeans_pipeline_k2_d5
  (
    .clk(clk),
    .centroid0_d0(k0d0),
    .centroid0_d1(k0d1),
    .centroid0_d2(k0d2),
    .centroid0_d3(k0d3),
    .centroid0_d4(k0d4),
    .centroid1_d0(k1d0),
    .centroid1_d1(k1d1),
    .centroid1_d2(k1d2),
    .centroid1_d3(k1d3),
    .centroid1_d4(k1d4),
    .input_data0(d0),
    .input_data1(d1),
    .input_data2(d2),
    .input_data3(d3),
    .input_data4(d4)
  );


  initial begin
    k0d0 = 0;
    k0d1 = 0;
    k0d2 = 0;
    k0d3 = 0;
    k0d4 = 0;
    k1d0 = 0;
    k1d1 = 0;
    k1d2 = 0;
    k1d3 = 0;
    k1d4 = 0;
    new_k0d0 = 0;
    new_k0d1 = 0;
    new_k0d2 = 0;
    new_k0d3 = 0;
    new_k0d4 = 0;
    new_k1d0 = 0;
    new_k1d1 = 0;
    new_k1d2 = 0;
    new_k1d3 = 0;
    new_k1d4 = 0;
  end


endmodule



module kmeans_input_data_block_5dim #
(
  parameter input_data_width = 8,
  parameter memory_depth_bits = 8,
  parameter mem_d0_init_file = "./db/d0.txt",
  parameter mem_d1_init_file = "./db/d1.txt",
  parameter mem_d2_init_file = "./db/d2.txt",
  parameter mem_d3_init_file = "./db/d3.txt",
  parameter mem_d4_init_file = "./db/d4.txt"
)
(
  input clk,
  input [memory_depth_bits-1:0] rd_address,
  output [input_data_width-1:0] output_data0,
  output [input_data_width-1:0] output_data1,
  output [input_data_width-1:0] output_data2,
  output [input_data_width-1:0] output_data3,
  output [input_data_width-1:0] output_data4
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


  RAM
  #(
    .read_f(1),
    .init_file(mem_d3_init_file),
    .write_f(0),
    .output_file("mem_out_file.txt"),
    .depth(memory_depth_bits),
    .width(input_data_width)
  )
  RAM_3
  (
    .clk(clk),
    .rd_addr(rd_address),
    .out(output_data3),
    .wr(1'd0),
    .wr_addr(8'd0),
    .wr_data(8'd0)
  );


  RAM
  #(
    .read_f(1),
    .init_file(mem_d4_init_file),
    .write_f(0),
    .output_file("mem_out_file.txt"),
    .depth(memory_depth_bits),
    .width(input_data_width)
  )
  RAM_4
  (
    .clk(clk),
    .rd_addr(rd_address),
    .out(output_data4),
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



module kmeans_pipeline_k2_d5 #
(
  parameter input_data_width = 8
)
(
  input clk,
  input [input_data_width-1:0] centroid0_d0,
  input [input_data_width-1:0] centroid0_d1,
  input [input_data_width-1:0] centroid0_d2,
  input [input_data_width-1:0] centroid0_d3,
  input [input_data_width-1:0] centroid0_d4,
  input [input_data_width-1:0] centroid1_d0,
  input [input_data_width-1:0] centroid1_d1,
  input [input_data_width-1:0] centroid1_d2,
  input [input_data_width-1:0] centroid1_d3,
  input [input_data_width-1:0] centroid1_d4,
  input [input_data_width-1:0] input_data0,
  input [input_data_width-1:0] input_data1,
  input [input_data_width-1:0] input_data2,
  input [input_data_width-1:0] input_data3,
  input [input_data_width-1:0] input_data4,
  output [input_data_width-1:0] output_data0,
  output [input_data_width-1:0] output_data1,
  output [input_data_width-1:0] output_data2,
  output [input_data_width-1:0] output_data3,
  output [input_data_width-1:0] output_data4,
  output [1-1:0] selected_centroid
);

  //Latency delay
  //1(sub) + 1(sqr) + ceil(log2(dimensions_qty)) (add) + ceil(log2(centroids_qty)) (comp)
  //for this one it is 6

  //pipeline stage 0 - Sub
  reg [input_data_width-1:0] sub_k0_d0_st0;
  reg [input_data_width-1:0] sub_k0_d1_st0;
  reg [input_data_width-1:0] sub_k0_d2_st0;
  reg [input_data_width-1:0] sub_k0_d3_st0;
  reg [input_data_width-1:0] sub_k0_d4_st0;
  reg [input_data_width-1:0] sub_k1_d0_st0;
  reg [input_data_width-1:0] sub_k1_d1_st0;
  reg [input_data_width-1:0] sub_k1_d2_st0;
  reg [input_data_width-1:0] sub_k1_d3_st0;
  reg [input_data_width-1:0] sub_k1_d4_st0;

  //pipeline stage 1 - Sqr
  reg [input_data_width*2-1:0] sqr_k0_d0_st1;
  reg [input_data_width*2-1:0] sqr_k0_d1_st1;
  reg [input_data_width*2-1:0] sqr_k0_d2_st1;
  reg [input_data_width*2-1:0] sqr_k0_d3_st1;
  reg [input_data_width*2-1:0] sqr_k0_d4_st1;
  reg [input_data_width*2-1:0] sqr_k1_d0_st1;
  reg [input_data_width*2-1:0] sqr_k1_d1_st1;
  reg [input_data_width*2-1:0] sqr_k1_d2_st1;
  reg [input_data_width*2-1:0] sqr_k1_d3_st1;
  reg [input_data_width*2-1:0] sqr_k1_d4_st1;

  //pipeline Add reduction - 3 stages
  //we needed to add 3b to the add witdh because we need ceil(log2(reduction_stages)) + 1 to don´t have overflow
  reg [input_data_width*2+3-1:0] add0_k0_st2;
  reg [input_data_width*2+3-1:0] add1_k0_st2;
  reg [input_data_width*2+3-1:0] add2_k0_st2;
  reg [input_data_width*2+3-1:0] add3_k0_st3;
  reg [input_data_width*2+3-1:0] add4_k0_st3;
  reg [input_data_width*2+3-1:0] add5_k0_st4;
  reg [input_data_width*2+3-1:0] add0_k1_st2;
  reg [input_data_width*2+3-1:0] add1_k1_st2;
  reg [input_data_width*2+3-1:0] add2_k1_st2;
  reg [input_data_width*2+3-1:0] add3_k1_st3;
  reg [input_data_width*2+3-1:0] add4_k1_st3;
  reg [input_data_width*2+3-1:0] add5_k1_st4;

  //pipeline comp reduction - 1 stages. Centroid idx propagation
  reg [1-1:0] cmp0_idx_st5;

  //pipeline comp reduction - 1 stages. Centroid add reduction propagation
  //The last stage of these regs are only for depuration. When in synthesys they will be automatically removed
  reg [input_data_width*2+3-1:0] cmp0_data_st5;

  //Output assigns
  assign selected_centroid = cmp0_idx_st5;

  always @(posedge clk) begin
    sub_k0_d0_st0 <= centroid0_d0 - input_data0;
    sub_k0_d1_st0 <= centroid0_d1 - input_data1;
    sub_k0_d2_st0 <= centroid0_d2 - input_data2;
    sub_k0_d3_st0 <= centroid0_d3 - input_data3;
    sub_k0_d4_st0 <= centroid0_d4 - input_data4;
    sub_k1_d0_st0 <= centroid1_d0 - input_data0;
    sub_k1_d1_st0 <= centroid1_d1 - input_data1;
    sub_k1_d2_st0 <= centroid1_d2 - input_data2;
    sub_k1_d3_st0 <= centroid1_d3 - input_data3;
    sub_k1_d4_st0 <= centroid1_d4 - input_data4;
    sqr_k0_d0_st1 <= sub_k0_d0_st0 * sub_k0_d0_st0;
    sqr_k0_d1_st1 <= sub_k0_d1_st0 * sub_k0_d1_st0;
    sqr_k0_d2_st1 <= sub_k0_d2_st0 * sub_k0_d2_st0;
    sqr_k0_d3_st1 <= sub_k0_d3_st0 * sub_k0_d3_st0;
    sqr_k0_d4_st1 <= sub_k0_d4_st0 * sub_k0_d4_st0;
    sqr_k1_d0_st1 <= sub_k1_d0_st0 * sub_k1_d0_st0;
    sqr_k1_d1_st1 <= sub_k1_d1_st0 * sub_k1_d1_st0;
    sqr_k1_d2_st1 <= sub_k1_d2_st0 * sub_k1_d2_st0;
    sqr_k1_d3_st1 <= sub_k1_d3_st0 * sub_k1_d3_st0;
    sqr_k1_d4_st1 <= sub_k1_d4_st0 * sub_k1_d4_st0;
    add0_k0_st2 <= sqr_k0_d0_st1 + sqr_k0_d1_st1;
    add0_k1_st2 <= sqr_k1_d0_st1 + sqr_k1_d1_st1;
    add1_k0_st2 <= sqr_k0_d2_st1 + sqr_k0_d3_st1;
    add1_k1_st2 <= sqr_k1_d2_st1 + sqr_k1_d3_st1;
    add2_k0_st2 <= sqr_k0_d4_st1;
    add2_k1_st2 <= sqr_k1_d4_st1;
    add3_k0_st3 <= add0_k0_st2 + add1_k0_st2;
    add3_k1_st3 <= add0_k1_st2 + add1_k1_st2;
    add4_k0_st3 <= add2_k0_st2;
    add4_k1_st3 <= add2_k1_st2;
    add5_k0_st4 <= add3_k0_st3 + add4_k0_st3;
    add5_k1_st4 <= add3_k1_st3 + add4_k1_st3;
    cmp0_idx_st5 <= (add5_k0_st4 < add5_k1_st4)? 1'd0 : 1'd1;
    cmp0_data_st5 <= (add5_k0_st4 < add5_k1_st4)? add5_k0_st4 : add5_k1_st4;
  end


  //Input data propagation pipeline
  reg [input_data_width-1:0] data_prop_d0_st0;
  reg [input_data_width-1:0] data_prop_d1_st0;
  reg [input_data_width-1:0] data_prop_d2_st0;
  reg [input_data_width-1:0] data_prop_d3_st0;
  reg [input_data_width-1:0] data_prop_d4_st0;
  reg [input_data_width-1:0] data_prop_d0_st1;
  reg [input_data_width-1:0] data_prop_d1_st1;
  reg [input_data_width-1:0] data_prop_d2_st1;
  reg [input_data_width-1:0] data_prop_d3_st1;
  reg [input_data_width-1:0] data_prop_d4_st1;
  reg [input_data_width-1:0] data_prop_d0_st2;
  reg [input_data_width-1:0] data_prop_d1_st2;
  reg [input_data_width-1:0] data_prop_d2_st2;
  reg [input_data_width-1:0] data_prop_d3_st2;
  reg [input_data_width-1:0] data_prop_d4_st2;
  reg [input_data_width-1:0] data_prop_d0_st3;
  reg [input_data_width-1:0] data_prop_d1_st3;
  reg [input_data_width-1:0] data_prop_d2_st3;
  reg [input_data_width-1:0] data_prop_d3_st3;
  reg [input_data_width-1:0] data_prop_d4_st3;
  reg [input_data_width-1:0] data_prop_d0_st4;
  reg [input_data_width-1:0] data_prop_d1_st4;
  reg [input_data_width-1:0] data_prop_d2_st4;
  reg [input_data_width-1:0] data_prop_d3_st4;
  reg [input_data_width-1:0] data_prop_d4_st4;
  reg [input_data_width-1:0] data_prop_d0_st5;
  reg [input_data_width-1:0] data_prop_d1_st5;
  reg [input_data_width-1:0] data_prop_d2_st5;
  reg [input_data_width-1:0] data_prop_d3_st5;
  reg [input_data_width-1:0] data_prop_d4_st5;

  //Output assigns
  assign output_data0 = data_prop_d0_st5;
  assign output_data1 = data_prop_d1_st5;
  assign output_data2 = data_prop_d2_st5;
  assign output_data3 = data_prop_d3_st5;
  assign output_data4 = data_prop_d4_st5;

  always @(posedge clk) begin
    data_prop_d0_st0 <= input_data0;
    data_prop_d1_st0 <= input_data1;
    data_prop_d2_st0 <= input_data2;
    data_prop_d3_st0 <= input_data3;
    data_prop_d4_st0 <= input_data4;
    data_prop_d0_st1 <= data_prop_d0_st0;
    data_prop_d1_st1 <= data_prop_d1_st0;
    data_prop_d2_st1 <= data_prop_d2_st0;
    data_prop_d3_st1 <= data_prop_d3_st0;
    data_prop_d4_st1 <= data_prop_d4_st0;
    data_prop_d0_st2 <= data_prop_d0_st1;
    data_prop_d1_st2 <= data_prop_d1_st1;
    data_prop_d2_st2 <= data_prop_d2_st1;
    data_prop_d3_st2 <= data_prop_d3_st1;
    data_prop_d4_st2 <= data_prop_d4_st1;
    data_prop_d0_st3 <= data_prop_d0_st2;
    data_prop_d1_st3 <= data_prop_d1_st2;
    data_prop_d2_st3 <= data_prop_d2_st2;
    data_prop_d3_st3 <= data_prop_d3_st2;
    data_prop_d4_st3 <= data_prop_d4_st2;
    data_prop_d0_st4 <= data_prop_d0_st3;
    data_prop_d1_st4 <= data_prop_d1_st3;
    data_prop_d2_st4 <= data_prop_d2_st3;
    data_prop_d3_st4 <= data_prop_d3_st3;
    data_prop_d4_st4 <= data_prop_d4_st3;
    data_prop_d0_st5 <= data_prop_d0_st4;
    data_prop_d1_st5 <= data_prop_d1_st4;
    data_prop_d2_st5 <= data_prop_d2_st4;
    data_prop_d3_st5 <= data_prop_d3_st4;
    data_prop_d4_st5 <= data_prop_d4_st4;
  end


  initial begin
    sub_k0_d0_st0 = 0;
    sub_k0_d1_st0 = 0;
    sub_k0_d2_st0 = 0;
    sub_k0_d3_st0 = 0;
    sub_k0_d4_st0 = 0;
    sub_k1_d0_st0 = 0;
    sub_k1_d1_st0 = 0;
    sub_k1_d2_st0 = 0;
    sub_k1_d3_st0 = 0;
    sub_k1_d4_st0 = 0;
    sqr_k0_d0_st1 = 0;
    sqr_k0_d1_st1 = 0;
    sqr_k0_d2_st1 = 0;
    sqr_k0_d3_st1 = 0;
    sqr_k0_d4_st1 = 0;
    sqr_k1_d0_st1 = 0;
    sqr_k1_d1_st1 = 0;
    sqr_k1_d2_st1 = 0;
    sqr_k1_d3_st1 = 0;
    sqr_k1_d4_st1 = 0;
    add0_k0_st2 = 0;
    add1_k0_st2 = 0;
    add2_k0_st2 = 0;
    add3_k0_st3 = 0;
    add4_k0_st3 = 0;
    add5_k0_st4 = 0;
    add0_k1_st2 = 0;
    add1_k1_st2 = 0;
    add2_k1_st2 = 0;
    add3_k1_st3 = 0;
    add4_k1_st3 = 0;
    add5_k1_st4 = 0;
    cmp0_idx_st5 = 0;
    cmp0_data_st5 = 0;
    data_prop_d0_st0 = 0;
    data_prop_d1_st0 = 0;
    data_prop_d2_st0 = 0;
    data_prop_d3_st0 = 0;
    data_prop_d4_st0 = 0;
    data_prop_d0_st1 = 0;
    data_prop_d1_st1 = 0;
    data_prop_d2_st1 = 0;
    data_prop_d3_st1 = 0;
    data_prop_d4_st1 = 0;
    data_prop_d0_st2 = 0;
    data_prop_d1_st2 = 0;
    data_prop_d2_st2 = 0;
    data_prop_d3_st2 = 0;
    data_prop_d4_st2 = 0;
    data_prop_d0_st3 = 0;
    data_prop_d1_st3 = 0;
    data_prop_d2_st3 = 0;
    data_prop_d3_st3 = 0;
    data_prop_d4_st3 = 0;
    data_prop_d0_st4 = 0;
    data_prop_d1_st4 = 0;
    data_prop_d2_st4 = 0;
    data_prop_d3_st4 = 0;
    data_prop_d4_st4 = 0;
    data_prop_d0_st5 = 0;
    data_prop_d1_st5 = 0;
    data_prop_d2_st5 = 0;
    data_prop_d3_st5 = 0;
    data_prop_d4_st5 = 0;
  end


endmodule

