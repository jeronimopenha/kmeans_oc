

module kmeans_k2n2_top #
(
  parameter mem_d0_init_file = "./db/d0.txt",
  parameter mem_d1_init_file = "./db/d1.txt",
  parameter data_width = 16,
  parameter n_input_data_b_depth = 8,
  parameter n_input_data = 256,
  parameter acc_sum_width = 8,
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


  //control regs and wires - begin
  reg kmeans_rdy;
  reg acc_rdy;
  reg ltcy_counter_rst;
  reg ltcy_counter_en;
  reg [2-1:0] ltcy_counter;
  //control regs and wires - end

  //Centroids regs and wires - begin
  wire up_centroids;
  //centroids values
  reg [data_width-1:0] k0_0;
  reg [data_width-1:0] k0_1;
  reg [data_width-1:0] k1_0;
  reg [data_width-1:0] k1_1;
  //new centroids values
  reg [data_width-1:0] k0_0_n;
  reg [data_width-1:0] k0_1_n;
  reg [data_width-1:0] k1_0_n;
  reg [data_width-1:0] k1_1_n;
  //centroids data counters
  reg [n_input_data_b_depth+1-1:0] k0_counter;
  reg [n_input_data_b_depth+1-1:0] k1_counter;
  //Centroids regs - end

  //input data memories regs and wires - begin
  //d0 memory
  wire [n_input_data_b_depth-1:0] mem_d0_rd_addr;
  wire [data_width-1:0] mem_d0_out;
  //d1 memory
  wire [n_input_data_b_depth-1:0] mem_d1_rd_addr;
  wire [data_width-1:0] mem_d1_out;
  //input data memories regs and wires - end

  //kmeans pipeline (kp) wires and regs - begin
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

  //kmeans accumulator memories wires and regs - begin
  reg mem_sum_init_rst;
  reg mem_sum_init_rst_wr_addr;
  //sum init memory init d0
  wire mem_sum_d0_init_rd_addr;
  wire mem_sum_d0_init_out;
  wire mem_sum_d0_init_wr;
  wire mem_sum_d0_init_wr_addr;
  wire mem_sum_d0_init_wr_data;
  //sum init memory init d1
  wire mem_sum_d1_init_rd_addr;
  wire mem_sum_d1_init_out;
  wire mem_sum_d1_init_wr;
  wire mem_sum_d1_init_wr_addr;
  wire mem_sum_d1_init_wr_data;
  //sum memory d0
  wire mem_sum_d0_rd_addr;
  wire [acc_sum_width-1:0] mem_sum_d0_out;
  wire mem_sum_d0_wr;
  wire mem_sum_d0_wr_addr;
  wire [acc_sum_width-1:0] mem_sum_d0_wr_data;
  //sum  memory d1
  wire mem_sum_d1_rd_addr;
  wire [acc_sum_width-1:0] mem_sum_d1_out;
  wire mem_sum_d1_wr;
  wire mem_sum_d1_wr_addr;
  wire [acc_sum_width-1:0] mem_sum_d1_wr_data;

  //kmeans accumulator memory wires and regs - end

  //Implementation - begin

  //centroids values control - begin

  always @(posedge clk) begin
    if(rst) begin
      k0_0 <= p_k0_0;
      k0_1 <= p_k0_1;
      k1_0 <= p_k1_0;
      k1_1 <= p_k1_1;
    end else begin
      if(up_centroids) begin
        k0_0 <= k0_0_n;
        k0_1 <= k0_1_n;
        k1_0 <= k1_0_n;
        k1_1 <= k1_1_n;
      end 
    end
  end

  //centroids values control - end

  //kmeans pipeline (kp) implementation - begin

  always @(posedge clk) begin
    kp_st0_sub00 <= mem_d0_out - k0_0;
    kp_st0_sub01 <= mem_d1_out - k0_1;
    kp_st0_sub10 <= mem_d0_out - k1_0;
    kp_st0_sub11 <= mem_d1_out - k1_1;
    kp_st0_d0 <= mem_d0_out;
    kp_st0_d1 <= mem_d1_out;
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

  //kmeans accumulator memories implementation - begin
  //sum init memory d0
  assign mem_sum_d0_init_rd_addr = kp_st3_k_out;
  assign mem_sum_d0_init_wr = (mem_sum_init_rst)? 1 : acc_rdy;
  assign mem_sum_d0_init_wr_addr = (mem_sum_init_rst)? mem_sum_init_rst_wr_addr : kp_st3_k_out;
  assign mem_sum_d0_init_wr_data = (mem_sum_init_rst)? 0 : 1;
  //sum init memory d1
  assign mem_sum_d1_init_rd_addr = kp_st3_k_out;
  assign mem_sum_d1_init_wr = (mem_sum_init_rst)? 1 : acc_rdy;
  assign mem_sum_d1_init_wr_addr = (mem_sum_init_rst)? mem_sum_init_rst_wr_addr : kp_st3_k_out;
  assign mem_sum_d1_init_wr_data = (mem_sum_init_rst)? 0 : 1;
  //sum memory d0
  assign mem_sum_d0_rd_addr = kp_st3_k_out;
  assign mem_sum_d0_wr = acc_rdy;
  assign mem_sum_d0_wr_addr = kp_st3_k_out;
  assign mem_sum_d0_wr_data = (mem_sum_d0_init_out)? mem_sum_d0_out + kp_st3_d0_out : kp_st3_d0_out;
  //sum memory d1
  assign mem_sum_d1_rd_addr = kp_st3_k_out;
  assign mem_sum_d1_wr = acc_rdy;
  assign mem_sum_d1_wr_addr = kp_st3_k_out;
  assign mem_sum_d1_wr_data = (mem_sum_d1_init_out)? mem_sum_d1_out + kp_st3_d1_out : kp_st3_d1_out;

  //init memories reset

  always @(posedge clk) begin
    if(rst) begin
      kmeans_rdy <= 0;
      mem_sum_init_rst <= 1;
      mem_sum_init_rst_wr_addr <= 0;
    end else begin
      if(start) begin
        if(&mem_sum_init_rst_wr_addr) begin
          mem_sum_init_rst <= 0;
          kmeans_rdy <= 1;
        end else begin
          mem_sum_init_rst_wr_addr <= mem_sum_init_rst_wr_addr + 1;
        end
      end 
    end
  end


  //centroids data counters

  always @(posedge clk) begin
    if(rst) begin
      k0_counter <= 0;
      k1_counter <= 0;
    end else begin
      case({ acc_rdy, kp_st3_k_out })
        2'b10: begin
          k0_counter <= k0_counter + 1;
        end
        2'b11: begin
          k1_counter <= k1_counter + 1;
        end
      endcase
    end
  end


  //latency counter exec

  always @(posedge clk) begin
    if(ltcy_counter_rst) begin
      ltcy_counter <= 0;
      acc_rdy <= 0;
    end else begin
      if(ltcy_counter_en) begin
        if(ltcy_counter == 3) begin
          acc_rdy <= 1;
        end else begin
          ltcy_counter <= ltcy_counter + 1;
        end
      end 
    end
  end


  //kmeans accumulator memory implementation - end

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
    kmeans_rdy = 0;
    acc_rdy = 0;
    ltcy_counter_rst = 0;
    ltcy_counter_en = 0;
    ltcy_counter = 0;
    k0_0 = 0;
    k0_1 = 0;
    k1_0 = 0;
    k1_1 = 0;
    k0_0_n = 0;
    k0_1_n = 0;
    k1_0_n = 0;
    k1_1_n = 0;
    k0_counter = 0;
    k1_counter = 0;
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
    mem_sum_init_rst = 0;
    mem_sum_init_rst_wr_addr = 0;
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

