# About

NOTE: use `-s llvm_tools:build_type=Release` during `conan install`

conan package for llvm tools:

* include-what-you-use (only if `LLVM_USE_SANITIZER` disabled)
* clang-tidy
* scan-build
* ccc-analyzer
* c++-analyzer
* clang-format
* supports `LLVM_USE_SANITIZER`, see https://github.com/google/sanitizers/wiki/MemorySanitizerLibcxxHowTo#instrumented-gtest
* libc++ (will be instrumented if `LLVM_USE_SANITIZER` enabled)
* clang and clang++ as compilers
* etc.

See `test_package/CMakeLists.txt` for usage example

NOTE: use `find_program` with `${CONAN_BIN_DIRS}` or `${CONAN_BIN_DIRS_LLVM_TOOLS}` like below:

```cmake
list(APPEND CMAKE_PROGRAM_PATH ${CONAN_BIN_DIRS})
list(APPEND CMAKE_PROGRAM_PATH ${CONAN_BIN_DIRS_LLVM_TOOLS})

find_program(CLANG_TIDY clang-tidy
  PATHS
    ${CONAN_BIN_DIRS}
    ${CONAN_BIN_DIRS_LLVM_TOOLS}
  NO_SYSTEM_ENVIRONMENT_PATH
  NO_CMAKE_SYSTEM_PATH
)
if(NOT CLANG_TIDY)
  message(FATAL_ERROR "CLANG_TIDY not found")
endif()

find_program(SCAN_BUILD scan-build
  PATHS
    ${CONAN_BIN_DIRS}
    ${CONAN_BIN_DIRS_LLVM_TOOLS}
  NO_SYSTEM_ENVIRONMENT_PATH
  NO_CMAKE_SYSTEM_PATH
)
if(NOT SCAN_BUILD)
  message(FATAL_ERROR "scan-build not found")
endif()

find_program(CLANG_10 clang-10
  PATHS
    ${CONAN_BIN_DIRS}
    ${CONAN_BIN_DIRS_LLVM_TOOLS}
  NO_SYSTEM_ENVIRONMENT_PATH
  NO_CMAKE_SYSTEM_PATH
)
if(NOT CLANG_10)
  message(FATAL_ERROR "clang-10 not found")
endif()

find_program(CCC_ANALYZER ccc-analyzer
  PATHS
    ${CONAN_BIN_DIRS}
    ${CONAN_BIN_DIRS_LLVM_TOOLS}
  NO_SYSTEM_ENVIRONMENT_PATH
  NO_CMAKE_SYSTEM_PATH
)
if(NOT CCC_ANALYZER)
  message(FATAL_ERROR "ccc-analyzer not found")
endif()

find_program(CPP_ANALYZER c++-analyzer
  PATHS
    ${CONAN_BIN_DIRS}
    ${CONAN_BIN_DIRS_LLVM_TOOLS}
  NO_SYSTEM_ENVIRONMENT_PATH
  NO_CMAKE_SYSTEM_PATH
)
if(NOT CPP_ANALYZER)
  message(FATAL_ERROR "c++-analyzer not found")
endif()

find_program(CLANG_FORMAT clang-format
  PATHS
    ${CONAN_BIN_DIRS}
    ${CONAN_BIN_DIRS_LLVM_TOOLS}
  NO_SYSTEM_ENVIRONMENT_PATH
  NO_CMAKE_SYSTEM_PATH
)
if(NOT CLANG_FORMAT)
  message(FATAL_ERROR "clang-format not found")
endif()

find_program(IWYU include-what-you-use
  PATHS
    ${CONAN_BIN_DIRS}
    ${CONAN_BIN_DIRS_LLVM_TOOLS}
  NO_SYSTEM_ENVIRONMENT_PATH
  NO_CMAKE_SYSTEM_PATH
)
if(NOT IWYU)
  message(FATAL_ERROR "IWYU not found")
endif()
```

You can change compiler to clang from conan package like so:

```cmake
  # use llvm_tools from conan
  find_program(CLANG_PROGRAM clang
    PATHS
      #${CONAN_BIN_DIRS}
      ${CONAN_BIN_DIRS_LLVM_TOOLS}
    NO_SYSTEM_ENVIRONMENT_PATH
    NO_CMAKE_SYSTEM_PATH
  )

  set(CMAKE_C_COMPILER
    ${CLANG_PROGRAM}
    CACHE string
    "Clang C compiler" FORCE)

  # ...
  # use find_program for CMAKE_CXX_COMPILER, llvm-ar, etc.
  # ...

  set(CMAKE_CXX_COMPILER
    ${CLANGPP_PROGRAM}
    CACHE string
    "Clang C++ compiler" FORCE)

  # Set linkers and other build tools.
  # Related documentation
  # https://cmake.org/cmake/help/latest/variable/CMAKE_LANG_COMPILER.html
  # https://cmake.org/cmake/help/latest/variable/CMAKE_LANG_FLAGS_INIT.html
  # https://cmake.org/cmake/help/latest/variable/CMAKE_LINKER.html
  # https://cmake.org/cmake/help/latest/variable/CMAKE_AR.html
  # https://cmake.org/cmake/help/latest/variable/CMAKE_RANLIB.html
  set(CMAKE_AR      "${LLVM_AR_PROGRAM}")
  set(CMAKE_LINKER  "${LLVM_LD_PROGRAM}")
  set(CMAKE_NM      "${LLVM_NM_PROGRAM}")
  set(CMAKE_OBJDUMP "${LLVM_OBJDUMP_PROGRAM}")
  set(CMAKE_RANLIB  "${LLVM_RANLIB_PROGRAM}")
  set(CMAKE_ASM_COMPILER  "${LLVM_ASM_PROGRAM}")
  set(CMAKE_RC_COMPILER  "${LLVM_RC_PROGRAM}")
```

Add before `include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)`:

```cmake
  # do not check compile in conanbuildinfo
  # cause we will switch to other compiler after conan install
  set(CONAN_DISABLE_CHECK_COMPILER ON)
```

You can use `libc++` from conan package like so:

```cmake
  find_path(
    LIBCXX_LIBCXXABI_INCLUDE_FILE cxxabi.h
    PATHS
      ${CONAN_LLVM_TOOLS_ROOT}/include/c++/v1
      ${CONAN_INCLUDE_DIRS_LLVM_TOOLS}
    NO_DEFAULT_PATH
    NO_CMAKE_FIND_ROOT_PATH
  )

  get_filename_component(LIBCXX_LIBCXXABI_INCLUDE_FILE_DIR
    ${LIBCXX_LIBCXXABI_INCLUDE_FILE}
    DIRECTORY)

  find_library(CLANG_LIBCPP
    NAMES
      c++
    PATHS
      ${CONAN_LIB_DIRS_LLVM_TOOLS}
      ${CONAN_BIN_DIRS_LLVM_TOOLS}
    NO_SYSTEM_ENVIRONMENT_PATH
    NO_CMAKE_SYSTEM_PATH
  )

  get_filename_component(CLANG_LIBCPP_DIR
    ${CLANG_LIBCPP}
    DIRECTORY)

  find_library(CLANG_LIBCPPABI
    NAMES
    c++abi
    PATHS
      ${CONAN_LIB_DIRS_LLVM_TOOLS}
      ${CONAN_BIN_DIRS_LLVM_TOOLS}
    NO_SYSTEM_ENVIRONMENT_PATH
    NO_CMAKE_SYSTEM_PATH
  )

  get_filename_component(CLANG_LIBCPPABI_DIR
    ${CLANG_LIBCPPABI}
    DIRECTORY)

  include_directories(
    "${CONAN_LLVM_TOOLS_ROOT}/include"
    "${CONAN_LLVM_TOOLS_ROOT}/include/c++/v1")

  set(CMAKE_CXX_FLAGS
    "${CMAKE_CXX_FLAGS} \
    -I${CONAN_LLVM_TOOLS_ROOT}/include/c++/v1 \
    -I${CONAN_LLVM_TOOLS_ROOT}/include")

  link_directories("${CONAN_LLVM_TOOLS_ROOT}/lib")
  link_directories("${CLANG_LIBCPP_DIR}")

  set(CMAKE_CXX_FLAGS
    "${CMAKE_CXX_FLAGS} \
    -Wno-unused-command-line-argument \
    -L${CONAN_LLVM_TOOLS_ROOT}/lib \
    -L${CLANG_LIBCPP_DIR} \
    -Wl,-rpath,${CLANG_LIBCPPABI_DIR} \
    -Wl,-rpath,${CONAN_LLVM_TOOLS_ROOT}/lib \
    -stdlib=libc++ -lc++abi -lc++ -lm -lc -fuse-ld=lld")

  add_compile_options(
      "-stdlib=libc++"
      "-lc++abi"
      "-nostdinc++"
      "-nodefaultlibs"
      "-v")
```

## Supported platforms

Tested on Ubuntu 18, x86_64.

```bash
# lsb_release -a
Distributor ID: Ubuntu
Description:    Ubuntu 18.04.2 LTS
Release:        18.04
Codename:       bionic

# uname -a
Linux username 4.15.0-96-generic #97-Ubuntu SMP Wed Apr 1 03:25:46 UTC 2020 x86_64 x86_64 x86_64 GNU/Linux
```

## LICENSE

MIT for conan package. Packaged source uses own license, see https://releases.llvm.org/2.8/LICENSE.TXT and https://github.com/root-project/root/blob/master/LICENSE

## Usage example (CMake)

See [https://github.com/include-what-you-use/include-what-you-use/issues/802#issuecomment-661058223](https://github.com/include-what-you-use/include-what-you-use/issues/802#issuecomment-661058223)

## Before build

```bash
sudo apt-get update

sudo apt-get -y install autoconf automake bison build-essential \
ca-certificates llvm-dev libtool libtool-bin \
libglib2.0-dev make nasm wget

# Tested with clang 6.0 and gcc 7
sudo apt-get -y install clang-6.0 g++-7 gcc-7

# llvm-config binary that coresponds to the same clang you are using to compile
export LLVM_CONFIG=/usr/bin/llvm-config-6.0
$LLVM_CONFIG --cxxflags

sudo apt-get install libncurses5-dev libncursesw5-dev libtinfo-dev

# optionaL: swig4, libeidt-dev
```

read https://llvm.org/docs/CMake.html and https://fuchsia.dev/fuchsia-src/development/build/toolchain and https://github.com/deepinwiki/wiki/wiki/%E7%94%A8LLVM%E7%BC%96%E8%AF%91%E5%86%85%E6%A0%B8

## BUGFIX: 92247 (libsanitizer/sanitizer_common/sanitizer_linux compilation failed)

Bugfix for https://gcc.gnu.org/bugzilla/show_bug.cgi?id=92247

Fixes `asm/errno.h: No such file or directory` or `‘__NR_open’ was not declared in this scope`

```bash
sudo apt install linux-libc-dev

# NOTE: NOT /usr/include/asm-generic
sudo ln -s /usr/include/x86_64-linux-gnu/asm/ /usr/include/asm
```

## BUGFIX (i386 instead of x86_64)

Fixes `sanitizer_allocator.cpp.o' is incompatible with i386:x86-64 output`, see https://bugs.llvm.org/show_bug.cgi?id=42463 and section about i386 on https://reviews.llvm.org/D58184

```bash
# see https://superuser.com/a/714392
apt-get purge ".*:i386"
dpkg --remove-architecture i386

export CXXFLAGS=-m64
export CFLAGS=-m64
export LDFLAGS=-m64
```

Or you can remove `test_target_arch(i386 __i386__ "-m32")` from `compiler-rt/cmake/base-config-ix.cmake`

## Local build

```bash
export CC=gcc
export CXX=g++

# https://www.pclinuxos.com/forum/index.php?topic=129566.0
# export LDFLAGS="$LDFLAGS -ltinfo -lncurses"

# If compilation of LLVM fails on your machine (`make` may be killed by OS due to lack of RAM e.t.c.)
# - set env. var. CONAN_LLVM_SINGLE_THREAD_BUILD to 1.
export CONAN_LLVM_SINGLE_THREAD_BUILD=1

$CC --version
$CXX --version

conan remote add conan-center https://api.bintray.com/conan/conan/conan-center False

export PKG_NAME=llvm_tools/master@conan/stable

(CONAN_REVISIONS_ENABLED=1 \
    conan remove --force $PKG_NAME || true)

# see BUGFIX (i386 instead of x86_64)
export CXXFLAGS=-m64
export CFLAGS=-m64
export LDFLAGS=-m64

CONAN_REVISIONS_ENABLED=1 \
    CONAN_VERBOSE_TRACEBACK=1 \
    CONAN_PRINT_RUN_COMMANDS=1 \
    CONAN_LOGGING_LEVEL=10 \
    GIT_SSL_NO_VERIFY=true \
    conan create . conan/stable -s build_type=Release --profile clang --build missing

CONAN_REVISIONS_ENABLED=1 \
    CONAN_VERBOSE_TRACEBACK=1 \
    CONAN_PRINT_RUN_COMMANDS=1 \
    CONAN_LOGGING_LEVEL=10 \
    conan upload $PKG_NAME --all -r=conan-local -c --retry 3 --retry-wait 10 --force
```

## conan Flow

```bash
export CC=gcc
export CXX=g++

# https://www.pclinuxos.com/forum/index.php?topic=129566.0
# export LDFLAGS="$LDFLAGS -ltinfo -lncurses"

# If compilation of LLVM fails on your machine (`make` may be killed by OS due to lack of RAM e.t.c.)
# - set env. var. CONAN_LLVM_SINGLE_THREAD_BUILD to 1.
export CONAN_LLVM_SINGLE_THREAD_BUILD=1

$CC --version
$CXX --version

# see BUGFIX (i386 instead of x86_64)
export CXXFLAGS=-m64
export CFLAGS=-m64
export LDFLAGS=-m64

conan source .
conan install --build missing --profile clang  -s build_type=Release .
conan build . \
  --build-folder . \
  --source-folder .
conan package . \
  --build-folder . \
  --package-folder . \
  --source-folder .
conan export-pkg . \
  conan/stable \
  --package-folder . \
  --settings build_type=Release \
  --force \
  --profile clang
conan test test_package llvm_tools/master@conan/stable --settings build_type=Release --profile clang
```

## Build with sanitizers support

Use `-o llvm_tools:enable_msan=True` like so:

```bash
export CC=gcc
export CXX=g++

# https://www.pclinuxos.com/forum/index.php?topic=129566.0
# export LDFLAGS="$LDFLAGS -ltinfo -lncurses"

# If compilation of LLVM fails on your machine (`make` may be killed by OS due to lack of RAM e.t.c.)
# - set env. var. CONAN_LLVM_SINGLE_THREAD_BUILD to 1.
export CONAN_LLVM_SINGLE_THREAD_BUILD=1

$CC --version
$CXX --version

# see BUGFIX (i386 instead of x86_64)
export CXXFLAGS=-m64
export CFLAGS=-m64
export LDFLAGS=-m64

CONAN_REVISIONS_ENABLED=1 \
    CONAN_VERBOSE_TRACEBACK=1 \
    CONAN_PRINT_RUN_COMMANDS=1 \
    CONAN_LOGGING_LEVEL=10 \
    GIT_SSL_NO_VERIFY=true \
    conan create . conan/stable \
      -s build_type=Release \
      --profile clang \
      -o llvm_tools:include_what_you_use=False \
      -o llvm_tools:enable_msan=True
```

NOTE: msan requires to set `-stdlib=libc++ -lc++abi` and use include and lib paths from conan package (see above). See https://github.com/google/sanitizers/wiki/MemorySanitizerLibcxxHowTo#instrumented-gtest

Perform checks:

```bash
# must exist
find ~/.conan -name libclang_rt.msan_cxx-x86_64.a

# see https://stackoverflow.com/a/47705420
nm -an $(find ~/.conan -name *libc++.so.1 | grep "llvm_tools/master/conan/stable/package/") | grep san
```

## Avoid Debug build, prefer Release builds

Debug build of llvm may take a lot of time or crash due to lack of RAM or CPU

## How to keep multiple llvm_tools package revisions in local cache

Usually you want to build LLVM in multiple configurations and re-use pre-built packages. Approach below allows to avoid full re-builds via `conan create` on each change in options.

Option 1: Create conan server. Solves problem because only conan client can have only one revision installed simultaneously (see https://github.com/conan-io/conan/issues/6836 )

Option 2: Store on disk multiple pre-built llvm_tools packages. Export desired version and work with that version globally.

Example below shows how to install multiple LLVM revisions: both with default options and with sanitizer (MSAN) enabled (not that you can enable only one of them globally using `conan export-pkg`).

## Build locally (revision with default options):

```bash
export CC=gcc
export CXX=g++

# https://www.pclinuxos.com/forum/index.php?topic=129566.0
# export LDFLAGS="$LDFLAGS -ltinfo -lncurses"

# If compilation of LLVM fails on your machine (`make` may be killed by OS due to lack of RAM e.t.c.)
# - set env. var. CONAN_LLVM_SINGLE_THREAD_BUILD to 1.
export CONAN_LLVM_SINGLE_THREAD_BUILD=1

$CC --version
$CXX --version

# see BUGFIX (i386 instead of x86_64)
export CXXFLAGS=-m64
export CFLAGS=-m64
export LDFLAGS=-m64

CONAN_REVISIONS_ENABLED=1 \
CONAN_VERBOSE_TRACEBACK=1 \
CONAN_PRINT_RUN_COMMANDS=1 \
CONAN_LOGGING_LEVEL=10 \
GIT_SSL_NO_VERIFY=true \
  cmake -E time \
    conan install . \
    --install-folder local_build \
    -s build_type=Release \
    -s llvm_tools:build_type=Release \
    --profile clang

CONAN_REVISIONS_ENABLED=1 \
CONAN_VERBOSE_TRACEBACK=1 \
CONAN_PRINT_RUN_COMMANDS=1 \
CONAN_LOGGING_LEVEL=10 \
GIT_SSL_NO_VERIFY=true \
  cmake -E time \
    conan source . --source-folder local_build

conan build . \
  --build-folder local_build \
  --source-folder local_build

conan package . \
  --build-folder local_build \
  --package-folder local_build/package_dir \
  --source-folder local_build
```

Now use `conan export-pkg` (or conan editable mode) to globally enable some revision of llvm_tools package.

```bash
conan export-pkg . \
  conan/stable \
  --package-folder local_build/package_dir \
  --settings build_type=Release \
  --force \
  --profile clang
```

## Build locally (revision with msan enabled):

```bash
export CC=gcc
export CXX=g++

# https://www.pclinuxos.com/forum/index.php?topic=129566.0
# export LDFLAGS="$LDFLAGS -ltinfo -lncurses"

# If compilation of LLVM fails on your machine (`make` may be killed by OS due to lack of RAM e.t.c.)
# - set env. var. CONAN_LLVM_SINGLE_THREAD_BUILD to 1.
export CONAN_LLVM_SINGLE_THREAD_BUILD=1

$CC --version
$CXX --version

# see BUGFIX (i386 instead of x86_64)
export CXXFLAGS=-m64
export CFLAGS=-m64
export LDFLAGS=-m64

CONAN_REVISIONS_ENABLED=1 \
CONAN_VERBOSE_TRACEBACK=1 \
CONAN_PRINT_RUN_COMMANDS=1 \
CONAN_LOGGING_LEVEL=10 \
GIT_SSL_NO_VERIFY=true \
  cmake -E time \
    conan install . \
    --install-folder local_build_msan \
    -s build_type=Release \
    -s llvm_tools:build_type=Release \
    --profile clang \
      -o llvm_tools:include_what_you_use=False \
      -o llvm_tools:enable_msan=True

CONAN_REVISIONS_ENABLED=1 \
CONAN_VERBOSE_TRACEBACK=1 \
CONAN_PRINT_RUN_COMMANDS=1 \
CONAN_LOGGING_LEVEL=10 \
GIT_SSL_NO_VERIFY=true \
  cmake -E time \
    conan source . --source-folder local_build_msan

conan build . \
  --build-folder local_build_msan \
  --source-folder local_build_msan

conan package . \
  --build-folder local_build_msan \
  --package-folder local_build_msan/package_dir \
  --source-folder local_build_msan
```

Now use `conan export-pkg` (or conan editable mode) to globally enable some revision of llvm_tools package.

```bash
conan export-pkg . \
  conan/stable \
  --package-folder local_build_msan/package_dir \
  --settings build_type=Release \
  --force \
  --profile clang \
    -o llvm_tools:include_what_you_use=False \
    -o llvm_tools:enable_msan=True
```

## Build locally (revision with include_what_you_use enabled):

```bash
export CC=gcc
export CXX=g++

# https://www.pclinuxos.com/forum/index.php?topic=129566.0
# export LDFLAGS="$LDFLAGS -ltinfo -lncurses"

# If compilation of LLVM fails on your machine (`make` may be killed by OS due to lack of RAM e.t.c.)
# - set env. var. CONAN_LLVM_SINGLE_THREAD_BUILD to 1.
export CONAN_LLVM_SINGLE_THREAD_BUILD=1

$CC --version
$CXX --version

# see BUGFIX (i386 instead of x86_64)
export CXXFLAGS=-m64
export CFLAGS=-m64
export LDFLAGS=-m64

CONAN_REVISIONS_ENABLED=1 \
CONAN_VERBOSE_TRACEBACK=1 \
CONAN_PRINT_RUN_COMMANDS=1 \
CONAN_LOGGING_LEVEL=10 \
GIT_SSL_NO_VERIFY=true \
  cmake -E time \
    conan install . \
    --install-folder local_build_iwyu \
    -s build_type=Release \
    -s llvm_tools:build_type=Release \
    --profile clang \
      -o llvm_tools:include_what_you_use=True

CONAN_REVISIONS_ENABLED=1 \
CONAN_VERBOSE_TRACEBACK=1 \
CONAN_PRINT_RUN_COMMANDS=1 \
CONAN_LOGGING_LEVEL=10 \
GIT_SSL_NO_VERIFY=true \
  cmake -E time \
    conan source . --source-folder local_build_iwyu

conan build . \
  --build-folder local_build_iwyu \
  --source-folder local_build_iwyu

conan package . \
  --build-folder local_build_iwyu \
  --package-folder local_build_iwyu/package_dir \
  --source-folder local_build_iwyu
```

Now use `conan export-pkg` (or conan editable mode) to globally enable some revision of llvm_tools package.

```bash
conan export-pkg . \
  conan/stable \
  --package-folder local_build_iwyu/package_dir \
  --settings build_type=Release \
  --force \
  --profile clang \
    -o llvm_tools:include_what_you_use=True
```
