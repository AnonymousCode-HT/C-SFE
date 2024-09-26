# Hardware and Middleware malicious code

## Hardware

The ``hardware`` directory contains files related to the implementation of HT.
HT is tested under [vivado-risc-v](https://github.com/eugene-tarassov/vivado-risc-v.git). The attaker only needs to copy the four files from the `hardware` directory to `vivado-risc-v/generators/gemmini/src/main/scala/gemmini`, and then follow the normal compilation process.

## Middleware

The malicious code is tested under [onnxruntime-riscv](https://github.com/ucb-bar/onnxruntime-riscv). To embed it in onnxruntime-riscv, the attacker needs to replace the original `onnxruntime-riscv/onnxruntime/core/mlas/lib/systolic` with `middleware/mlas/lib/systolic`, replace the original `onnxruntime-riscv/onnxruntime/core/providers/systolic` directory with `middleware/providers/systolic`, and replace the original `cmake/CMakeLists.txt` with `middleware/CMakeLists.txt`, and then follow the normal compilation process.

**Note:** The version of [onnxruntime-riscv](https://github.com/ucb-bar/onnxruntime-riscv) is outdated, and it can only compile dynamic and static libraries running on Rocket Core (i.e., users can only use C/C++ programming). It cannot compile a Python wheel suitable for the RISC-V version. Therefore, we recommend using the latest version of [onnxruntime](https://github.com/microsoft/onnxruntime). However, porting the Gemmini driver code to the latest [onnxruntime](https://github.com/microsoft/onnxruntime) requires cumbersome steps, so we directly provide a precompiled Python wheel file (`onnxruntime_training-1.18.0+cpu-cp311-cp311-linux_riscv64.whl`), which can be installed directly on Rocket Core. We will provide a detailed tutorial on how to port the Gemmini software driver (including malicious code) to the latest [onnxruntime](https://github.com/microsoft/onnxruntime) in the near future.

**Note** : In the middleware, we only provide the embedding of the low-level malicious code and have disabled the top-level invocation process (i.e., `atk` is set to `NULL` in the top-level function). However, interested users can still set it to a valid value for testing purposes.
