#!/bin/bash
set -euxo pipefail

rustup target add aarch64-linux-android

rm -rf build
mkdir -p build/model_lib

python prepare_model_lib.py

cd build
touch config.cmake
cmake .. \
      -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_TOOLCHAIN_FILE=${ANDROID_NDK}/build/cmake/android.toolchain.cmake \
      -DCMAKE_INSTALL_PREFIX=. \
      -DCMAKE_CXX_FLAGS="-O3" \
      -DANDROID_ABI=arm64-v8a \
      -DANDROID_NATIVE_API_LEVEL=android-24 \
      -DANDROID_PLATFORM=android-24 \
      -DCMAKE_FIND_ROOT_PATH_MODE_PACKAGE=ON \
      -DANDROID_STL=c++_static \
      -DUSE_HEXAGON_SDK=OFF \
      -DMLC_LLM_INSTALL_STATIC_LIB=ON \
      -DCMAKE_SKIP_INSTALL_ALL_DEPENDENCY=ON \
      -DUSE_OPENCL=ON

make tvm4j_runtime_packed -j8
cmake --build . --target install --config release -j

