from ctypes import util
from pygame import K_F10
from veriloggen import *
import util as _u


class KComponents:
    _instance = None

    def __init__(
            self,
            d_bits: int = 16,
            n_data: int = 256
    ):
        self.d_bits = d_bits
        self.n_data = n_data
        self.cache = {}

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

    def create_kmeans_fsm(self):
        name = 'kmeans_fsm'
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)

        _u.initialize_regs(m)
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
        name = 'kmeans_top'
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)

        _u.initialize_regs(m)
        self.cache[name] = m
        return m

    def create_kmeans_testbench(self):
        pass


k = KComponents()
print(k.create_kmeans_core().to_verilog())
