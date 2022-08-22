from veriloggen import *
from math import ceil, log2
import util as _u


class KMeans:
    _instance = None

    def __init__(
            self,
            d_bits: int = 16,
            n_data: int = 256
    ):
        self.d_bits = d_bits
        self.n_data = n_data
        self.cache = {}

    def get(self):
        pass

    def create_RAM(self) -> Module:
        name = 'RAM'
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)
        read_f = m.Parameter('read_f', 0)
        init_file = m.Parameter('init_file', 'mem_file.txt')
        write_f = m.Parameter('write_f', 0)
        output_file = m.Parameter('output_file', 'mem_out_file.txt')
        depth = m.Parameter('depth', 8)
        width = m.Parameter('width', 16)

        clk = m.Input('clk')
        # rd = m.Input('rd')
        rd_addr = m.Input('rd_addr', depth)
        out = m.Output('out', width)

        wr = m.Input('wr')
        wr_addr = m.Input('wr_addr', depth)
        wr_data = m.Input('wr_data', width)

        mem = m.Reg('mem', width, Power(2, depth))

        out.assign(mem[rd_addr])

        m.Always(Posedge(clk))(
            If(wr)(
                mem[wr_addr](wr_data)
            ),
        )

        m.EmbeddedCode('  //synthesis translate_off')
        m.Always(Posedge(clk))(
            If(AndList(wr, write_f))(
                Systask('writememh', output_file, mem)
            ),
        )
        
        m.Initial(
            If(read_f)(
                Systask('readmemh', init_file, mem),
            )
        )
        m.EmbeddedCode('  //synthesis translate_on')

        self.cache[name] = m
        return m

    def create_counter(self):
        name = 'counter'
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)

        _u.initialize_regs(m)
        self.cache[name] = m
        return m

    def create_kmeans_core(self):
        name = 'kmeans_core'
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)

        d_width = m.Parameter('d_width', 16)

        clk = m.Input('clk')

        d0 = m.Input('d0', d_width)
        d1 = m.Input('d1', d_width)

        k0_0 = m.Input('k0_0', d_width)
        k0_1 = m.Input('k0_1', d_width)
        k1_0 = m.Input('k1_0', d_width)
        k1_1 = m.Input('k1_1', d_width)

        d0_out = m.OutputReg('d0_out', d_width)
        d1_out = m.OutputReg('d1_out', d_width)
        k_out = m.OutputReg('k_out')

        m.EmbeddedCode('//st1 outputs - sub data kx')
        st0_00 = m.Reg('st0_00', d_width)
        st0_01 = m.Reg('st0_01', d_width)
        st0_10 = m.Reg('st0_10', d_width)
        st0_11 = m.Reg('st0_11', d_width)
        st0_d0 = m.Reg('st0_d0', d_width)
        st0_d1 = m.Reg('st0_d1', d_width)

        m.EmbeddedCode('//st1 outputs - pow')
        st1_00 = m.Reg('st1_00', d_width*2)
        st1_01 = m.Reg('st1_01', d_width*2)
        st1_10 = m.Reg('st1_10', d_width*2)
        st1_11 = m.Reg('st1_11', d_width*2)
        st1_d0 = m.Reg('st1_d0', d_width)
        st1_d1 = m.Reg('st1_d1', d_width)

        m.EmbeddedCode('//st2 outputs - add')
        st2_0 = m.Reg('st2_0', (d_width*2)+1)
        st2_1 = m.Reg('st2_1', (d_width*2)+1)
        st2_d0 = m.Reg('st2_d0', d_width)
        st2_d1 = m.Reg('st2_d1', d_width)

        m.Always(Posedge(clk))(
            st0_00(d0 - k0_0),
            st0_01(d1 - k0_1),
            st0_10(d0 - k1_0),
            st0_11(d1 - k1_1),
            st0_d0(d0),
            st0_d1(d1),

            st1_00(st0_00*st0_00),
            st1_01(st0_01*st0_01),
            st1_10(st0_10*st0_10),
            st1_11(st0_11*st0_11),
            st1_d0(st0_d0),
            st1_d1(st0_d1),

            st2_0(st1_00 + st1_01),
            st2_1(st1_10 + st1_11),
            st2_d0(st1_d0),
            st2_d1(st1_d1),

            d0_out(st2_d0),
            d1_out(st2_d1),
            k_out(Mux(st2_0 < st2_1, 0, 1)),
        )

        _u.initialize_regs(m)
        self.cache[name] = m
        return m

    def create_kmeans_top(self):
        name = 'kmeans_k2n2_top'
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)

        mem_d0_init_file = m.Parameter('mem_d0_init_file', './db/d0.txt')
        mem_d1_init_file = m.Parameter('mem_d1_init_file', './db/d1.txt')
        data_width = m.Parameter('data_width', 16)
        n_input_data_b_depth = m.Parameter('n_input_data_b_depth', 8)
        n_input_data = m.Parameter('n_input_data', 256)
        acc_sum_width = m.Parameter('acc_sum_width', ceil(log2(256)))
        p_k0_0 = m.Parameter('p_k0_0', 0, data_width)
        p_k0_1 = m.Parameter('p_k0_1', 0, data_width)
        p_k1_0 = m.Parameter('p_k1_0', 1, data_width)
        p_k1_1 = m.Parameter('p_k1_1', 1, data_width)

        clk = m.Input('clk')
        rst = m.Input('rst')
        start = m.Input('start')

        m.EmbeddedCode('\n//control regs and wires - begin')
        kmeans_rst = m.Reg('kmeans_rst')
        kmeans_rdy = m.Reg('kmeans_rdy')
        acc_rdy = m.Reg('acc_rdy')
        class_done = m.Reg('class_done')
        data_counter_en = m.Reg('data_counter_en')
        data_counter = m.Reg('data_counter', n_input_data_b_depth+1)
        m.EmbeddedCode('//control regs and wires - end')

        m.EmbeddedCode('\n//Centroids regs and wires - begin')
        up_centroids = m.Wire('up_centroids')

        m.EmbeddedCode('//centroids values')
        k0_0 = m.Reg('k0_0', data_width)
        k0_1 = m.Reg('k0_1', data_width)
        k1_0 = m.Reg('k1_0', data_width)
        k1_1 = m.Reg('k1_1', data_width)

        m.EmbeddedCode('//new centroids values')
        k0_0_n = m.Reg('k0_0_n', data_width)
        k0_1_n = m.Reg('k0_1_n', data_width)
        k1_0_n = m.Reg('k1_0_n', data_width)
        k1_1_n = m.Reg('k1_1_n', data_width)

        m.EmbeddedCode('//centroids data counters')
        k0_counter = m.Reg('k0_counter', n_input_data_b_depth+1)
        k1_counter = m.Reg('k1_counter', n_input_data_b_depth+1)
        m.EmbeddedCode('//Centroids regs - end')

        m.EmbeddedCode('\n//input data memories regs and wires - begin')
        m.EmbeddedCode('//d0 memory')
        mem_d0_rd_addr = m.Wire('mem_d0_rd_addr', n_input_data_b_depth)
        mem_d0_out = m.Wire('mem_d0_out', data_width)

        m.EmbeddedCode('//d1 memory')
        mem_d1_rd_addr = m.Wire('mem_d1_rd_addr', n_input_data_b_depth)
        mem_d1_out = m.Wire('mem_d1_out', data_width)
        m.EmbeddedCode('//input data memories regs and wires - end')

        m.EmbeddedCode('\n//kmeans pipeline (kp) wires and regs - begin')
        m.EmbeddedCode('//st1 outputs - sub data kx')
        kp_st0_sub00 = m.Reg('kp_st0_sub00', data_width)
        kp_st0_sub01 = m.Reg('kp_st0_sub01', data_width)
        kp_st0_sub10 = m.Reg('kp_st0_sub10', data_width)
        kp_st0_sub11 = m.Reg('kp_st0_sub11', data_width)
        kp_st0_d0 = m.Reg('kp_st0_d0', data_width)
        kp_st0_d1 = m.Reg('kp_st0_d1', data_width)

        m.EmbeddedCode('//st1 outputs - sqr')
        kp_st1_sqr00 = m.Reg('kp_st1_sqr00', data_width*2)
        kp_st1_sqr01 = m.Reg('kp_st1_sqr01', data_width*2)
        kp_st1_sqr10 = m.Reg('kp_st1_sqr10', data_width*2)
        kp_st1_sqr11 = m.Reg('kp_st1_sqr11', data_width*2)
        kp_st1_d0 = m.Reg('kp_st1_d0', data_width)
        kp_st1_d1 = m.Reg('kp_st1_d1', data_width)

        m.EmbeddedCode('//st2 outputs - add')
        kp_st2_add0 = m.Reg('kp_st2_add0', (data_width*2)+1)
        kp_st2_add1 = m.Reg('kp_st2_add1', (data_width*2)+1)
        kp_st2_d0 = m.Reg('kp_st2_d0', data_width)
        kp_st2_d1 = m.Reg('kp_st2_d1', data_width)

        m.EmbeddedCode('//st3 outputs - kmeans decision')
        kp_st3_d0_out = m.Reg('kp_st3_d0_out', data_width)
        kp_st3_d1_out = m.Reg('kp_st3_d1_out', data_width)
        kp_st3_k_out = m.Reg('kp_st3_k_out')
        m.EmbeddedCode('//kmeans pipeline (kp) wires and regs - end')

        m.EmbeddedCode(
            '\n//kmeans accumulator memories wires and regs - begin')

        mem_sum_init_rst = m.Reg('mem_sum_init_rst')
        mem_sum_init_rst_wr_addr = m.Reg('mem_sum_init_rst_wr_addr')

        bck_rd = m.Reg('bck_rd')
        bck_rd_addr = m.Reg('bck_rd_addr')

        m.EmbeddedCode('//sum init memory init d0')
        mem_sum_d0_init_rd_addr = m.Wire('mem_sum_d0_init_rd_addr')
        mem_sum_d0_init_out = m.Wire('mem_sum_d0_init_out')
        mem_sum_d0_init_wr = m.Wire('mem_sum_d0_init_wr')
        mem_sum_d0_init_wr_addr = m.Wire('mem_sum_d0_init_wr_addr')
        mem_sum_d0_init_wr_data = m.Wire('mem_sum_d0_init_wr_data')

        m.EmbeddedCode('//sum init memory init d1')
        mem_sum_d1_init_rd_addr = m.Wire('mem_sum_d1_init_rd_addr')
        mem_sum_d1_init_out = m.Wire('mem_sum_d1_init_out')
        mem_sum_d1_init_wr = m.Wire('mem_sum_d1_init_wr')
        mem_sum_d1_init_wr_addr = m.Wire('mem_sum_d1_init_wr_addr')
        mem_sum_d1_init_wr_data = m.Wire('mem_sum_d1_init_wr_data')

        m.EmbeddedCode('//sum memory d0')
        mem_sum_d0_rd_addr = m.Wire('mem_sum_d0_rd_addr')
        mem_sum_d0_out = m.Wire('mem_sum_d0_out', acc_sum_width)
        mem_sum_d0_wr = m.Wire('mem_sum_d0_wr')
        mem_sum_d0_wr_addr = m.Wire('mem_sum_d0_wr_addr')
        mem_sum_d0_wr_data = m.Wire('mem_sum_d0_wr_data', acc_sum_width)

        m.EmbeddedCode('//sum  memory d1')
        mem_sum_d1_rd_addr = m.Wire('mem_sum_d1_rd_addr')
        mem_sum_d1_out = m.Wire('mem_sum_d1_out', acc_sum_width)
        mem_sum_d1_wr = m.Wire('mem_sum_d1_wr')
        mem_sum_d1_wr_addr = m.Wire('mem_sum_d1_wr_addr')
        mem_sum_d1_wr_data = m.Wire('mem_sum_d1_wr_data', acc_sum_width)
        m.EmbeddedCode('\n//kmeans accumulator memory wires and regs - end')

        m.EmbeddedCode('\n//Implementation - begin')

        m.EmbeddedCode('\n//centroids values control')
        m.Always(Posedge(clk))(
            If(rst)(
                k0_0(p_k0_0),
                k0_1(p_k0_1),
                k1_0(p_k1_0),
                k1_1(p_k1_1),
            ).Elif(up_centroids)(
                k0_0(k0_0_n),
                k0_1(k0_1_n),
                k1_0(k1_0_n),
                k1_1(k1_1_n),
            )
        )

        m.EmbeddedCode('\n//kmeans pipeline (kp) implementation')

        m.Always(Posedge(clk))(
            kp_st0_sub00(mem_d0_out - k0_0),
            kp_st0_sub01(mem_d1_out - k0_1),
            kp_st0_sub10(mem_d0_out - k1_0),
            kp_st0_sub11(mem_d1_out - k1_1),
            kp_st0_d0(mem_d0_out),
            kp_st0_d1(mem_d1_out),
            kp_st1_sqr00(kp_st0_sub00*kp_st0_sub00),
            kp_st1_sqr01(kp_st0_sub01*kp_st0_sub01),
            kp_st1_sqr10(kp_st0_sub10*kp_st0_sub10),
            kp_st1_sqr11(kp_st0_sub11*kp_st0_sub11),
            kp_st1_d0(kp_st0_d0),
            kp_st1_d1(kp_st0_d1),
            kp_st2_add0(kp_st1_sqr00 + kp_st1_sqr01),
            kp_st2_add1(kp_st1_sqr10 + kp_st1_sqr11),
            kp_st2_d0(kp_st1_d0),
            kp_st2_d1(kp_st1_d1),
            kp_st3_k_out(Mux(kp_st2_add0 < kp_st2_add1, 0, 1)),
            kp_st3_d0_out(kp_st2_d0),
            kp_st3_d1_out(kp_st2_d1),
        )

        m.EmbeddedCode(
            '\n//kmeans accumulator memories implementation')
        m.EmbeddedCode('//sum init memory d0')
        mem_sum_d0_init_rd_addr.assign(kp_st3_k_out)
        mem_sum_d0_init_wr.assign(Mux(mem_sum_init_rst, 1, acc_rdy))
        mem_sum_d0_init_wr_addr.assign(
            Mux(mem_sum_init_rst, mem_sum_init_rst_wr_addr, kp_st3_k_out))
        mem_sum_d0_init_wr_data.assign(Mux(mem_sum_init_rst, 0, 1))

        m.EmbeddedCode('//sum init memory d1')
        mem_sum_d1_init_rd_addr.assign(kp_st3_k_out)
        mem_sum_d1_init_wr.assign(Mux(mem_sum_init_rst, 1, acc_rdy))
        mem_sum_d1_init_wr_addr.assign(
            Mux(mem_sum_init_rst, mem_sum_init_rst_wr_addr, kp_st3_k_out))
        mem_sum_d1_init_wr_data.assign(Mux(mem_sum_init_rst, 0, 1))

        m.EmbeddedCode('//sum memory d0')
        mem_sum_d0_rd_addr.assign(Mux(bck_rd, bck_rd_addr, kp_st3_k_out))
        mem_sum_d0_wr.assign(acc_rdy)
        mem_sum_d0_wr_addr.assign(kp_st3_k_out)
        mem_sum_d0_wr_data.assign(
            Mux(mem_sum_d0_init_out, mem_sum_d0_out + kp_st3_d0_out, kp_st3_d0_out))

        m.EmbeddedCode('//sum memory d1')
        mem_sum_d1_rd_addr.assign(Mux(bck_rd, bck_rd_addr, kp_st3_k_out))
        mem_sum_d1_wr.assign(acc_rdy)
        mem_sum_d1_wr_addr.assign(kp_st3_k_out)
        mem_sum_d1_wr_data.assign(
            Mux(mem_sum_d1_init_out, mem_sum_d1_out + kp_st3_d1_out, kp_st3_d1_out))

        m.EmbeddedCode('\n//init memories reset')
        m.Always(Posedge(clk))(
            If(kmeans_rst)(
                kmeans_rdy(0),
                mem_sum_init_rst(1),
                mem_sum_init_rst_wr_addr(0)
            ).Else(
                If(Uand(mem_sum_init_rst_wr_addr))(
                    mem_sum_init_rst(0),
                    kmeans_rdy(1),
                ).Else(
                    mem_sum_init_rst_wr_addr.inc(),
                ),
            )
        )

        m.EmbeddedCode('\n//centroids data counters')
        m.Always(Posedge(clk))(
            If(kmeans_rst)(
                k0_counter(0),
                k1_counter(0),
            ).Else(
                Case(Cat(acc_rdy, kp_st3_k_out))(
                    When(Int(2, 2, 2))(
                        k0_counter.inc()
                    ),
                    When(Int(3, 2, 2))(
                        k1_counter.inc()
                    ),
                )
            )
        )

        m.EmbeddedCode('\n//data and latency counter exec')
        m.Always(Posedge(clk))(
            If(kmeans_rst)(
                data_counter(0),
                acc_rdy(0),
                class_done(0),
            ).Elif(data_counter_en)(
                If(data_counter == n_input_data - 1)(
                    class_done(1),
                    acc_rdy(0),
                ).Else(
                    If(data_counter == 3)(
                        acc_rdy(1)
                    ),
                    data_counter.inc()
                )
            )
        )

        fsm_kmeans_control = m.Reg('fsm_kmeans_control', 6)
        fsm_kc_kmeans_rst = m.Localparam('fsm_kc_kmeans_rst', 0)
        fsm_kc_wait_init = m.Localparam('fsm_kc_wait_init', 1)
        fsm_kc_wait_class = m.Localparam('fsm_kc_wait_class', 2)

        m.EmbeddedCode('\n//fsm control')
        m.Always(Posedge(clk))(
            If(rst)(
                kmeans_rst(0),
                up_centroids(0),
                fsm_kmeans_control(fsm_kc_kmeans_rst)
            ).Elif(start)(
                Case(fsm_kmeans_control)(
                    When(fsm_kc_kmeans_rst)(
                        kmeans_rst(1),
                        fsm_kmeans_control(fsm_kc_wait_init),
                    ),
                    When(fsm_kc_wait_init)(
                        kmeans_rst(0),
                        If(kmeans_rdy)(
                            data_counter_en(1),
                            fsm_kmeans_control(fsm_kc_wait_class)
                        )
                    ),
                    When(fsm_kc_wait_class)(
                        If(class_done)(
                            data_counter_en(0),
                        )
                    )
                )
            )
        )

        m.EmbeddedCode('\n//Implementation - end')

        m.EmbeddedCode('\n//Modules instantiation - begin')
        m.EmbeddedCode('\n//kmeans input data memories')
        m.EmbeddedCode('//d0 memory')
        aux = self.create_RAM()
        par = [
            ('read_f', Int(1, 1, 2)),
            ('init_file', mem_d0_init_file),
            ('write_f', Int(0, 1, 2)),
            ('depth', n_input_data_b_depth),
            ('width', data_width)
        ]
        con = [
            ('clk', clk),
            ('rd_addr', data_counter[0:n_input_data_b_depth]),
            ('out', mem_d0_out),
        ]
        m.Instance(aux, '%s_d0' % aux.name, par, con)

        m.EmbeddedCode('//d1 memory')
        par = [
            ('read_f', Int(1, 1, 2)),
            ('init_file', mem_d1_init_file),
            ('write_f', Int(0, 1, 2)),
            ('depth', n_input_data_b_depth),
            ('width', data_width)
        ]
        con = [
            ('clk', clk),
            ('rd_addr', data_counter[0:n_input_data_b_depth]),
            ('out', mem_d1_out),
        ]
        m.Instance(aux, '%s_d1' % aux.name, par, con)

        m.EmbeddedCode('\n//Sum memories and init memories')
        m.EmbeddedCode('//d0 init memory')
        par = [
            ('read_f', Int(0, 1, 2)),
            ('write_f', Int(0, 1, 2)),
            ('depth', 1),
            ('width', 1)
        ]
        con = [
            ('clk', clk),
            ('rd_addr', mem_sum_d0_init_rd_addr),
            ('out', mem_sum_d0_init_out),
            ('wr',mem_sum_d0_init_wr),
            ('wr_addr', mem_sum_d0_init_wr_addr),
            ('wr_data', mem_sum_d0_init_wr_data),
        ]
        m.Instance(aux, '%s_sum_d0_init' % aux.name, par, con)

        m.EmbeddedCode('//d1 init memory')
        par = [
            ('read_f', Int(0, 1, 2)),
            ('write_f', Int(0, 1, 2)),
            ('depth', 1),
            ('width', 1)
        ]
        con = [
            ('clk', clk),
            ('rd_addr', mem_sum_d1_init_rd_addr),
            ('out', mem_sum_d1_init_out),
            ('wr',mem_sum_d1_init_wr),
            ('wr_addr', mem_sum_d1_init_wr_addr),
            ('wr_data', mem_sum_d1_init_wr_data),
        ]
        m.Instance(aux, '%s_sum_d1_init' % aux.name, par, con)

        m.EmbeddedCode('//d0 sum memory')
        par = [
            ('read_f', Int(0, 1, 2)),
            ('write_f', Int(0, 1, 2)),
            ('depth', 1),
            ('width', acc_sum_width)
        ]
        con = [
            ('clk', clk),
            ('rd_addr', mem_sum_d0_rd_addr),
            ('out', mem_sum_d0_out),
            ('wr',mem_sum_d0_wr),
            ('wr_addr', mem_sum_d0_wr_addr),
            ('wr_data', mem_sum_d0_wr_data),
        ]
        m.Instance(aux, '%s_sum_d0' % aux.name, par, con)

        m.EmbeddedCode('//d1 sum memory')
        par = [
            ('read_f', Int(0, 1, 2)),
            ('write_f', Int(0, 1, 2)),
            ('depth', 1),
            ('width', acc_sum_width)
        ]
        con = [
            ('clk', clk),
            ('rd_addr', mem_sum_d1_rd_addr),
            ('out', mem_sum_d1_out),
            ('wr',mem_sum_d1_wr),
            ('wr_addr', mem_sum_d1_wr_addr),
            ('wr_data', mem_sum_d1_wr_data),
        ]
        m.Instance(aux, '%s_sum_d1' % aux.name, par, con)

        m.EmbeddedCode('\n//Modules instantiation - end')

        _u.initialize_regs(m)
        self.cache[name] = m
        return m

    def create_kmeans_testbench(self):
        pass


k = KMeans()
k.create_kmeans_top().to_verilog('./verilog/kmeans_top.v')
