# About

conan package for llvm tools:

* include-what-you-use
* clang-tidy
* scan-build
* ccc-analyzer
* c++-analyzer
* clang-format
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

NOTE: use `-s llvm_tools:build_type=Release` during `conan install`

## LICENSE

MIT for conan package. Packaged source uses own license, see https://releases.llvm.org/2.8/LICENSE.TXT and https://github.com/root-project/root/blob/master/LICENSE

## Before build

```bash
sudo apt-get install build-essential

sudo apt-get install libncurses5-dev libncursesw5-dev libtinfo-dev

# optionaL: swig4, libeidt-dev
```

read https://llvm.org/docs/CMake.html and https://fuchsia.dev/fuchsia-src/development/build/toolchain and https://github.com/deepinwiki/wiki/wiki/%E7%94%A8LLVM%E7%BC%96%E8%AF%91%E5%86%85%E6%A0%B8

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
conan source .
conan install --build missing --profile clang  -s build_type=Release .
conan build . --build-folder=.
conan package --build-folder=. .
conan export-pkg . conan/stable --settings build_type=Release --force --profile clang
conan test test_package llvm_tools/master@conan/stable --settings build_type=Release --profile clang
```

## Avoid Debug build, prefer Release builds

Debug build of llvm may take a lot of time or crash due to lack of RAM or CPU

## Docker build with `--no-cache`

```bash
export MY_IP=$(ip route get 8.8.8.8 | sed -n '/src/{s/.*src *\([^ ]*\).*/\1/p;q}')
sudo -E docker build \
    --build-arg PKG_NAME=llvm_tools \
    --build-arg PKG_CHANNEL=conan/stable \
    --build-arg PKG_UPLOAD_NAME=llvm_tools/master@conan/stable \
    --build-arg CONAN_EXTRA_REPOS="conan-local http://$MY_IP:8081/artifactory/api/conan/conan False" \
    --build-arg CONAN_EXTRA_REPOS_USER="user -p password1 -r conan-local admin" \
    --build-arg CONAN_UPLOAD="conan upload --all -r=conan-local -c --retry 3 --retry-wait 10 --force" \
    --build-arg BUILD_TYPE=Release \
    -f llvm_tools_source.Dockerfile --tag llvm_tools_repoadd_source_install . --no-cache

sudo -E docker build \
    --build-arg PKG_NAME=llvm_tools \
    --build-arg PKG_CHANNEL=conan/stable \
    --build-arg PKG_UPLOAD_NAME=llvm_tools/master@conan/stable \
    --build-arg CONAN_EXTRA_REPOS="conan-local http://$MY_IP:8081/artifactory/api/conan/conan False" \
    --build-arg CONAN_EXTRA_REPOS_USER="user -p password1 -r conan-local admin" \
    --build-arg CONAN_UPLOAD="conan upload --all -r=conan-local -c --retry 3 --retry-wait 10 --force" \
    --build-arg BUILD_TYPE=Release \
    -f llvm_tools_build.Dockerfile --tag llvm_tools_build_package_export_test_upload . --no-cache

# OPTIONAL: clear unused data
sudo -E docker rmi llvm_tools_*
```

## How to run single command in container using bash with gdb support

```bash
# about gdb support https://stackoverflow.com/a/46676907
docker run --cap-add=SYS_PTRACE --security-opt seccomp=unconfined --rm --entrypoint="/bin/bash" -v "$PWD":/home/u/project_copy -w /home/u/project_copy -p 50051:50051 --name DEV_llvm_tools llvm_tools -c pwd
```