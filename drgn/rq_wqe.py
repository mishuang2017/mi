#!/usr/local/bin/drgn -k
#
# Dump mlx5e RX queue WQE info: RQ params, linked-list ring state, and per-WQE
# descriptor (data seg addr/len/lkey), mpw_info (consumed strides) and pages.
#
# usage: rq_wqe.py <ifname> [channel] [-p] [-x] [-u] [-c]
#   no channel : one summary line per channel
#   channel    : full per-WQE dump of that channel's RQ
#   -p         : also print every page behind each WQE (netmem, frags, dma)
#   -x         : use the XSK RQ (c->xskrq) instead of c->rq
#   -u         : also decode the UMR WQEs still in the channel's ICOSQ ring
#   -c         : also dump the RQ's CQ (cc, doorbells, recent and next CQEs)
#
# live:   sudo drgn rq_wqe.py enp8s0f0 0
# vmcore: sudo drgn -c /var/crash/.../vmcore rq_wqe.py enp8s0f0 0

import sys

from drgn import Object, offsetof, sizeof
from drgn.helpers.linux import *

MLX5_WQ_TYPE_CYCLIC = 0x1
MLX5_WQ_TYPE_LINKED_LIST_STRIDING_RQ = 0x2
NET_IOV = 0x1

def be16(x): return int.from_bytes(x.value_().to_bytes(2, 'little'), 'big')
def be32(x): return int.from_bytes(x.value_().to_bytes(4, 'little'), 'big')
def be64(x): return int.from_bytes(x.value_().to_bytes(8, 'little'), 'big')

def sym(fp):
    try:
        return prog.symbol(fp.value_()).name
    except LookupError:
        return hex(fp.value_())

# mlx5_frag_buf_get_wqe()
def frag_buf_get_wqe(fbc, ix):
    ix += fbc.strides_offset.value_()
    frag = ix >> fbc.log_frag_strides.value_()
    off = (fbc.frag_sz_m1.value_() & ix) << fbc.log_stride.value_()
    return fbc.frags[frag].buf.value_() + off

# mlx5e_get_mpw_info(): struct_size(info, alloc_units.frag_pages, pages_per_wqe)
def get_mpw_info(rq, ix):
    isz = sizeof(prog.type('struct mlx5e_mpw_info')) + \
          rq.mpwqe.pages_per_wqe.value_() * sizeof(prog.type('struct mlx5e_frag_page'))
    return Object(prog, 'struct mlx5e_mpw_info',
                  address=rq.mpwqe.info.value_() + ix * isz)

# page_pool_get_dma_addr_netmem() on 64-bit: netmem_desc.dma_addr
def netmem_dma(netmem):
    nm = netmem.value_()
    if nm & NET_IOV:
        return None
    if not nm:
        return 0
    try:
        return Object(prog, 'struct netmem_desc', address=nm).dma_addr.value_()
    except LookupError:
        return Object(prog, 'struct page', address=nm).dma_addr.value_()

def rq_state_str(rq):
    names = []
    st = rq.state.value_()
    for name in ('MLX5E_RQ_STATE_ENABLED', 'MLX5E_RQ_STATE_RECOVERING',
                 'MLX5E_RQ_STATE_DIM', 'MLX5E_RQ_STATE_NO_CSUM_COMPLETE',
                 'MLX5E_RQ_STATE_CSUM_FULL', 'MLX5E_RQ_STATE_MINI_CQE_HW_STRIDX',
                 'MLX5E_RQ_STATE_SHAMPO', 'MLX5E_RQ_STATE_MINI_CQE_ENHANCED',
                 'MLX5E_RQ_STATE_XSK', 'MLX5E_RQ_STATE_DATA_DIRECT'):
        try:
            bit = prog[name].value_()
        except KeyError:
            continue
        if st & (1 << bit):
            names.append(name[len('MLX5E_RQ_STATE_'):])
    return "%#x(%s)" % (st, "|".join(names))

def get_rq(priv, ch, xsk):
    c = priv.channels.c[ch]
    return c.xskrq if xsk else c.rq

def print_summary(priv, xsk):
    num = priv.channels.num.value_()
    print("channels: %d" % num)
    for i in range(num):
        rq = get_rq(priv, i, xsk)
        if rq.wq_type.value_() == MLX5_WQ_TYPE_LINKED_LIST_STRIDING_RQ:
            wq = rq.mpwqe.wq
            sz_m1 = wq.fbc.sz_m1.value_()
            print("ch %-3d rqn %#-7x mpwqe wq_sz %-5d cur_sz %-5d missing %-5d "
                  "head %-5d actual_head %-5d umr_in_progress %-3d umr_completed %-3d "
                  "wqe_ctr %-5d db %d" %
                  (i, rq.rqn.value_(), sz_m1 + 1, wq.cur_sz.value_(),
                   sz_m1 - wq.cur_sz.value_(), wq.head.value_(),
                   rq.mpwqe.actual_wq_head.value_(),
                   rq.mpwqe.umr_in_progress.value_(), rq.mpwqe.umr_completed.value_(),
                   wq.wqe_ctr.value_(), be32(wq.db[0])))
        else:
            wq = rq.wqe.wq
            print("ch %-3d rqn %#-7x cyclic wq_sz %-5d cur_sz %-5d wqe_ctr %-5d db %d" %
                  (i, rq.rqn.value_(), wq.sz.value_(), wq.cur_sz.value_(),
                   wq.wqe_ctr.value_(), be32(wq.db[0])))

def print_rq_header(rq):
    print("rq %#x  rqn %#x  ix %d  wq_type %d  state %s" %
          (rq.address_of_().value_(), rq.rqn.value_(), rq.ix.value_(),
           rq.wq_type.value_(), rq_state_str(rq)))
    print("  hw_mtu %d  headroom %d  page_pool %#x  mkey_be %#x" %
          (rq.hw_mtu.value_(), rq.buff.headroom.value_(),
           rq.page_pool.value_(), be32(rq.mkey_be)))
    print("  handle_rx_cqe %s  post_wqes %s" %
          (sym(rq.handle_rx_cqe), sym(rq.post_wqes)))

def walk_mpwqe(rq, show_pages):
    m = rq.mpwqe
    wq = m.wq
    fbc = wq.fbc
    sz = fbc.sz_m1.value_() + 1
    num_strides = m.num_strides.value_()
    stride_sz = 1 << m.log_stride_sz.value_()
    ppw = m.pages_per_wqe.value_()
    cur_sz = wq.cur_sz.value_()
    missing = sz - 1 - cur_sz
    umr_ip = m.umr_in_progress.value_()

    print("  skb_from_cqe_mpwrq %s" % sym(m.skb_from_cqe_mpwrq))
    print("  num_strides %d  stride_sz %d (log %d)  wqe buf %d bytes" %
          (num_strides, stride_sz, m.log_stride_sz.value_(), num_strides * stride_sz))
    print("  pages_per_wqe %d  page_shift %d  mtts_per_wqe %d  umr_mode %d  "
          "umr_entry_size %d  umr_wqebbs %d" %
          (ppw, m.page_shift.value_(), m.mtts_per_wqe.value_(), m.umr_mode.value_(),
           m.umr_entry_size.value_(), m.umr_wqebbs.value_()))
    print("  umr_mkey %#x  min_wqe_bulk %d" % (be32(m.umr_mkey_be), m.min_wqe_bulk.value_()))
    print("wq: size %d  cur_sz %d (HW-owned)  missing %d  head %d  actual_wq_head %d  "
          "wqe_ctr %d  db_record %d" %
          (sz, cur_sz, missing, wq.head.value_(), m.actual_wq_head.value_(),
           wq.wqe_ctr.value_(), be32(wq.db[0])))
    print("    umr_in_progress %d  umr_completed %d  umr_last_bulk %d" %
          (umr_ip, m.umr_completed.value_(), m.umr_last_bulk.value_()))

    # Ring order: wq.head is the next WQE to be posted (mlx5_wq_ll_push sets
    # head = next(head)). Following next_wqe_index from head:
    #   UMR  - allocated, UMR WQE in flight (umr_in_progress), not posted yet
    #   FREE - popped, waiting for mlx5e_post_rx_mpwqes() to refill
    #   TAIL - last popped WQE (wq->tail_next points at its next field); kept
    #          back as the list end, that's why capacity is sz_m1
    #   HW   - posted, owned by the NIC (cur_sz of them), oldest first
    # The tail's next field is stale but still points at the oldest HW WQE,
    # since WQEs are popped in list order.
    tail_next = wq.tail_next.value_()
    order = []
    seen = set()
    ix = wq.head.value_()
    for _ in range(sz):
        if ix in seen:
            break
        seen.add(ix)
        order.append(ix)
        wqe = Object(prog, 'struct mlx5e_rx_wqe_ll', address=frag_buf_get_wqe(fbc, ix))
        ix = be16(wqe.next.next_wqe_index)

    print()
    print("%-5s %-4s %-8s %-6s %-9s %-18s %-10s %-10s %s" %
          ("pos", "ix", "state", "next", "consumed", "addr", "byte_cnt", "lkey", "wqe"))
    for pos, ix in enumerate(order):
        waddr = frag_buf_get_wqe(fbc, ix)
        wqe = Object(prog, 'struct mlx5e_rx_wqe_ll', address=waddr)
        is_tail = wqe.next.next_wqe_index.address_of_().value_() == tail_next
        if pos < umr_ip:
            state = "UMR"
        elif pos < missing:
            state = "FREE"
        elif pos == missing:
            state = "TAIL"
        else:
            state = "HW"
        ds = wqe.data[0]
        wi = get_mpw_info(rq, ix)
        consumed = wi.consumed_strides.value_()
        mark = ""
        if state == "HW" and 0 < consumed < num_strides:
            mark = "  <- NIC filling"
        if is_tail != (state == "TAIL"):
            mark += "  !! tail_next mismatch (tail_next=%#x)" % tail_next
        print("%-5d %-4d %-8s %-6d %4d/%-4d %#-18x %-10d %#-10x %#x%s" %
              (pos, ix, state, be16(wqe.next.next_wqe_index), consumed, num_strides,
               be64(ds.addr), be32(ds.byte_count), be32(ds.lkey), waddr, mark))
        if show_pages:
            print_mpw_pages(rq, wi, ppw)

def print_mpw_pages(rq, wi, ppw):
    bitmap = wi.skip_release_bitmap
    bits_per_long = sizeof(bitmap[0]) * 8
    xsk = rq.xsk_pool.value_() != 0
    for i in range(ppw):
        skip = (bitmap[i // bits_per_long].value_() >> (i % bits_per_long)) & 1
        if xsk:
            print("        [%2d] xdp_buff %#x  skip_release %d" %
                  (i, wi.alloc_units.xsk_buffs[i].value_(), skip))
            continue
        fp = wi.alloc_units.frag_pages[i]
        dma = netmem_dma(fp.netmem)
        dma_s = "net_iov" if dma is None else "%#x" % dma
        print("        [%2d] netmem %#x  frags %-5d dma %s  skip_release %d" %
              (i, fp.netmem.value_(), fp.frags.value_(), dma_s, skip))

MLX5_OPCODE_NOP = 0x00
MLX5_OPCODE_UMR = 0x25
MLX5_OCTWORD = 16

def icosq_wqe(sq, ctr):
    wq = sq.wq
    pi = ctr & (wq.sz.value_() - 1)
    return pi, Object(prog, 'struct mlx5e_umr_wqe', address=frag_buf_get_wqe(wq.fbc, pi))

# A WQE starts at ring counter ctr if its ctrl seg carries that counter
# (opmod_idx_opcode = pc << 8 | opcode, see mlx5e_post_nop/mlx5e_alloc_rx_mpwqe).
def icosq_wqe_starts_at(sq, ctr):
    pi, w = icosq_wqe(sq, ctr)
    return (be32(w.hdr.ctrl.opmod_idx_opcode) >> 8) & 0xffff == ctr & 0xffff

# Ring slots before cc keep the WQEs already completed. Find the oldest
# counter from which the chain of WQEs (stepping num_wqebbs) lands exactly on pc.
def icosq_find_start(sq):
    sz = sq.wq.sz.value_()
    cc = sq.cc.value_()
    pc = sq.pc.value_()
    for start in range(pc - sz, cc + 1):
        ctr = start
        ok = True
        while ctr < pc:
            if not icosq_wqe_starts_at(sq, ctr):
                ok = False
                break
            n = sq.db.wqe_info[ctr & (sz - 1)].num_wqebbs.value_()
            if n == 0:
                ok = False
                break
            ctr += n
        if ok and ctr == pc:
            return start
    return cc

def icosq_type_name(t):
    try:
        return prog.type('enum mlx5e_icosq_wqe_type').enumerators[t].name[len('MLX5E_ICOSQ_WQE_'):]
    except (LookupError, IndexError):
        return str(t)

def walk_icosq_umr(rq, nentries=4):
    sq = rq.icosq
    wq = sq.wq
    m = rq.mpwqe
    cc = sq.cc.value_()
    pc = sq.pc.value_()
    ppw = m.pages_per_wqe.value_()
    entry_sz = m.umr_entry_size.value_()
    per_wqe_oct = m.mtts_per_wqe.value_() * entry_sz // MLX5_OCTWORD
    data_direct = 'DATA_DIRECT' in rq_state_str(rq)

    print()
    print("icosq %#x  sqn %#x  size %d wqebbs  cc %d  pc %d  in-flight %d wqebbs" %
          (sq.address_of_().value_(), sq.sqn.value_(), wq.sz.value_(), cc, pc, pc - cc))
    print("%-7s %-5s %-8s %-6s %-5s %-6s %-7s %-7s %-6s %s" %
          ("ctr", "pi", "type", "state", "bbs", "mkey", "xlt_off", "xlt_oct", "rq_ix",
           "first entries (dma)"))

    ctr = icosq_find_start(sq)
    while ctr < pc:
        pi, w = icosq_wqe(sq, ctr)
        wi = sq.db.wqe_info[pi]
        t = wi.wqe_type.value_()
        n = wi.num_wqebbs.value_()
        state = "INFL" if ctr >= cc else "done"
        opcode = be32(w.hdr.ctrl.opmod_idx_opcode) & 0xff
        if opcode != MLX5_OPCODE_UMR or wi.umr.rq.value_() != rq.address_of_().value_():
            print("%-7d %-5d %-8s %-6s %-5d" % (ctr, pi, icosq_type_name(t), state, n))
            ctr += max(n, 1)
            continue

        xlt_off = be16(w.hdr.uctrl.xlt_offset)
        xlt_oct = be16(w.hdr.uctrl.xlt_octowords)
        rq_ix = xlt_off // per_wqe_oct
        ents = []
        for i in range(min(nentries, ppw)):
            if data_direct:
                ents.append("%#x" % be64(w.inline_ksms[i].va))
            else:
                ents.append("%#x" % (be64(w.inline_mtts[i].ptag) & ~0x3))

        # Compare with the pages the driver currently holds for that RQ WQE:
        # equal means this is the latest UMR that mapped it.
        cur = get_mpw_info(rq, rq_ix)
        match = all(netmem_dma(cur.alloc_units.frag_pages[i].netmem) ==
                    (be64(w.inline_mtts[i].ptag) & ~0x3)
                    for i in range(min(nentries, ppw))) if not data_direct else False
        print("%-7d %-5d %-8s %-6s %-5d %#-6x %-7d %-7d %-6d %s ...%s" %
              (ctr, pi, icosq_type_name(t), state, n,
               be32(w.hdr.ctrl.umr_mkey), xlt_off, xlt_oct, rq_ix, " ".join(ents),
               "  == current pages" if match else ""))
        ctr += n

MLX5_COMPRESSED = 3
MLX5_CQ_DB_REQ_NOT_SOL = 1 << 24

CQE_OPCODES = {0: 'REQ', 1: 'RESP_WR_IMM', 2: 'RESP_SEND', 3: 'RESP_SEND_IMM',
               4: 'RESP_SEND_INV', 5: 'RESIZE_CQ', 12: 'SIG_ERR',
               13: 'REQ_ERR', 14: 'RESP_ERR', 15: 'INVALID'}

def rq_state_test(rq, name):
    try:
        return bool(rq.state.value_() & (1 << prog[name].value_()))
    except KeyError:
        return False

# mlx5_cqwq_get_cqe() / mlx5_cqwq_get_cqe_enhanced_comp(): is the CQE at
# counter ctr already written by HW for the lap ctr belongs to?
def cqe_valid(cqe, ctr, log_sz, enhanced):
    if enhanced:
        return cqe.validity_iteration_count.value_() == (ctr >> log_sz) & 0xff
    return cqe.op_own.value_() & 1 == (ctr >> log_sz) & 1

def cqe_row(rq, wq, ctr, cc, enhanced, striding):
    log_sz = wq.fbc.log_sz.value_()
    sz_m1 = wq.fbc.sz_m1.value_()
    ci = ctr & sz_m1
    addr = frag_buf_get_wqe(wq.fbc, ci)
    # mlx5_cqwq_get_wqe(): for 128B CQEs the data is in the last 64B
    if wq.fbc.log_stride.value_() == 7:
        addr += 64
    cqe = Object(prog, 'struct mlx5_cqe64', address=addr)
    op_own = cqe.op_own.value_()
    opcode = op_own >> 4
    fmt = (op_own >> 2) & 3
    valid = cqe_valid(cqe, ctr, log_sz, enhanced)
    bc = be32(cqe.byte_cnt)

    if fmt == MLX5_COMPRESSED:
        # title CQE: mini CQE array follows in the next slots
        what = "COMPRESSED title  wqe_id %d  n_mini %d" % \
               (be16(cqe.wqe_id), opcode + 1 if enhanced else be32(cqe.byte_cnt))
    elif opcode == 0 and op_own >> 1 == 0:
        # mlx5e_cqes_update_owner() rewrote op_own of slots that held
        # mini CQE arrays; an RX CQ never gets a real REQ CQE
        what = "(mini CQE array slot, owner fixed up by driver)"
    elif striding:
        # mpwrq_get_cqe_*(): byte_cnt = filler:1 | consumed_strides:15 | bytes:16
        what = "%-9s wqe_id %-4d stride %-4d cstrides %-4d bytes %-5d%s" % \
               (CQE_OPCODES.get(opcode, opcode), be16(cqe.wqe_id),
                be16(cqe.wqe_counter), (bc >> 16) & 0x7fff, bc & 0xffff,
                "  FILLER" if bc >> 31 else "")
    else:
        what = "%-9s wqe_counter %-5d bytes %-5d" % \
               (CQE_OPCODES.get(opcode, opcode), be16(cqe.wqe_counter), bc)
    if opcode in (13, 14):
        # struct mlx5_err_cqe: syndrome at byte 55, vendor_err_synd at 54
        b = prog.read(addr + 54, 2)
        what += "  vendor_synd %#x synd %#x" % (b[0], b[1])
    # done: already polled; READY: written by HW, not polled yet;
    # stale: still holds the CQE from the previous lap
    if not valid:
        state = "stale"
    else:
        state = "done" if ctr < cc else "READY"
    return "%-8d %-5d %-3d %-6s %#06x  %s" % (ctr, ci, op_own & 1, state, op_own, what)

def walk_cq(rq, nback=8, nfwd=4):
    cq = rq.cq
    wq = cq.wq
    log_sz = wq.fbc.log_sz.value_()
    sz = 1 << log_sz
    cc = wq.cc.value_()
    enhanced = rq_state_test(rq, 'MLX5E_RQ_STATE_MINI_CQE_ENHANCED')
    striding = rq.wq_type.value_() == MLX5_WQ_TYPE_LINKED_LIST_STRIDING_RQ
    set_ci = be32(wq.db[0])
    arm = be32(wq.db[1])

    print()
    print("cq: cqn %#x  size %d  cqe_sz %d  cc %d  ci %d  lap %d  event_ctr %d  arm_sn %d" %
          (cq.mcq.cqn.value_(), sz, 1 << wq.fbc.log_stride.value_(), cc,
           cc & (sz - 1), cc >> log_sz, cq.event_ctr.value_(),
           cq.mcq.arm_sn.value_()))
    print("    db[0] set_ci %d%s" %
          (set_ci, "" if set_ci == cc & 0xffffff else
           "  (!= cc %d: CQEs popped but not yet published)" % (cc & 0xffffff)))
    print("    db[1] arm    %#x  (sn %d cmd %s ci %d)%s" %
          (arm, (arm >> 28) & 3,
           "REQ_NOT_SOL" if arm & MLX5_CQ_DB_REQ_NOT_SOL else "REQ_NOT",
           arm & 0xffffff,
           "  armed at current cc" if arm & 0xffffff == cc & 0xffffff else
           "  (cc moved since last arm: in NAPI or IRQ fired)"))
    cqd = rq.cqd
    if cqd.left.value_():
        print("    decompress in progress: left %d  mini_arr_idx %d" %
              (cqd.left.value_(), cqd.mini_arr_idx.value_()))
    print("    ownership check: %s" %
          ("validity_iteration_count == lap & 0xff" if enhanced else
           "op_own & 1 == lap & 1"))

    print()
    print("%-8s %-5s %-3s %-6s %-7s %s" % ("ctr", "ci", "own", "state", "op_own", "cqe"))
    for ctr in range(max(0, cc - nback), cc):
        print(cqe_row(rq, wq, ctr, cc, enhanced, striding))
    print("-------- cc %d: next CQE the driver will poll --------" % cc)
    for ctr in range(cc, cc + nfwd):
        print(cqe_row(rq, wq, ctr, cc, enhanced, striding))

def walk_cyclic(rq):
    wq = rq.wqe.wq
    fbc = wq.fbc
    sz = wq.sz.value_()
    nfrags = rq.wqe.info.num_frags.value_()
    log_nfrags = rq.wqe.info.log_num_frags.value_()
    print("  skb_from_cqe %s  num_frags %d" % (sym(rq.wqe.skb_from_cqe), nfrags))
    print("wq: size %d  cur_sz %d  wqe_ctr %d  db_record %d" %
          (sz, wq.cur_sz.value_(), wq.wqe_ctr.value_(), be32(wq.db[0])))
    print()
    for ix in range(sz):
        wqe = Object(prog, 'struct mlx5e_rx_wqe_cyc', address=frag_buf_get_wqe(fbc, ix))
        segs = []
        for f in range(1 << log_nfrags):
            ds = wqe.data[f]
            segs.append("%#x/%d/%#x" % (be64(ds.addr), be32(ds.byte_count), be32(ds.lkey)))
        print("%-5d %s" % (ix, "  ".join(segs)))

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('-')]
    show_pages = '-p' in sys.argv
    xsk = '-x' in sys.argv
    show_umr = '-u' in sys.argv
    show_cq = '-c' in sys.argv
    if not args:
        sys.exit("usage: rq_wqe.py <ifname> [channel] [-p] [-x] [-u] [-c]")

    dev = netdev_get_by_name(prog['init_net'], args[0])
    if not dev:
        sys.exit("netdev %s not found in init_net" % args[0])
    priv = netdev_priv(dev, 'struct mlx5e_priv')

    if len(args) < 2:
        print_summary(priv, xsk)
        return

    ch = int(args[1])
    if ch >= priv.channels.num.value_():
        sys.exit("channel %d out of range (num %d)" % (ch, priv.channels.num.value_()))
    rq = get_rq(priv, ch, xsk)
    print_rq_header(rq)
    if rq.wq_type.value_() == MLX5_WQ_TYPE_LINKED_LIST_STRIDING_RQ:
        walk_mpwqe(rq, show_pages)
        if show_umr:
            walk_icosq_umr(rq)
    else:
        walk_cyclic(rq)
    if show_cq:
        walk_cq(rq)

main()
