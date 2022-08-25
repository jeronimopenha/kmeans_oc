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
            input_data_width: int = 8,
            input_data_qty: int = 256,
            dimensions_qty: int = 2,
            centroids_qty: int = 2
    ):
        self.input_data_width = input_data_width
        self.input_data_qty = input_data_qty
        self.input_data_qty_width = ceil(log2(self.input_data_qty))
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

    def create_ram_memory(self) -> Module:
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

    def create_kmeans_input_data_block(self):
        dimensions_qty_v = self.dimensions_qty
        input_data_width_v = self.input_data_width
        input_data_qty_width_v = self.input_data_qty_width

        name = 'kmeans_input_data_block_%ddim' % dimensions_qty_v
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)

        input_data_width = m.Parameter('input_data_width', input_data_width_v)
        memory_depth_bits = m.Parameter(
            'memory_depth_bits', input_data_qty_width_v)
        mem_init_file_par_vec = []
        for d in range(dimensions_qty_v):
            mem_init_file_par_vec.append(m.Parameter(
                'mem_d%d_init_file' % d, './db/d%d.txt' % d))

        clk = m.Input('clk')
        rd_address = m.Input('rd_address', memory_depth_bits)
        output_data = []
        for d in range(dimensions_qty_v):
            output_data.append(m.Output('output_data%d' %
                               d, input_data_width))

        aux = self.create_ram_memory()
        for d in range(dimensions_qty_v):
            par = [
                ('read_f', 1),
                ('init_file', mem_init_file_par_vec[d]),
                ('write_f', 0),
                ('output_file', 'mem_out_file.txt'),
                ('depth', memory_depth_bits),
                ('width', input_data_width),
            ]
            con = [
                ('clk', clk),
                ('rd_addr', rd_address),
                ('out', output_data[d]),
                ('wr', Int(0, 1, 10)),
                ('wr_addr', Int(0, input_data_qty_width_v, 10)),
                ('wr_data', Int(0, input_data_width_v, 10)),
            ]
            m.Instance(aux, '%s_%d' % (aux.name, d), par, con)

        _u.initialize_regs(m)
        self.cache[name] = m
        return m

    def create_kmeans_pipeline(self):
        input_data_width_v = self.input_data_width
        input_data_qty_v = self.input_data_qty
        dimensions_qty_v = self.dimensions_qty
        centroids_qty_v = self.centroids_qty
        centroid_id_width_v = self.centroid_id_width
        # 1 - sub, 1 - sqr, ceil(log2(dimensions_qty)) add, ceil(log2(centroids_qty)) comp
        pipe_latency_delay_v = 1+1 + \
            ceil(log2(dimensions_qty_v)) + ceil(log2(centroids_qty_v))
        pipe_latency_delay_width_v = ceil(log2(pipe_latency_delay_v))

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
        add_idx = 0
        for k in add_dict.keys():

            for i in range(centroids_qty_v):
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

    def create_kmeans_acc_block(self):
        input_data_width_v = self.input_data_width
        input_data_qty_v = self.input_data_qty
        input_data_qty_width_v = self.input_data_qty_width
        dimensions_qty_v = self.dimensions_qty
        centroids_qty_v = self.centroids_qty
        centroid_id_width_v = self.centroid_id_width

        name = 'kmeans_acc_block_k%dn%d' % (centroids_qty_v, dimensions_qty_v)
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)

        input_data_width = m.Parameter('input_data_width', input_data_width_v)
        input_data_qty_bit_width = m.Parameter(
            'input_data_qty_bit_width', input_data_qty_width_v)
        acc_width = m.Parameter(
            'acc_width', input_data_width_v + ceil(log2(input_data_qty_v)))

        clk = m.Input('clk')
        rst = m.Input('rst')
        acc_enable = m.Input('acc_enable')

        d_to_acc_vec = [] = []
        for d in range(dimensions_qty_v):
            d_to_acc_vec.append(
                m.Input('d%d_to_acc' % d, input_data_width))
        selected_centroid = m.Input('selected_centroid', centroid_id_width_v)

        rd_acc_en = m.Input('rd_acc_en')
        rd_acc_centroid = m.Input('rd_acc_centroid', centroid_id_width_v)
        centroid_output = m.OutputReg('centroid_output', centroid_id_width_v)
        acc_output_vec = []
        for d in range(dimensions_qty_v):
            acc_output_vec.append(
                m.Output('acc%d_output' % d, acc_width))
        acc_counter_output = m.Output('acc_counter_output', input_data_qty_bit_width)

        # counters for each centroid acc data
        m.EmbeddedCode('\n//counters for each centroid')
        centroid_counters = m.Reg(
            'centroid_counter', input_data_qty_bit_width, centroids_qty_v)
        #centroid_counter_vec = []
        # for d in range(centroids_qty_v):
        #    centroid_counter_vec.append(
        #        m.Reg('k%d_counter' % d, input_data_qty_bit_width))

        # Memories valid content register flag
        m.EmbeddedCode('\n//Memories valid content register flag')
        acc_valid_content_vec = []
        for d in range(dimensions_qty_v):
            acc_valid_content_vec.append(
                m.Reg('acc%d_valid_content' % d, centroids_qty_v))

        # Memories wires and regs
        m.EmbeddedCode('\n//Memories wires and regs')

        mem_acc_rd_addr = m.Wire('mem_acc_rd_addr', centroid_id_width_v)
        mem_acc_out_vec = []
        for d in range(dimensions_qty_v):
            mem_acc_out_vec.append(
                m.Wire('mem_acc_%d_out' % d, acc_width),)
        mem_acc_wr_vec = []
        for d in range(dimensions_qty_v):
            mem_acc_wr_vec.append(m.Wire('mem_acc_%d_wr' % d))
        mem_acc_wr_addr_vec = []
        for d in range(dimensions_qty_v):
            mem_acc_wr_addr_vec.append(
                m.Wire('mem_acc%d_wr_addr' % d, centroid_id_width_v))
        mem_acc_wr_data_vec = []
        for d in range(dimensions_qty_v):
            mem_acc_wr_data_vec.append(
                m.Wire('mem_acc%d_wr_data' % d, acc_width))

        # Assigns to control the read and write acc logic
        # First the read conditions:
        # If we are accumulating, so we read the memory, add the input content to the memory content
        # If we are reading the ACC, we need to have authority to read withot interference of the pipeline
        # selected centroid input

        m.EmbeddedCode('\n//Assigns to control the read and write acc logic')
        m.EmbeddedCode('//First the read conditions:')
        m.EmbeddedCode(
            '//If we are accumulating, we need to read the memory, add the input content to the memory content if it is valid')
        m.EmbeddedCode(
            '//If we are reading the ACC, we need to have authority to read with no interference from the pipeline`s')
        m.EmbeddedCode('//selected centroid input')
        mem_acc_rd_addr.assign(
            Mux(rd_acc_en, rd_acc_centroid, selected_centroid))

        # The write enable signal is controled by the input "acc_enable"
        m.EmbeddedCode(
            '\n//The write enable signal is controled by the input "acc_enable"')
        for d in range(dimensions_qty_v):
            mem_acc_wr_vec[d].assign(acc_enable)

        # The write address is the number of selected centroid given by the "selected_centroid" input signal
        m.EmbeddedCode(
            '\n//The write address is the number of selected centroid given by the "selected_centroid" input signal')
        for d in range(dimensions_qty_v):
            mem_acc_wr_addr_vec[d].assign(selected_centroid)

        # Next the write data is the sum of the memory content + input data for each memory if the memory is initialized.
        m.EmbeddedCode(
            '\n//Next the write data is the sum of the memory content + input data for each memory if the memory is initialized.')
        for d in range(dimensions_qty_v):
            mem_acc_wr_data_vec[d].assign(
                Mux(acc_valid_content_vec[d][selected_centroid], d_to_acc_vec[d] + mem_acc_out_vec[d], d_to_acc_vec[d]))

        # Output data assigns
        m.EmbeddedCode('\n//Output data assigns')
        for d in range(dimensions_qty_v):
            acc_output_vec[d].assign(mem_acc_out_vec[d])

        # Resetting the ACC contents and updating it`s bits when a data is written in memory
        m.EmbeddedCode(
            '\n//Resetting the ACC contents and updating it`s bits when a data is written in memory')
        content_always = m.Always(Posedge(clk))
        content_rst_if = If(rst)().Elif(acc_enable)()
        for d in range(dimensions_qty_v):
            content_rst_if.true_statement += (acc_valid_content_vec[d](0),)
            content_rst_if.next_call.true_statement += (
                acc_valid_content_vec[d][selected_centroid](1),)
        content_always.set_statement(content_rst_if)

        # Output counter assigns
        m.EmbeddedCode('\n//Output counter assigns')
        acc_counter_output.assign(centroid_counters[rd_acc_centroid])
        
        # Resetting the centroids counters and updating them when a data is written in a centroid line
        m.EmbeddedCode(
            '\n//Resetting the centroids counters and updating them when a data is written in a centroid line')
        counter_always = m.Always(Posedge(clk))
        counter_rst_if = If(rst)().Elif(acc_enable)()

        for k in range(centroids_qty_v):
            counter_rst_if.true_statement += (centroid_counters[k](0),)
        counter_rst_if.next_call.true_statement += centroid_counters[selected_centroid](
            centroid_counters[selected_centroid] + 1),

        counter_always.set_statement(counter_rst_if)

        # ACC memories
        # we have one memory for wach dimension and the lines are the centrods acc
        m.EmbeddedCode('\n//ACC memories')
        m.EmbeddedCode(
            '//we have one memory for wach dimension and the lines are the centrods acc')
        for d in range(dimensions_qty_v):
            aux = self.create_ram_memory()
            par = [
                ('read_f', 0),
                ('write_f', 0),
                ('depth', centroid_id_width_v),
                ('width', acc_width),
            ]
            con = [
                ('clk', clk),
                ('rd_addr', mem_acc_rd_addr),
                ('out', mem_acc_out_vec[d]),
                ('wr', mem_acc_wr_vec[d]),
                ('wr_addr', mem_acc_wr_addr_vec[d]),
                ('wr_data', mem_acc_wr_data_vec[d]),
            ]
            m.Instance(aux, '%s_d%d' % (aux.name, d), par, con)

        _u.initialize_regs(m)
        self.cache[name] = m
        return m

    def create_kmeans_top(self):
        input_data_width_v = self.input_data_width
        input_data_qty_v = self.input_data_qty
        input_data_qty_width_v = self.input_data_qty_width
        dimensions_qty_v = self.dimensions_qty
        centroids_qty_v = self.centroids_qty
        centroid_id_width_v = self.centroid_id_width
        # latency 1 - sub, 1 - sqr, ceil(log2(dimensions_qty)) add, ceil(log2(centroids_qty)) comp
        pipe_latency_delay_v = 1+1 + \
            ceil(log2(dimensions_qty_v)) + ceil(log2(centroids_qty_v))
        pipe_latency_delay_width_v = ceil(log2(pipe_latency_delay_v))

        name = 'kmeans_k%dn%d_top' % (centroids_qty_v, dimensions_qty_v)
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)

        # parameters for data input for each dimensions
        input_data_width = m.Parameter('input_data_width', input_data_qty_v)
        input_data_qty = m.Parameter('input_data_qty', input_data_qty_v)
        input_data_qty_bit_width = m.Parameter(
            'input_data_qty_bit_width', input_data_qty_width_v)
        acc_width = m.Parameter(
            'acc_width', input_data_width_v + ceil(log2(input_data_qty_v)))
        mem_init_file_par_vec = []
        for d in range(dimensions_qty_v):
            mem_init_file_par_vec.append(m.Parameter(
                'mem_d%d_init_file' % d, './db/d%d.txt' % d))
        k_init_vec = []
        for k in range(centroids_qty_v):
            for d in range(dimensions_qty_v):
                k_init_vec.append(m.Parameter('k%d_d%d_initial' % (k, d), k))

        clk = m.Input('clk')
        rst = m.Input('rst')
        start = m.Input('start')

        # Centroids registers
        m.EmbeddedCode('\n//Centroids unique regs')
        centroids_vec = []
        for k in range(centroids_qty_v):
            centroids_vec.append([])
            for d in range(dimensions_qty_v):
                centroids_vec[k].append(
                    m.Reg('k%dd%d' % (k, d), input_data_width))

        # New centroids registers
        m.EmbeddedCode('\n//New centroids vector regs')
        new_centroids_reg_vec = []
        for k in range(centroids_qty_v):
            new_centroids_reg_vec.append(
                m.Reg('new_centroid_k%d' % k, input_data_width, dimensions_qty_v))

        m.EmbeddedCode('\n//New centroids unique buses')
        new_centroids_unique_vec = []
        for k in range(centroids_qty_v):
            new_centroids_unique_vec.append([])
            for d in range(dimensions_qty_v):
                new_centroids_unique_vec[k].append(
                    m.Wire('new_k%dd%d' % (k, d), input_data_width))

        m.EmbeddedCode(
            '\n//Assigning each new centroid buses to it`s respective reg')
        for k in range(centroids_qty_v):
            for d in range(dimensions_qty_v):
                new_centroids_unique_vec[k][d].assign(
                    new_centroids_reg_vec[k][d])

        # Input data memories
        m.EmbeddedCode('\n//Input data block')
        m.EmbeddedCode(
            '//In this block we have N RAM memories. Each one contains data for one input dimension')

        input_ram_rd_address = m.Wire(
            'input_ram_rd_address', input_data_qty_bit_width)
        data_vec = []
        for d in range(dimensions_qty_v):
            data_vec.append(m.Wire('d%d' % d, input_data_width))

        aux = self.create_kmeans_input_data_block()
        par = [
            ('input_data_width', input_data_width),
            ('memory_depth_bits', input_data_qty_bit_width)
        ]
        for d in range(dimensions_qty_v):
            par.append(('mem_d%d_init_file' % d, mem_init_file_par_vec[d]),)

        con = [
            ('clk', clk),
            ('rd_address', input_ram_rd_address)
        ]
        for d in range(dimensions_qty_v):
            con.append(('output_data%d' % d, data_vec[d]),)

        m.Instance(aux, aux.name, par, con)

        # Kmeans main pipeline
        m.EmbeddedCode('\n//kmeans main pipeline')

        d_to_acc_vec = []
        for d in range(dimensions_qty_v):
            d_to_acc_vec.append(m.Wire('d%d_to_acc' % d, input_data_width))

        selected_centroid = m.Wire('selected_centroid', centroid_id_width_v)

        aux = self.create_kmeans_pipeline()
        par = []
        con = [
            ('clk', clk)
        ]
        for k in range(centroids_qty_v):
            for d in range(dimensions_qty_v):
                con.append(('centroid%d_d%d' %
                           (k, d), centroids_vec[k][d]),)
        for d in range(dimensions_qty_v):
            con.append(('input_data%d' % d, data_vec[d]),)
        for d in range(dimensions_qty_v):
            con.append(('output_data%d' % d, d_to_acc_vec[d]),)
        con.append(('selected_centroid', selected_centroid),)
        m.Instance(aux, aux.name, par, con)

        # Kmeans acc block
        m.EmbeddedCode('\n//kmeans acc clock')

        aux = self.create_kmeans_acc_block()
        par = []
        con = []
        m.Instance(aux, aux.name, par, con)

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

for k in range(2, 6):
    for d in range(2, 4):
        km = KMeans(centroids_qty=k, dimensions_qty=d)
        kmeans_top = km.create_kmeans_top()
        kmeans_top.to_verilog('./verilog/%s.v' % kmeans_top.name)
        # print(km.create_kmeans_input_data_block().to_verilog())
        # kmeans_pipeline = km.create_kmeans_pipeline()
        # kmeans_pipeline.to_verilog('./verilog/%s.v' % kmeans_pipeline.name)
