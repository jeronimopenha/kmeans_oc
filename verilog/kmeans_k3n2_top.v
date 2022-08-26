

module kmeans_k3n2_top #
(
  parameter input_data_width = 8,
  parameter input_data_qty = 256,
  parameter input_data_qty_bit_width = 8,
  parameter acc_width = 16,
  parameter mem_d0_init_file = "./db/d0.txt",
  parameter mem_d1_init_file = "./db/d1.txt",
  parameter k0_d0_initial = 0,
  parameter k0_d1_initial = 0,
  parameter k1_d0_initial = 1,
  parameter k1_d1_initial = 1,
  parameter k2_d0_initial = 2,
  parameter k2_d1_initial = 2
)
(
  input clk,
  input rst,
  input start
);


  //Centroids unique regs
  reg [input_data_width-1:0] k0d0;
  reg [input_data_width-1:0] k0d1;
  reg [input_data_width-1:0] k1d0;
  reg [input_data_width-1:0] k1d1;
  reg [input_data_width-1:0] k2d0;
  reg [input_data_width-1:0] k2d1;

  //New centroids vector regs
  reg [input_data_width-1:0] new_centroid_k0 [0:2-1];
  reg [input_data_width-1:0] new_centroid_k1 [0:2-1];
  reg [input_data_width-1:0] new_centroid_k2 [0:2-1];

  //New centroids unique buses
  wire [input_data_width-1:0] new_k0d0;
  wire [input_data_width-1:0] new_k0d1;
  wire [input_data_width-1:0] new_k1d0;
  wire [input_data_width-1:0] new_k1d1;
  wire [input_data_width-1:0] new_k2d0;
  wire [input_data_width-1:0] new_k2d1;

  //Assigning each new centroid buses to it`s respective reg
  assign new_k0d0 = new_centroid_k0[0];
  assign new_k0d1 = new_centroid_k0[1];
  assign new_k1d0 = new_centroid_k1[0];
  assign new_k1d1 = new_centroid_k1[1];
  assign new_k2d0 = new_centroid_k2[0];
  assign new_k2d1 = new_centroid_k2[1];

  //Input data block
  //In this block we have N RAM memories. Each one contains data for one input dimension
  wire [input_data_qty_bit_width-1:0] input_ram_rd_address;
  wire [input_data_width-1:0] d0;
  wire [input_data_width-1:0] d1;

  kmeans_input_data_block_2dim
  #(
    .input_data_width(input_data_width),
    .memory_depth_bits(input_data_qty_bit_width),
    .mem_d0_init_file(mem_d0_init_file),
    .mem_d1_init_file(mem_d1_init_file)
  )
  kmeans_input_data_block_2dim
  (
    .clk(clk),
    .rd_address(input_ram_rd_address),
    .output_data0(d0),
    .output_data1(d1)
  );


  //kmeans main pipeline
  wire [input_data_width-1:0] d0_to_acc;
  wire [input_data_width-1:0] d1_to_acc;
  wire [2-1:0] selected_centroid;

  kmeans_pipeline_k3_d2
  kmeans_pipeline_k3_d2
  (
    .clk(clk),
    .centroid0_d0(k0d0),
    .centroid0_d1(k0d1),
    .centroid1_d0(k1d0),
    .centroid1_d1(k1d1),
    .centroid2_d0(k2d0),
    .centroid2_d1(k2d1),
    .input_data0(d0),
    .input_data1(d1),
    .output_data0(d0_to_acc),
    .output_data1(d1_to_acc),
    .selected_centroid(selected_centroid)
  );


  //kmeans acc block
  wire [acc_width-1:0] acc0_output;
  wire [acc_width-1:0] acc1_output;
  wire [2-1:0] centroid_acc_output;
  wire [input_data_qty_bit_width-1:0] acc_counter_output;

  kmeans_acc_block_k3n2
  #(
    .input_data_width(input_data_width),
    .input_data_qty_bit_width(input_data_qty_bit_width),
    .acc_width(acc_width)
  )
  kmeans_acc_block_k3n2
  (
    .clk(clk),
    .rst(0),
    .acc_enable(0),
    .d0_to_acc(d0_to_acc),
    .d1_to_acc(d1_to_acc),
    .selected_centroid(selected_centroid),
    .rd_acc_en(0),
    .rd_acc_centroid(0),
    .centroid_output(centroid_acc_output),
    .acc0_output(acc0_output),
    .acc1_output(acc1_output),
    .acc_counter_output(acc_counter_output)
  );

  integer i_initial;

  initial begin
    k0d0 = 0;
    k0d1 = 0;
    k1d0 = 0;
    k1d1 = 0;
    k2d0 = 0;
    k2d1 = 0;
    for(i_initial=0; i_initial<2; i_initial=i_initial+1) begin
      new_centroid_k0[i_initial] = 0;
    end
    for(i_initial=0; i_initial<2; i_initial=i_initial+1) begin
      new_centroid_k1[i_initial] = 0;
    end
    for(i_initial=0; i_initial<2; i_initial=i_initial+1) begin
      new_centroid_k2[i_initial] = 0;
    end
  end


endmodule



module kmeans_input_data_block_2dim #
(
  parameter input_data_width = 8,
  parameter memory_depth_bits = 8,
  parameter mem_d0_init_file = "./db/d0.txt",
  parameter mem_d1_init_file = "./db/d1.txt"
)
(
  input clk,
  input [memory_depth_bits-1:0] rd_address,
  output [input_data_width-1:0] output_data0,
  output [input_data_width-1:0] output_data1
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



module kmeans_pipeline_k3_d2 #
(
  parameter input_data_width = 8
)
(
  input clk,
  input [input_data_width-1:0] centroid0_d0,
  input [input_data_width-1:0] centroid0_d1,
  input [input_data_width-1:0] centroid1_d0,
  input [input_data_width-1:0] centroid1_d1,
  input [input_data_width-1:0] centroid2_d0,
  input [input_data_width-1:0] centroid2_d1,
  input [input_data_width-1:0] input_data0,
  input [input_data_width-1:0] input_data1,
  output [input_data_width-1:0] output_data0,
  output [input_data_width-1:0] output_data1,
  output [2-1:0] selected_centroid
);

  //Latency delay
  //1(sub) + 1(sqr) + ceil(log2(dimensions_qty)) (add) + ceil(log2(centroids_qty)) (comp)
  //for this one it is 5

  //pipeline stage 0 - Sub
  reg [input_data_width-1:0] sub_k0_d0_st0;
  reg [input_data_width-1:0] sub_k0_d1_st0;
  reg [input_data_width-1:0] sub_k1_d0_st0;
  reg [input_data_width-1:0] sub_k1_d1_st0;
  reg [input_data_width-1:0] sub_k2_d0_st0;
  reg [input_data_width-1:0] sub_k2_d1_st0;

  //pipeline stage 1 - Sqr
  reg [input_data_width*2-1:0] sqr_k0_d0_st1;
  reg [input_data_width*2-1:0] sqr_k0_d1_st1;
  reg [input_data_width*2-1:0] sqr_k1_d0_st1;
  reg [input_data_width*2-1:0] sqr_k1_d1_st1;
  reg [input_data_width*2-1:0] sqr_k2_d0_st1;
  reg [input_data_width*2-1:0] sqr_k2_d1_st1;

  //pipeline Add reduction - 1 stages
  //we needed to add 1b to the add witdh because we need ceil(log2(reduction_stages)) + 1 to don´t have overflow
  reg [input_data_width*2+1-1:0] add0_k0_st2;
  reg [input_data_width*2+1-1:0] add0_k1_st2;
  reg [input_data_width*2+1-1:0] add0_k2_st2;

  //pipeline comp reduction - 2 stages. Centroid idx propagation
  reg [2-1:0] cmp0_idx_st3;
  reg [2-1:0] cmp1_idx_st3;
  reg [2-1:0] cmp2_idx_st4;

  //pipeline comp reduction - 2 stages. Centroid add reduction propagation
  //The last stage of these regs are only for depuration. When in synthesys they will be automatically removed
  reg [input_data_width*2+1-1:0] cmp0_data_st3;
  reg [input_data_width*2+1-1:0] cmp1_data_st3;
  reg [input_data_width*2+1-1:0] cmp2_data_st4;

  //Output assigns
  assign selected_centroid = cmp2_idx_st4;

  always @(posedge clk) begin
    sub_k0_d0_st0 <= centroid0_d0 - input_data0;
    sub_k0_d1_st0 <= centroid0_d1 - input_data1;
    sub_k1_d0_st0 <= centroid1_d0 - input_data0;
    sub_k1_d1_st0 <= centroid1_d1 - input_data1;
    sub_k2_d0_st0 <= centroid2_d0 - input_data0;
    sub_k2_d1_st0 <= centroid2_d1 - input_data1;
    sqr_k0_d0_st1 <= sub_k0_d0_st0 * sub_k0_d0_st0;
    sqr_k0_d1_st1 <= sub_k0_d1_st0 * sub_k0_d1_st0;
    sqr_k1_d0_st1 <= sub_k1_d0_st0 * sub_k1_d0_st0;
    sqr_k1_d1_st1 <= sub_k1_d1_st0 * sub_k1_d1_st0;
    sqr_k2_d0_st1 <= sub_k2_d0_st0 * sub_k2_d0_st0;
    sqr_k2_d1_st1 <= sub_k2_d1_st0 * sub_k2_d1_st0;
    add0_k0_st2 <= sqr_k0_d0_st1 + sqr_k0_d1_st1;
    add0_k1_st2 <= sqr_k1_d0_st1 + sqr_k1_d1_st1;
    add0_k2_st2 <= sqr_k2_d0_st1 + sqr_k2_d1_st1;
    cmp0_idx_st3 <= (add0_k0_st2 < add0_k1_st2)? 2'd0 : 2'd1;
    cmp0_data_st3 <= (add0_k0_st2 < add0_k1_st2)? add0_k0_st2 : add0_k1_st2;
    cmp1_idx_st3 <= 2'd2;
    cmp1_data_st3 <= add0_k2_st2;
    cmp2_idx_st4 <= (cmp0_data_st3 < cmp1_data_st3)? cmp0_idx_st3 : cmp1_idx_st3;
    cmp2_data_st4 <= (cmp0_data_st3 < cmp1_data_st3)? cmp0_data_st3 : cmp1_data_st3;
  end


  //Input data propagation pipeline
  reg [input_data_width-1:0] data_prop_d0_st0;
  reg [input_data_width-1:0] data_prop_d1_st0;
  reg [input_data_width-1:0] data_prop_d0_st1;
  reg [input_data_width-1:0] data_prop_d1_st1;
  reg [input_data_width-1:0] data_prop_d0_st2;
  reg [input_data_width-1:0] data_prop_d1_st2;
  reg [input_data_width-1:0] data_prop_d0_st3;
  reg [input_data_width-1:0] data_prop_d1_st3;
  reg [input_data_width-1:0] data_prop_d0_st4;
  reg [input_data_width-1:0] data_prop_d1_st4;

  //Output assigns
  assign output_data0 = data_prop_d0_st4;
  assign output_data1 = data_prop_d1_st4;

  always @(posedge clk) begin
    data_prop_d0_st0 <= input_data0;
    data_prop_d1_st0 <= input_data1;
    data_prop_d0_st1 <= data_prop_d0_st0;
    data_prop_d1_st1 <= data_prop_d1_st0;
    data_prop_d0_st2 <= data_prop_d0_st1;
    data_prop_d1_st2 <= data_prop_d1_st1;
    data_prop_d0_st3 <= data_prop_d0_st2;
    data_prop_d1_st3 <= data_prop_d1_st2;
    data_prop_d0_st4 <= data_prop_d0_st3;
    data_prop_d1_st4 <= data_prop_d1_st3;
  end


  initial begin
    sub_k0_d0_st0 = 0;
    sub_k0_d1_st0 = 0;
    sub_k1_d0_st0 = 0;
    sub_k1_d1_st0 = 0;
    sub_k2_d0_st0 = 0;
    sub_k2_d1_st0 = 0;
    sqr_k0_d0_st1 = 0;
    sqr_k0_d1_st1 = 0;
    sqr_k1_d0_st1 = 0;
    sqr_k1_d1_st1 = 0;
    sqr_k2_d0_st1 = 0;
    sqr_k2_d1_st1 = 0;
    add0_k0_st2 = 0;
    add0_k1_st2 = 0;
    add0_k2_st2 = 0;
    cmp0_idx_st3 = 0;
    cmp1_idx_st3 = 0;
    cmp2_idx_st4 = 0;
    cmp0_data_st3 = 0;
    cmp1_data_st3 = 0;
    cmp2_data_st4 = 0;
    data_prop_d0_st0 = 0;
    data_prop_d1_st0 = 0;
    data_prop_d0_st1 = 0;
    data_prop_d1_st1 = 0;
    data_prop_d0_st2 = 0;
    data_prop_d1_st2 = 0;
    data_prop_d0_st3 = 0;
    data_prop_d1_st3 = 0;
    data_prop_d0_st4 = 0;
    data_prop_d1_st4 = 0;
  end


endmodule



module kmeans_acc_block_k3n2 #
(
  parameter input_data_width = 8,
  parameter input_data_qty_bit_width = 8,
  parameter acc_width = 16
)
(
  input clk,
  input rst,
  input acc_enable,
  input [input_data_width-1:0] d0_to_acc,
  input [input_data_width-1:0] d1_to_acc,
  input [2-1:0] selected_centroid,
  input rd_acc_en,
  input [2-1:0] rd_acc_centroid,
  output reg [2-1:0] centroid_output,
  output [acc_width-1:0] acc0_output,
  output [acc_width-1:0] acc1_output,
  output [input_data_qty_bit_width-1:0] acc_counter_output
);


  //counters for each centroid
  reg [input_data_qty_bit_width-1:0] centroid_counter [0:3-1];

  //Memories valid content register flag
  reg [3-1:0] acc_valid_content;

  //Memories wires and regs
  wire [2-1:0] mem_acc_rd_addr;
  wire [acc_width-1:0] mem_acc_0_out;
  wire [acc_width-1:0] mem_acc_1_out;
  wire mem_acc_0_wr;
  wire mem_acc_1_wr;
  wire [2-1:0] mem_acc0_wr_addr;
  wire [2-1:0] mem_acc1_wr_addr;
  wire [acc_width-1:0] mem_acc0_wr_data;
  wire [acc_width-1:0] mem_acc1_wr_data;

  //Assigns to control the read and write acc logic
  //First the read conditions:
  //If we are accumulating, we need to read the memory, add the input content to the memory content if it is valid
  //If we are reading the ACC, we need to have authority to read with no interference from the pipeline`s
  //selected centroid input
  assign mem_acc_rd_addr = (rd_acc_en)? rd_acc_centroid : selected_centroid;

  //The write enable signal is controled by the input "acc_enable"
  assign mem_acc_0_wr = acc_enable;
  assign mem_acc_1_wr = acc_enable;

  //The write address is the number of selected centroid given by the "selected_centroid" input signal
  assign mem_acc0_wr_addr = selected_centroid;
  assign mem_acc1_wr_addr = selected_centroid;

  //Next the write data is the sum of the memory content + input data for each memory if the memory is initialized.
  assign mem_acc0_wr_data = (acc_valid_content[selected_centroid])? d0_to_acc + mem_acc_0_out : d0_to_acc;
  assign mem_acc1_wr_data = (acc_valid_content[selected_centroid])? d1_to_acc + mem_acc_1_out : d1_to_acc;

  //Output data assigns
  assign acc0_output = mem_acc_0_out;
  assign acc1_output = mem_acc_1_out;

  //Resetting the ACC contents and updating it`s bits when a data is written in memory

  always @(posedge clk) begin
    if(rst) begin
      acc_valid_content <= 0;
    end else begin
      if(acc_enable) begin
        acc_valid_content[selected_centroid] <= 1;
      end 
    end
  end


  //Output counter assigns
  assign acc_counter_output = centroid_counter[rd_acc_centroid];

  //Resetting the centroids counters and updating them when a data is written in a centroid line

  always @(posedge clk) begin
    if(rst) begin
      centroid_counter[0] <= 0;
      centroid_counter[1] <= 0;
      centroid_counter[2] <= 0;
    end else begin
      if(acc_enable) begin
        centroid_counter[selected_centroid] <= centroid_counter[selected_centroid] + 1;
      end 
    end
  end


  //ACC memories
  //we have one memory for wach dimension and the lines are the centrods acc

  RAM
  #(
    .read_f(0),
    .write_f(0),
    .depth(2),
    .width(acc_width)
  )
  RAM_d0
  (
    .clk(clk),
    .rd_addr(mem_acc_rd_addr),
    .out(mem_acc_0_out),
    .wr(mem_acc_0_wr),
    .wr_addr(mem_acc0_wr_addr),
    .wr_data(mem_acc0_wr_data)
  );


  RAM
  #(
    .read_f(0),
    .write_f(0),
    .depth(2),
    .width(acc_width)
  )
  RAM_d1
  (
    .clk(clk),
    .rd_addr(mem_acc_rd_addr),
    .out(mem_acc_1_out),
    .wr(mem_acc_1_wr),
    .wr_addr(mem_acc1_wr_addr),
    .wr_data(mem_acc1_wr_data)
  );

  integer i_initial;

  initial begin
    centroid_output = 0;
    for(i_initial=0; i_initial<3; i_initial=i_initial+1) begin
      centroid_counter[i_initial] = 0;
    end
    acc_valid_content = 0;
  end


endmodule

