from ast import Pow
from pickle import EMPTY_LIST
from queue import Empty
from re import A
from veriloggen import *
from math import ceil, log2
import util as _u


class KMeans:
    _instance = None

    def __init__(
            self,
            input_data_width: int = 16,
            input_data_qty: int = 256,
            dimensions_qty: int = 2,
            centroids_qty: int = 2
    ):
        self.input_data_width = input_data_width
        self.input_data_qty = input_data_qty
        self.dimensions_qty = dimensions_qty
        self.centroids_qty = centroids_qty
        self.centroid_id_width = ceil(log2(self.centroids_qty))
        self.add_dict, self.add_ltcy = _u.create_reduce_tree(
            self.dimensions_qty)
        self.cmp_dict, self.cmp_ltcy = _u.create_reduce_tree(
            self.centroids_qty)

        self.cache = {}

    def get(self):
        pass

    def create_kmeans_pipeline(self):
        input_data_width_v = self.input_data_width
        input_data_qty_v = self.input_data_qty
        dimensions_qty_v = self.dimensions_qty
        centroids_qty_v = self.centroids_qty
        centroid_id_width_v = self.centroid_id_width
        # 1 - sub, 1 - sqr, ceil(log2(dimensions_qty)) add, ceil(log2(centroids_qty)) comp
        pipe_latency_delay_v = 1+1 + \
            ceil(log2(dimensions_qty_v)) + ceil(log2(centroids_qty_v))
        pipe_latency_delay_with_v = ceil(log2(pipe_latency_delay_v))

        name = 'kmeans_pipeline_k%d_d%d' % (centroids_qty_v, dimensions_qty_v)
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)

        centroids_vec = []
        input_data_vec = []
        output_data_vec = []

        input_data_width = m.Parameter('input_data_width', input_data_width_v)

        clk = m.Input('clk')

        for i in range(centroids_qty_v):
            centroids_vec.append([])
            for j in range(dimensions_qty_v):
                centroids_vec[i].append(
                    m.Input('centroid%d_d%d' % (i, j), input_data_width))

        for i in range(dimensions_qty_v):
            input_data_vec.append(m.Input('input_data%d' %
                                  i, input_data_width))

        n = self.dimensions_qty
        for i in range(dimensions_qty_v):
            output_data_vec.append(m.Output(
                'output_data%d' % i, input_data_width))

        selected_centroid = m.Output('selected_centroid', centroid_id_width_v)
        # latency_delay = m.Output('latency_delay',pipe_latency_delay_with_v)
        m.EmbeddedCode('//Latency delay')
        m.EmbeddedCode(
            '//1(sub) + 1(sqr) + ceil(log2(dimensions_qty)) (add) + ceil(log2(centroids_qty)) (comp)')
        m.EmbeddedCode('//for this one it is %d' % pipe_latency_delay_v)

        # pipes regs
        # st0 - sub
        m.EmbeddedCode('\n//pipeline stage 0 - Sub')
        st0_regs_vec = []
        for i in range(centroids_qty_v):
            st0_regs_vec.append([])
            for j in range(dimensions_qty_v):
                st0_regs_vec[i].append(m.Reg('sub_k%d_d%d_st0' %
                                             (i, j), input_data_width))
        # st1 - sqr
        m.EmbeddedCode('\n//pipeline stage 1 - Sqr')
        st1_regs_vec = []
        for i in range(centroids_qty_v):
            st1_regs_vec.append([])
            for j in range(dimensions_qty_v):
                st1_regs_vec[i].append(m.Reg('sqr_k%d_d%d_st1' %
                                             (i, j), input_data_width*2))

        # st - add reduction
        st_idx = 2
        add_dict = self.add_dict
        add_ltcy = self.add_ltcy
        add_plus_bits = ceil(log2(add_ltcy)) + 1
        st_add_vec = []
        m.EmbeddedCode('\n//pipeline Add reduction - %d stages' % add_ltcy)
        m.EmbeddedCode(
            '//we needed to add %db to the add witdh because we need ceil(log2(reduction_stages)) + 1 to don´t have overflow' % add_plus_bits)
        for i in range(centroids_qty_v):
            add_idx = 0
            st_add_vec.append([])
            for k in add_dict.keys():
                st_add_vec[i].append(m.Reg('add%d_k%d_st%d' % (
                    add_idx, i, add_dict[k][0]+st_idx), input_data_width*2+add_plus_bits))
                add_idx += 1

        # st - comp reduction
        st_idx += add_dict[len(add_dict)-1][0]+1
        cmp_dict = self.cmp_dict
        cmp_ltcy = self.cmp_ltcy
        st_cmp_idx_vec = []

        m.EmbeddedCode(
            '\n//pipeline comp reduction - %d stages. Centroid idx propagation' % cmp_ltcy)
        cmp_idx = 0
        for k in cmp_dict.keys():
            st_cmp_idx_vec.append(m.Reg('cmp%d_idx_st%d' % (
                cmp_idx, cmp_dict[k][0]+st_idx), centroid_id_width_v))
            cmp_idx += 1

        st_cmp_data_vec = []
        m.EmbeddedCode(
            '\n//pipeline comp reduction - %d stages. Centroid add reduction propagation' % cmp_ltcy)
        m.EmbeddedCode(
            '//The last stage of these regs are only for depuration. When in synthesys they will be automatically removed')
        cmp_idx = 0
        for k in cmp_dict.keys():
            st_cmp_data_vec.append(m.Reg('cmp%d_data_st%d' % (
                cmp_idx, cmp_dict[k][0]+st_idx), input_data_width*2+add_plus_bits))
            cmp_idx += 1

        # output assigns
        m.EmbeddedCode('\n//Output assigns')
        selected_centroid.assign(st_cmp_idx_vec[-1])

        pipeline_always = m.Always(Posedge(clk))()
        # sub pipe
        for i in range(centroids_qty_v):
            for j in range(dimensions_qty_v):
                pipeline_always.statement += (st0_regs_vec[i][j]
                                              (centroids_vec[i][j]-input_data_vec[j]),)

        # sqr pipe
        for i in range(centroids_qty_v):
            for j in range(dimensions_qty_v):
                pipeline_always.statement += (st1_regs_vec[i][j](
                    st0_regs_vec[i][j]*st0_regs_vec[i][j]),)

        # add reduction pipe(s)
        for i in range(centroids_qty_v):
            add_idx = 0
            for k in add_dict.keys():
                if add_dict[k][0] == 0:
                    a = add_dict[k][1]
                    if len(add_dict[k]) > 2:
                        b = add_dict[k][2]
                        pipeline_always.statement += (st_add_vec[i][add_idx](
                            st1_regs_vec[i][a]+st1_regs_vec[i][b]),)
                    else:
                        pipeline_always.statement += (
                            st_add_vec[i][add_idx](st1_regs_vec[i][a]),)
                else:
                    a = add_dict[k][1]
                    if len(add_dict[k]) > 2:
                        b = add_dict[k][2]
                        pipeline_always.statement += (st_add_vec[i][add_idx](
                            st_add_vec[i][a]+st_add_vec[i][b]),)
                    else:
                        pipeline_always.statement += (
                            st_add_vec[i][add_idx](st_add_vec[i][a]),)
                add_idx += 1

        # comp tree pipe(s)
        cmp_idx = 0
        for k in cmp_dict.keys():
            if cmp_dict[k][0] == 0:
                a = cmp_dict[k][1]
                if len(cmp_dict[k]) > 2:
                    b = cmp_dict[k][2]
                    pipeline_always.statement += (
                        st_cmp_idx_vec[cmp_idx](
                            Mux(
                                st_add_vec[a][-1] < st_add_vec[b][-1],
                                Int(a, centroid_id_width_v, 10),
                                Int(b, centroid_id_width_v, 10)
                            )
                        ),
                        st_cmp_data_vec[cmp_idx](
                            Mux(
                                st_add_vec[a][-1] < st_add_vec[b][-1],
                                st_add_vec[a][-1],
                                st_add_vec[b][-1],
                            )
                        ),
                    )
                else:
                    pipeline_always.statement += (
                        st_cmp_idx_vec[cmp_idx](
                            Int(a, centroid_id_width_v, 10),
                        ),
                        st_cmp_data_vec[cmp_idx](
                            st_add_vec[a][-1],
                        ),
                    )
            else:
                a = cmp_dict[k][1]
                if len(cmp_dict[k]) > 2:
                    b = cmp_dict[k][2]
                    pipeline_always.statement += (
                        st_cmp_idx_vec[cmp_idx](
                            Mux(
                                st_cmp_data_vec[a] < st_cmp_data_vec[b],
                                st_cmp_idx_vec[a],
                                st_cmp_idx_vec[b]
                            )
                        ),
                        st_cmp_data_vec[cmp_idx](
                            Mux(
                                st_cmp_data_vec[a] < st_cmp_data_vec[b],
                                st_cmp_data_vec[a],
                                st_cmp_data_vec[b]
                            )
                        ),
                    )
                else:
                    pipeline_always.statement += (
                        st_cmp_idx_vec[cmp_idx](
                            st_cmp_idx_vec[a]
                        ),
                        st_cmp_data_vec[cmp_idx](
                            st_cmp_data_vec[a],
                        ),
                    )
            cmp_idx += 1

        # Input data propagation pipeline
        m.EmbeddedCode('\n//Input data propagation pipeline')
        data_prop_vec = []
        for i in range(pipe_latency_delay_v):
            data_prop_vec.append([])
            for d in range(dimensions_qty_v):
                data_prop_vec[i].append(
                    m.Reg('data_prop_d%d_st%d' % (d, i), input_data_width))

        # output assigns
        m.EmbeddedCode('\n//Output assigns')
        for d in range(dimensions_qty_v):
            output_data_vec[d].assign(data_prop_vec[-1][d])

        data_always = m.Always(Posedge(clk))()
        # Input data propagation pipeline
        for i in range(pipe_latency_delay_v):
            for d in range(dimensions_qty_v):
                if i == 0:
                    data_always.statement += (
                        data_prop_vec[i][d](input_data_vec[d]),)
                else:
                    pass
                    data_always.statement += (
                        data_prop_vec[i][d](data_prop_vec[i-1][d]),)

        _u.initialize_regs(m)
        return m

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

    def create_kmeans_top(self):
        name = 'kmeans_k2n2_top'
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)

        mem_d0_init_file = m.Parameter('mem_d0_init_file', './db/d0.txt')
        mem_d1_init_file = m.Parameter('mem_d1_init_file', './db/d1.txt')
        data_width = m.Parameter('data_width', 8)
        n_input_data_b_depth = m.Parameter('n_input_data_b_depth', 8)
        n_input_data = m.Parameter('n_input_data', 256)
        acc_sum_width = m.Parameter('acc_sum_width', 8 + ceil(log2(256)))
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
        up_centroids = m.Reg('up_centroids')

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
            ('wr', mem_sum_d0_init_wr),
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
            ('wr', mem_sum_d1_init_wr),
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
            ('wr', mem_sum_d0_wr),
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
            ('wr', mem_sum_d1_wr),
            ('wr_addr', mem_sum_d1_wr_addr),
            ('wr_data', mem_sum_d1_wr_data),
        ]
        m.Instance(aux, '%s_sum_d1' % aux.name, par, con)

        m.EmbeddedCode('\n//Modules instantiation - end')

        _u.initialize_regs(m)
        self.cache[name] = m
        return m

    def create_kmeans_testbench(self) -> str:
        name = "testbench_kmeans_k2s2"
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)

        clk = m.Reg('clk')
        rst = m.Reg('rst')
        start = m.Reg('start')

        # kmeans top
        par = [
            ('mem_d0_init_file', './db/d0.txt'),
            ('mem_d1_init_file', './db/d1.txt'),
            ('data_width', 8),
            ('n_input_data_b_depth', 8),
            ('n_input_data', 256),
            ('acc_sum_width', 8 + ceil(log2(256))),
            ('p_k0_0', 0),
            ('p_k0_1', 0),
            ('p_k1_0', 1),
            ('p_k1_1', 1),
        ]
        con = [
            ('clk', clk),
            ('rst', rst),
            ('start', start)
        ]
        aux = self.create_kmeans_top()
        m.Instance(aux, aux.name, par, con)

        _u.initialize_regs(m, {"clk": 0, "rst": 1, "start": 0})
        simulation.setup_waveform(m)
        m.Initial(
            EmbeddedCode("@(posedge clk);"),
            EmbeddedCode("@(posedge clk);"),
            EmbeddedCode("@(posedge clk);"),
            rst(0),
            start(1),
            Delay(400),
            Finish(),
        )
        m.EmbeddedCode("always #5clk=~clk;")

        m.to_verilog(os.getcwd() + "/verilog/testbench_kmeans_k2s2.v")
        # sim = simulation.Simulator(m, sim="iverilog")
        # rslt = sim.run()
        # print(rslt)


# kmeans_pipeline.to_verilog('./verilog/pipeline.v')

for k in range(2, 4):
    for d in range(2, 6):
        km = KMeans(centroids_qty=k, dimensions_qty=d)
        kmeans_pipeline = km.create_kmeans_pipeline()
        kmeans_pipeline.to_verilog('./verilog/%s.v' % kmeans_pipeline.name)
