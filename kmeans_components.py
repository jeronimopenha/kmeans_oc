from veriloggen import *
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

        m = Module(name)

        mem_d0_init_file = m.Parameter('mem_d0_init_file', './db/d0.txt')
        mem_d1_init_file = m.Parameter('mem_d1_init_file', './db/d1.txt')
        data_width = m.Parameter('data_width', 16)
        n_input_data_b_depth = m.Parameter('n_input_data_b_depth', 8)
        n_input_data = m.Parameter('n_input_data', 256)
        p_k0_0 = m.Parameter('p_k0_0', 0, data_width)
        p_k0_1 = m.Parameter('p_k0_1', 0, data_width)
        p_k1_0 = m.Parameter('p_k1_0', 1, data_width)
        p_k1_1 = m.Parameter('p_k1_1', 1, data_width)

        clk = m.Input('clk')
        rst = m.Input('rst')
        start = m.Input('start')

        m.EmbeddedCode('//Centroids regs - begin')
        k0_0 = m.Reg('k0_0', data_width)
        k0_1 = m.Reg('k0_1', data_width)
        k1_0 = m.Reg('k1_0', data_width)
        k1_1 = m.Reg('k1_1', data_width)
        m.EmbeddedCode('//Centroids regs - end')

        m.EmbeddedCode('\n//input data memories regs and wires - begin')
        mem_d0_rd_addr = m.Wire('mem_d0_rd_addr', n_input_data_b_depth)
        mem_d0_out = m.Wire('mem_d0_out', data_width)
        mem_d1_rd_addr = m.Wire('mem_d1_rd_addr', n_input_data_b_depth)
        mem_d1_out = m.Wire('mem_d1_out', data_width)
        m.EmbeddedCode('//input data memories regs and wires - end')

        m.EmbeddedCode('\n//kmeans pipeline (kp) wires and regs - begin')
        m.EmbeddedCode('//data input')
        kp_d0 = m.Wire('kp_d0', data_width)
        kp_d1 = m.Wire('kp_d1', data_width)

        m.EmbeddedCode('//centroids')
        kp_k0_0 = m.Wire('kp_k0_0', data_width)
        kp_k0_1 = m.Wire('kp_k0_1', data_width)
        kp_k1_0 = m.Wire('kp_k1_0', data_width)
        kp_k1_1 = m.Wire('kp_k1_1', data_width)

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

        m.EmbeddedCode('\n//Implementation - begin')

        m.EmbeddedCode('\n//centroids values control - begin')
        m.Always(Posedge(clk))(
            If(rst)(
                k0_0(p_k0_0),
                k0_1(p_k0_1),
                k1_0(p_k1_0),
                k1_1(p_k1_1),
            )
        )
        m.EmbeddedCode('//centroids values control - end')

        m.EmbeddedCode('\n//kmeans pipeline (kp) implementation - begin')
        kp_k0_0.assign(k0_0)
        kp_k0_1.assign(k0_1)
        kp_k1_0.assign(k1_0)
        kp_k1_1.assign(k1_1)
        kp_d0.assign(mem_d0_out)
        kp_d1.assign(mem_d1_out)

        m.Always(Posedge(clk))(
            kp_st0_sub00(kp_d0 - kp_k0_0),
            kp_st0_sub01(kp_d1 - kp_k0_1),
            kp_st0_sub10(kp_d0 - kp_k1_0),
            kp_st0_sub11(kp_d1 - kp_k1_1),
            kp_st0_d0(kp_d0),
            kp_st0_d1(kp_d1),
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
        m.EmbeddedCode('//kmeans pipeline (kp) implementation - end')

        m.EmbeddedCode('\n//Implementation - end')

        m.EmbeddedCode('\n//Modules instantiation - begin')
        m.EmbeddedCode('\n//kmeans input data memories - begin')
        m.EmbeddedCode('//d0 memory')
        aux = self.create_RAM()
        par = [
            ('init_file', mem_d0_init_file),
            ('write_f', Int(0, 1, 2)),
            ('depth', n_input_data_b_depth),
            ('width', data_width)
        ]
        con = [
            ('clk', clk),
            ('rd_addr', mem_d0_rd_addr),
            ('out', mem_d0_out),
        ]
        m.Instance(aux, '%s_d0' % aux.name, par, con)

        m.EmbeddedCode('//d1 memory')
        par = [
            ('init_file', mem_d1_init_file),
            ('write_f', Int(0, 1, 2)),
            ('depth', n_input_data_b_depth),
            ('width', data_width)
        ]
        con = [
            ('clk', clk),
            ('rd_addr', mem_d1_rd_addr),
            ('out', mem_d1_out),
        ]
        m.Instance(aux, '%s_d1' % aux.name, par, con)
        m.EmbeddedCode('\n//kmeans input data memories - end')
        m.EmbeddedCode('\n//Modules instantiation - end')

        _u.initialize_regs(m)
        self.cache[name] = m
        return m

    def create_kmeans_testbench(self):
        pass


k = KMeans()
k.create_kmeans_top().to_verilog('./verilog/kmeans_top.v')
