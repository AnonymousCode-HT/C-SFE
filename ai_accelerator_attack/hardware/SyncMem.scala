
package gemmini
import chisel3._
import chisel3.util._

import chisel3.experimental.{
  annotate,
  ChiselAnnotation
}

import firrtl.{
  AttributeAnnotation,
}

// Directly use the IP provided by Xilinx synthesis tools to optimize timing.
class xilinxSyncReadMem[T <: Data](n:Int, t: T, mask_len: Int) extends BlackBox(Map(
  "ADDR_WIDTH_A" -> (log2Ceil(n) max 1),
  "ADDR_WIDTH_B" -> (log2Ceil(n) max 1),
  "BYTE_WRITE_WIDTH_A" -> (t.getWidth / mask_len),
  "MEMORY_SIZE" -> (n*t.getWidth),
  "READ_DATA_WIDTH_B" -> t.getWidth,
  "MEMORY_PRIMITIVE" -> "auto",
  // The timing for the instance xxx.mem_reg_0 (implemented as a Block RAM) might be sub-optimal as no optional output register could be merged into the ram block. Providing additional output register may help in improving timing.
  "READ_LATENCY_B" -> 1,        //TODO: The output end has a delay of 2 cycles, optimizing the timing
  "WRITE_DATA_WIDTH_A" -> t.getWidth
)){
  override val desiredName = s"xpm_memory_sdpram"
  val io = IO(new Bundle {
    val dina = Input(UInt(t.getWidth.W))
    val addra = Input(UInt((log2Ceil(n) max 1).W))
    val ena = Input(Bool())
    val wea = Input(UInt(mask_len.W))
    val clka = Input(Clock())
    val addrb = Input(UInt((log2Ceil(n) max 1).W))
    val clkb = Input(Clock())
    val enb = Input(Bool())
    val doutb = Output(UInt(t.getWidth.W))
    val rstb = Input(UInt(1.W))
    val sleep = Input(UInt(1.W))
  })


  // io.sleep := 0.U
  //  io.rstb := 0.U
}

class SinglePortedSyncMemIO[T <: Data](n: Int, t: T) extends Bundle {
  val addr = Input(UInt((log2Ceil(n) max 1).W))
  val wdata = Input(t)
  val rdata = Output(t)
  val wen = Input(Bool())
  val ren = Input(Bool())

}

class SinglePortSyncMem[T <: Data](n: Int, t: T) extends Module {
  val io = IO(new SinglePortedSyncMemIO(n, t))

  assert(!(io.ren && io.wen), "undefined behavior in single-ported SRAM")

  val mem = SyncReadMem(n, t)

  when (io.wen) {
    mem.write(io.addr, io.wdata)
    io.rdata := DontCare
  }.otherwise {
    io.rdata := mem.read(io.addr, io.ren)
  }
}

class TwoPortSyncMem[T <: Data](n: Int, t: T, mask_len: Int) extends Module {
  val io = IO(new Bundle {
    val waddr = Input(UInt((log2Ceil(n) max 1).W))
    val raddr = Input(UInt((log2Ceil(n) max 1).W))
    val wdata = Input(t)
    val rdata = Output(t)
    val wen = Input(Bool())
    val ren = Input(Bool())
    val mask = Input(Vec(mask_len, Bool()))
  })

  assert(!(io.wen && io.ren && io.raddr === io.waddr), "undefined behavior in dual-ported SRAM")

  // val mem = SyncReadMem(n, t)
  val mask_elem = UInt((t.getWidth / mask_len).W)

  /*******************************************************USE XILINX BRAM IP**********************************/
  // Concatenate input data.
  val flatWriteData = io.wdata.asTypeOf(Vec(mask_len, mask_elem))
  val combWriteData = flatWriteData.reduce((a, b) => Cat(b, a))

  // Concatenate the mask.
  val maskTypeUInt = io.mask.asTypeOf(Vec(mask_len, UInt(1.W)))
  val combMask = maskTypeUInt.reduce((a, b) => Cat(b, a))

  val xilinxSyncMem = Module(new xilinxSyncReadMem(n, t, mask_len))
  xilinxSyncMem.io.dina := combWriteData
  xilinxSyncMem.io.addra := io.waddr
  xilinxSyncMem.io.ena := io.wen
  xilinxSyncMem.io.wea := combMask
  xilinxSyncMem.io.clka := clock

  xilinxSyncMem.io.addrb := io.raddr
  xilinxSyncMem.io.clkb := clock
  xilinxSyncMem.io.enb := io.ren
  io.rdata := xilinxSyncMem.io.doutb.asTypeOf(t)
  xilinxSyncMem.io.rstb := 0.U
  xilinxSyncMem.io.sleep := 0.U
  /*******************************************************USE XILINX BRAM IP**********************************/


//  val mem = SyncReadMem(n, Vec(mask_len, mask_elem))
//
//  io.rdata := mem.read(io.raddr, io.ren).asTypeOf(t)
//
//  when (io.wen) {
//    mem.write(io.waddr, io.wdata.asTypeOf(Vec(mask_len, mask_elem)), io.mask)
//  }
//
//  Seq(
//    new ChiselAnnotation {
//      override def toFirrtl = AttributeAnnotation(mem.toTarget, "rw_addr_collision = \"yes\"")
//    }
//  ).foreach(annotate(_))
}

class SplitSinglePortSyncMem[T <: Data](n: Int, t: T, splits: Int) extends Module {
  val io = IO(new Bundle {
    val waddr = Input(UInt((log2Ceil(n) max 1).W))
    val raddr = Input(UInt((log2Ceil(n) max 1).W))
    val wdata = Input(t)
    val rdata = Output(t)
    val wen = Input(Bool())
    val ren = Input(Bool())
  })

  val lens = n / splits
  val last_len = n - (splits-1)*lens

  def is_in_range(addr: UInt, i: Int) = {
    if (i == splits-1)
      addr >= (i*lens).U
    else
      addr >= (i*lens).U && addr < ((i+1)*lens).U
  }

  def split_addr(addr: UInt, i: Int) = {
    addr - (i*lens).U
  }

  val srams = Seq.fill(splits-1)(SinglePortSyncMem(lens, t).io) :+ SinglePortSyncMem(last_len, t).io

  val output_split = Reg(UInt((log2Ceil(splits) max 1).W))
  io.rdata := DontCare

  srams.zipWithIndex.foreach { case (sr, i) =>
    sr.addr := Mux(sr.ren, split_addr(io.raddr, i), split_addr(io.waddr, i))
    sr.wdata := io.wdata
    sr.ren := io.ren && is_in_range(io.raddr, i)
    sr.wen := io.wen && is_in_range(io.waddr, i)

    when (sr.ren) {
      output_split := i.U
    }

    // This is an awkward Chisel Vec error workaround
    when (output_split === i.U) {
      io.rdata := sr.rdata
    }
  }
}

object SinglePortSyncMem {
  def apply[T <: Data](n: Int, t: T): SinglePortSyncMem[T] = Module(new SinglePortSyncMem(n, t))
}

object TwoPortSyncMem {
  def apply[T <: Data](n: Int, t: T, mask_len: Int): TwoPortSyncMem[T] = Module(new TwoPortSyncMem(n, t, mask_len))
}

object SplitSinglePortSyncMem {
  def apply[T <: Data](n: Int, t: T, splits: Int): SplitSinglePortSyncMem[T] = Module(new SplitSinglePortSyncMem(n, t, splits))
}
