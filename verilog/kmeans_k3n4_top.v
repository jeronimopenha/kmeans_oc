

module kmeans_k3n4_top #
(
  parameter data_width = 8,
  parameter input_data_qty_bit_width = 8,
  parameter input_data_qty = 256,
  parameter mem_d0_init_file = "./db/d0.txt",
  parameter mem_d1_init_file = "./db/d1.txt",
  parameter mem_d2_init_file = "./db/d2.txt",
  parameter mem_d3_init_file = "./db/d3.txt",
  parameter k0_d0_initial = 0,
  parameter k0_d1_initial = 0,
  parameter k0_d2_initial = 0,
  parameter k0_d3_initial = 0,
  parameter k1_d0_initial = 1,
  parameter k1_d1_initial = 1,
  parameter k1_d2_initial = 1,
  parameter k1_d3_initial = 1,
  parameter k2_d0_initial = 2,
  parameter k2_d1_initial = 2,
  parameter k2_d2_initial = 2,
  parameter k2_d3_initial = 2
)
(
  input clk,
  input rst,
  input start
);


endmodule

