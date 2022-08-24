

module kmeans_pipeline_k3_d4 #
(
  parameter input_data_width = 16
)
(
  input clk,
  input [input_data_width-1:0] centroid0_d0,
  input [input_data_width-1:0] centroid0_d1,
  input [input_data_width-1:0] centroid0_d2,
  input [input_data_width-1:0] centroid0_d3,
  input [input_data_width-1:0] centroid1_d0,
  input [input_data_width-1:0] centroid1_d1,
  input [input_data_width-1:0] centroid1_d2,
  input [input_data_width-1:0] centroid1_d3,
  input [input_data_width-1:0] centroid2_d0,
  input [input_data_width-1:0] centroid2_d1,
  input [input_data_width-1:0] centroid2_d2,
  input [input_data_width-1:0] centroid2_d3,
  input [input_data_width-1:0] input_data0,
  input [input_data_width-1:0] input_data1,
  input [input_data_width-1:0] input_data2,
  input [input_data_width-1:0] input_data3,
  output [input_data_width-1:0] output_data0,
  output [input_data_width-1:0] output_data1,
  output [input_data_width-1:0] output_data2,
  output [input_data_width-1:0] output_data3,
  output [2-1:0] selected_centroid
);

  //Latency delay
  //1(sub) + 1(sqr) + ceil(log2(dimensions_qty)) (add) + ceil(log2(centroids_qty)) (comp)
  //for this one it is 6

  //pipeline stage 0 - Sub
  reg [input_data_width-1:0] sub_k0_d0_st0;
  reg [input_data_width-1:0] sub_k0_d1_st0;
  reg [input_data_width-1:0] sub_k0_d2_st0;
  reg [input_data_width-1:0] sub_k0_d3_st0;
  reg [input_data_width-1:0] sub_k1_d0_st0;
  reg [input_data_width-1:0] sub_k1_d1_st0;
  reg [input_data_width-1:0] sub_k1_d2_st0;
  reg [input_data_width-1:0] sub_k1_d3_st0;
  reg [input_data_width-1:0] sub_k2_d0_st0;
  reg [input_data_width-1:0] sub_k2_d1_st0;
  reg [input_data_width-1:0] sub_k2_d2_st0;
  reg [input_data_width-1:0] sub_k2_d3_st0;

  //pipeline stage 1 - Sqr
  reg [input_data_width*2-1:0] sqr_k0_d0_st1;
  reg [input_data_width*2-1:0] sqr_k0_d1_st1;
  reg [input_data_width*2-1:0] sqr_k0_d2_st1;
  reg [input_data_width*2-1:0] sqr_k0_d3_st1;
  reg [input_data_width*2-1:0] sqr_k1_d0_st1;
  reg [input_data_width*2-1:0] sqr_k1_d1_st1;
  reg [input_data_width*2-1:0] sqr_k1_d2_st1;
  reg [input_data_width*2-1:0] sqr_k1_d3_st1;
  reg [input_data_width*2-1:0] sqr_k2_d0_st1;
  reg [input_data_width*2-1:0] sqr_k2_d1_st1;
  reg [input_data_width*2-1:0] sqr_k2_d2_st1;
  reg [input_data_width*2-1:0] sqr_k2_d3_st1;

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
    sub_k0_d3_st0 <= centroid0_d3 - input_data3;
    sub_k1_d0_st0 <= centroid1_d0 - input_data0;
    sub_k1_d1_st0 <= centroid1_d1 - input_data1;
    sub_k1_d2_st0 <= centroid1_d2 - input_data2;
    sub_k1_d3_st0 <= centroid1_d3 - input_data3;
    sub_k2_d0_st0 <= centroid2_d0 - input_data0;
    sub_k2_d1_st0 <= centroid2_d1 - input_data1;
    sub_k2_d2_st0 <= centroid2_d2 - input_data2;
    sub_k2_d3_st0 <= centroid2_d3 - input_data3;
    sqr_k0_d0_st1 <= sub_k0_d0_st0 * sub_k0_d0_st0;
    sqr_k0_d1_st1 <= sub_k0_d1_st0 * sub_k0_d1_st0;
    sqr_k0_d2_st1 <= sub_k0_d2_st0 * sub_k0_d2_st0;
    sqr_k0_d3_st1 <= sub_k0_d3_st0 * sub_k0_d3_st0;
    sqr_k1_d0_st1 <= sub_k1_d0_st0 * sub_k1_d0_st0;
    sqr_k1_d1_st1 <= sub_k1_d1_st0 * sub_k1_d1_st0;
    sqr_k1_d2_st1 <= sub_k1_d2_st0 * sub_k1_d2_st0;
    sqr_k1_d3_st1 <= sub_k1_d3_st0 * sub_k1_d3_st0;
    sqr_k2_d0_st1 <= sub_k2_d0_st0 * sub_k2_d0_st0;
    sqr_k2_d1_st1 <= sub_k2_d1_st0 * sub_k2_d1_st0;
    sqr_k2_d2_st1 <= sub_k2_d2_st0 * sub_k2_d2_st0;
    sqr_k2_d3_st1 <= sub_k2_d3_st0 * sub_k2_d3_st0;
    add0_k0_st2 <= sqr_k0_d0_st1 + sqr_k0_d1_st1;
    add1_k0_st2 <= sqr_k0_d2_st1 + sqr_k0_d3_st1;
    add2_k0_st3 <= add0_k0_st2 + add1_k0_st2;
    add0_k1_st2 <= sqr_k1_d0_st1 + sqr_k1_d1_st1;
    add1_k1_st2 <= sqr_k1_d2_st1 + sqr_k1_d3_st1;
    add2_k1_st3 <= add0_k1_st2 + add1_k1_st2;
    add0_k2_st2 <= sqr_k2_d0_st1 + sqr_k2_d1_st1;
    add1_k2_st2 <= sqr_k2_d2_st1 + sqr_k2_d3_st1;
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
  reg [input_data_width-1:0] data_prop_d3_st0;
  reg [input_data_width-1:0] data_prop_d0_st1;
  reg [input_data_width-1:0] data_prop_d1_st1;
  reg [input_data_width-1:0] data_prop_d2_st1;
  reg [input_data_width-1:0] data_prop_d3_st1;
  reg [input_data_width-1:0] data_prop_d0_st2;
  reg [input_data_width-1:0] data_prop_d1_st2;
  reg [input_data_width-1:0] data_prop_d2_st2;
  reg [input_data_width-1:0] data_prop_d3_st2;
  reg [input_data_width-1:0] data_prop_d0_st3;
  reg [input_data_width-1:0] data_prop_d1_st3;
  reg [input_data_width-1:0] data_prop_d2_st3;
  reg [input_data_width-1:0] data_prop_d3_st3;
  reg [input_data_width-1:0] data_prop_d0_st4;
  reg [input_data_width-1:0] data_prop_d1_st4;
  reg [input_data_width-1:0] data_prop_d2_st4;
  reg [input_data_width-1:0] data_prop_d3_st4;
  reg [input_data_width-1:0] data_prop_d0_st5;
  reg [input_data_width-1:0] data_prop_d1_st5;
  reg [input_data_width-1:0] data_prop_d2_st5;
  reg [input_data_width-1:0] data_prop_d3_st5;

  //Output assigns
  assign output_data0 = data_prop_d0_st5;
  assign output_data1 = data_prop_d1_st5;
  assign output_data2 = data_prop_d2_st5;
  assign output_data3 = data_prop_d3_st5;

  always @(posedge clk) begin
    data_prop_d0_st0 <= input_data0;
    data_prop_d1_st0 <= input_data1;
    data_prop_d2_st0 <= input_data2;
    data_prop_d3_st0 <= input_data3;
    data_prop_d0_st1 <= data_prop_d0_st0;
    data_prop_d1_st1 <= data_prop_d1_st0;
    data_prop_d2_st1 <= data_prop_d2_st0;
    data_prop_d3_st1 <= data_prop_d3_st0;
    data_prop_d0_st2 <= data_prop_d0_st1;
    data_prop_d1_st2 <= data_prop_d1_st1;
    data_prop_d2_st2 <= data_prop_d2_st1;
    data_prop_d3_st2 <= data_prop_d3_st1;
    data_prop_d0_st3 <= data_prop_d0_st2;
    data_prop_d1_st3 <= data_prop_d1_st2;
    data_prop_d2_st3 <= data_prop_d2_st2;
    data_prop_d3_st3 <= data_prop_d3_st2;
    data_prop_d0_st4 <= data_prop_d0_st3;
    data_prop_d1_st4 <= data_prop_d1_st3;
    data_prop_d2_st4 <= data_prop_d2_st3;
    data_prop_d3_st4 <= data_prop_d3_st3;
    data_prop_d0_st5 <= data_prop_d0_st4;
    data_prop_d1_st5 <= data_prop_d1_st4;
    data_prop_d2_st5 <= data_prop_d2_st4;
    data_prop_d3_st5 <= data_prop_d3_st4;
  end


  initial begin
    sub_k0_d0_st0 = 0;
    sub_k0_d1_st0 = 0;
    sub_k0_d2_st0 = 0;
    sub_k0_d3_st0 = 0;
    sub_k1_d0_st0 = 0;
    sub_k1_d1_st0 = 0;
    sub_k1_d2_st0 = 0;
    sub_k1_d3_st0 = 0;
    sub_k2_d0_st0 = 0;
    sub_k2_d1_st0 = 0;
    sub_k2_d2_st0 = 0;
    sub_k2_d3_st0 = 0;
    sqr_k0_d0_st1 = 0;
    sqr_k0_d1_st1 = 0;
    sqr_k0_d2_st1 = 0;
    sqr_k0_d3_st1 = 0;
    sqr_k1_d0_st1 = 0;
    sqr_k1_d1_st1 = 0;
    sqr_k1_d2_st1 = 0;
    sqr_k1_d3_st1 = 0;
    sqr_k2_d0_st1 = 0;
    sqr_k2_d1_st1 = 0;
    sqr_k2_d2_st1 = 0;
    sqr_k2_d3_st1 = 0;
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
    data_prop_d3_st0 = 0;
    data_prop_d0_st1 = 0;
    data_prop_d1_st1 = 0;
    data_prop_d2_st1 = 0;
    data_prop_d3_st1 = 0;
    data_prop_d0_st2 = 0;
    data_prop_d1_st2 = 0;
    data_prop_d2_st2 = 0;
    data_prop_d3_st2 = 0;
    data_prop_d0_st3 = 0;
    data_prop_d1_st3 = 0;
    data_prop_d2_st3 = 0;
    data_prop_d3_st3 = 0;
    data_prop_d0_st4 = 0;
    data_prop_d1_st4 = 0;
    data_prop_d2_st4 = 0;
    data_prop_d3_st4 = 0;
    data_prop_d0_st5 = 0;
    data_prop_d1_st5 = 0;
    data_prop_d2_st5 = 0;
    data_prop_d3_st5 = 0;
  end


endmodule

