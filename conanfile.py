import os, re, stat, fnmatch, platform, glob, traceback, shutil
from conans import ConanFile, CMake, tools
from conans.tools import Version
from conans.errors import ConanInvalidConfiguration
from conans.model.version import Version

# Users locally they get the 1.0.0 version,
# without defining any env-var at all,
# and CI servers will append the build number.
# USAGE
# version = get_version("1.0.0")
# BUILD_NUMBER=-pre1+build2 conan export-pkg . my_channel/release
def get_version(version):
    bn = os.getenv("BUILD_NUMBER")
    return (version + bn) if bn else version

class LLVMToolsConan(ConanFile):
    name = "llvm_tools"

    version = get_version("master")
    # TODO: llvmorg-9.0.1
    llvm_version = "release/10.x"
    iwyu_version = "clang_10"

    description = "conan package for LLVM TOOLS"
    topics = ("c++", "conan", "clang", "include-what-you-use", "llvm", "iwyu")
    #url = "https://github.com/bincrafters/conan-folly" # TODO
    #homepage = "https://github.com/facebook/folly" # TODO
    #license = "Apache-2.0" # TODO

    # Constrains build_type inside a recipe to Release!
    settings = "os_build", "build_type", "arch_build", "compiler", "arch"

    options = {
        # hack (forcing -m64)
        # sanitizer_allocator.cpp.o' is incompatible with i386:x86-64 output
        # see https://bugs.llvm.org/show_bug.cgi?id=42463
        "force_x86_64": [True, False],
        "link_ltinfo": [True, False],
        "include_what_you_use": [True, False],
        # Sanitizer is well supported on Linux
        # see https://clang.llvm.org/docs/MemorySanitizer.html#handling-external-code
        "enable_msan": [True, False],
        "enable_tsan": [True, False],
        "enable_ubsan": [True, False],
        "enable_asan": [True, False]
    }

    default_options = {
        "force_x86_64": True,
        "link_ltinfo": False,
        "include_what_you_use": True,
        "enable_msan": False,
        "enable_tsan": False,
        "enable_ubsan": False,
        "enable_asan": False
    }

    exports = ["LICENSE.md"]

    exports_sources = ["LICENSE", "README.md", "include/*", "src/*",
                       "cmake/*", "CMakeLists.txt", "tests/*", "benchmarks/*",
                       "scripts/*", "patches/*"]

    generators = 'cmake_find_package', "cmake", "cmake_paths"

    llvm_repo_url = "https://github.com/llvm/llvm-project.git"
    iwyu_repo_url = "https://github.com/include-what-you-use/include-what-you-use.git"

    llvm_libs = {
        'LLVMCore': True,
        'LLVMAnalysis': True,
        'LLVMSupport': True,
        'LLVMipo': True,
        'LLVMIRReader': True,
        'LLVMBinaryFormat': True,
        'LLVMBitReader': True,
        'LLVMBitWriter': True,
        'LLVMMC': True,
        'LLVMMCParser': True,
        'LLVMTransformUtils': True,
        'LLVMScalarOpts': True,
        'LLVMLTO': True,
        'LLVMCoroutines': True,
        'LLVMCoverage': True,
        'LLVMInstCombine': True,
        'LLVMInstrumentation': True,
        'LLVMLinker': True,
        'LLVMObjCARCOpts': True,
        'LLVMObject': True,
        'LLVMPasses': True,
        'LLVMProfileData': True,
        'LLVMTarget': True,
        'LLVMLibDriver': True,
        'LLVMLineEditor': True,
        'LLVMMIRParser': True,
        'LLVMOption': True,
        'LLVMRuntimeDyld': True,
        'LLVMSelectionDAG': True,
        'LLVMSymbolize': True,
        'LLVMTableGen': True,
        'LLVMVectorize': True,
        'clangARCMigrate': True,
        'clangAnalysis': True,
        'clangAST': True,
        'clangASTMatchers': True,
        'clangBasic': True,
        'clangCodeGen': True,
        'clangDriver': True,
        'clangDynamicASTMatchers': True,
        'clangEdit': True,
        'clangFormat': True,
        'clangFrontend': True,
        'clangFrontendTool': True,
        'clangIndex': True,
        'clangLex': True,
        'clangParse': True,
        'clangRewrite': True,
        'clangRewriteFrontend': True,
        'clangSema': True,
        'clangSerialization': True,
        'clangStaticAnalyzerCheckers': True,
        'clangStaticAnalyzerCore': True,
        'clangStaticAnalyzerFrontend': True,
        'clangTooling': True,
        'clangToolingCore': True,
        'clangToolingRefactoring': True,
        'clangStaticAnalyzerCore': True,
        'clangDynamicASTMatchers': True,
        'clangCodeGen': True,
        'clangFrontendTool': True,
        'clang': True,
        'clangEdit': True,
        'clangRewriteFrontend': True,
        'clangDriver': True,
        'clangSema': True,
        'clangASTMatchers': True,
        'clangSerialization': True,
        'clangBasic': True,
        'clangAST': True,
        'clangTooling': True,
        'clangStaticAnalyzerFrontend': True,
        'clangFormat': True,
        'clangLex': True,
        'clangFrontend': True,
        'clangRewrite': True,
        'clangToolingCore': True,
        'clangIndex': True,
        'clangAnalysis': True,
        'clangParse': True,
        'clangStaticAnalyzerCheckers': True,
        'clangARCMigrate': True,
    }

    @property
    def _llvm_source_subfolder(self):
        return "llvm_project"

    @property
    def _iwyu_source_subfolder(self):
        return "iwyu"

    @property
    def _libcxx(self):
      return str(self.settings.get_safe("compiler.libcxx"))

    @property
    def _has_sanitizers(self):
      return self.options.enable_msan \
              or self.options.enable_asan \
              or self.options.enable_ubsan \
              or self.options.enable_tsan

    @property
    def _lower_build_type(self):
      return str(self.settings.build_type).lower()

    # Do not copy large files
    # https://stackoverflow.com/a/13814557
    def copytree(self, src, dst, symlinks=False, ignore=None, verbose=False):
        if not os.path.exists(dst):
            os.makedirs(dst)
        ignore_list = ['.travis.yml', '.git', '.make', '.o', '.obj', '.marks', '.internal', 'CMakeFiles', 'CMakeCache']
        for item in os.listdir(src):
            if item not in ignore_list:
              s = os.path.join(src, item)
              d = os.path.join(dst, item)
              if verbose:
                self.output.info('copying %s into %d' % (s, d))
              if os.path.isdir(s):
                  self.copytree(s, d, symlinks, ignore)
              else:
                  if not os.path.exists(d) or os.stat(s).st_mtime - os.stat(d).st_mtime > 1:
                      shutil.copy2(s, d)
            elif verbose:
              self.output.info('IGNORED copying %s' % (item))

    def configure(self):
        compiler_version = Version(self.settings.compiler.version.value)
        if self.settings.build_type != "Release":
            raise ConanInvalidConfiguration("This library is compatible only with Release builds. Debug build of llvm may take a lot of time or crash due to lack of RAM or CPU")
        if (self.options.enable_msan \
            or self.options.enable_tsan \
            or self.options.enable_asan \
            or self.options.enable_ubsan) \
            and not self.settings.compiler in ['clang', 'apple-clang', 'clang-cl']:
            raise ConanInvalidConfiguration("This package is only compatible with clang")
            if Version(self.settings.compiler.version.value) < "6.0":
                raise ConanInvalidConfiguration("%s %s couldn't be built by clang < 6.0" % (self.name, self.version))

        if self.options.include_what_you_use and (self.options.enable_msan \
            or self.options.enable_tsan \
            or self.options.enable_asan \
            or self.options.enable_ubsan):
            raise ConanInvalidConfiguration("disable include_what_you_use when sanitizers enabled")

    def requirements(self):
        print('self.settings.compiler {}'.format(self.settings.compiler))

    def source(self):
        # LLVM
        self.run('git clone -b {} --progress --depth 100 --recursive --recurse-submodules {} {}'.format(self.llvm_version, self.llvm_repo_url, self._llvm_source_subfolder))

        # IWYU
        if self.options.include_what_you_use:
            self.run('git clone -b {} --progress --depth 100 --recursive --recurse-submodules {} {}'.format(self.iwyu_version, self.iwyu_repo_url, self._iwyu_source_subfolder))

    def prepend_to_definition(self, cmake, name, value):
      cmake.definitions[name]=value + " " \
        + (cmake.definitions[name] if name in cmake.definitions else "")

    # see https://releases.llvm.org/9.0.0/docs/CMake.html
    def _configure_cmake(self, llvm_projects, llvm_runtimes, llvm_sanitizer=""):
        self.output.info('configuring LLVM')

        llvm_src_dir = os.path.join(self._llvm_source_subfolder, "llvm")
        self.output.info('llvm_src_dir is {}'.format(llvm_src_dir))

        compiler_rt_src_dir = os.path.join(self._llvm_source_subfolder, "compiler-rt")
        self.output.info('compiler_rt_src_dir is {}'.format(compiler_rt_src_dir))

        for patch in os.listdir(os.path.join(self.source_folder, "patches")):
            patchpath = os.path.join(self.source_folder, "patches", patch)
            self.output.info('patch is {}'.format(patchpath))
            tools.patch(base_path=compiler_rt_src_dir, patch_file=patchpath)

        cmake = CMake(self, set_cmake_flags=True)
        cmake.verbose = True

        # don't hang all CPUs and force OS to kill build process
        cpu_count = max(tools.cpu_count() - 3, 1)
        self.output.info('Detected %s CPUs' % (cpu_count))

        # https://bugs.llvm.org/show_bug.cgi?id=44074
        # cmake.definitions["EXECUTION_ENGINE_USE_LLVM_UNWINDER"]="ON"

        # Semicolon-separated list of projects to build
        # (clang;clang-tools-extra;compiler-rt;debuginfo-tests;libc;libclc;libcxx;libcxxabi;libunwind;lld;lldb;llgo;mlir;openmp;parallel-libs;polly;pstl),
        # or "all".
        # This flag assumes that projects are checked out side-by-side and not nested,
        # i.e. clang needs to be in parallel of llvm instead of nested in llvm/tools.
        # This feature allows to have one build for only LLVM and another
        # for clang+llvm using the same source checkout.
        cmake.definitions["LLVM_ENABLE_PROJECTS"]=llvm_projects

        # see Building LLVM with CMake https://llvm.org/docs/CMake.html
        cmake.definitions["LLVM_PARALLEL_COMPILE_JOBS"]=cpu_count

        # Microsoft Visual C++ specific
        # Specifies the maximum number of parallel compiler jobs
        # to use per project when building with msbuild or Visual Studio.
        # Only supported for the Visual Studio 2010 CMake generator.
        # 0 means use all processors. Default is 0.
        cmake.definitions["LLVM_COMPILER_JOBS"]=cpu_count

        cmake.definitions["LLVM_PARALLEL_LINK_JOBS"]=1

        # TODO: make customizable
        # This should speed up building debug builds
        # see https://www.productive-cpp.com/improving-cpp-builds-with-split-dwarf/
        #cmake.definitions["LLVM_USE_SPLIT_DWARF"]="ON"

        # force Release build
        #cmake.definitions["CMAKE_BUILD_TYPE"]="Release"

        if self.options.link_ltinfo:
            # https://github.com/MaskRay/ccls/issues/556
            # https://stackoverflow.com/a/51924150
            self.prepend_to_definition(cmake, "CMAKE_CXX_LINKER_FLAGS", "-lncurses -ltinfo")

        if len(llvm_runtimes) > 0:
          # Semicolon-separated list of runtimes to build
          # (libcxx;libcxxabi;libunwind;compiler-rt;...), or "all".
          # Enable some projects to be built as runtimes
          # which means these projects will be built using the just-built rather
          # than the host compiler
          cmake.definitions["LLVM_ENABLE_RUNTIMES"]=llvm_runtimes

        # sanitizer runtimes - runtime libraries that are required
        # to run the code with sanitizer instrumentation.
        # This includes runtimes for:
        # AddressSanitizer ThreadSanitizer UndefinedBehaviorSanitizer
        # MemorySanitizer LeakSanitizer DataFlowSanitizer
        self.output.info('llvm_sanitizer = {}'.format(llvm_sanitizer))
        if len(llvm_sanitizer) > 0:
            cmake.definitions["LLVM_USE_SANITIZER"]=llvm_sanitizer
            self.output.info('LLVM_USE_SANITIZER = {}'.format(llvm_sanitizer))

            # see libcxx in LLVM_ENABLE_PROJECTS
            # compile using libc++ instead of the system default
            #cmake.definitions["LLVM_ENABLE_LIBCXX"]="ON"

            # Build clang-tidy/clang-format
            cmake.definitions["LLVM_TOOL_CLANG_TOOLS_EXTRA_BUILD"]="OFF"

            cmake.definitions["LLVM_TOOL_OPENMP_BUILD"]="OFF"

            cmake.definitions["CLANG_ENABLE_ARCMT"]="OFF"
            cmake.definitions["CLANG_ENABLE_STATIC_ANALYZER"]="OFF"
            cmake.definitions["CLANG_ENABLE_FORMAT"]="OFF"
            #cmake.definitions["CLANG_TOOL_CLANG_CHECK_BUILD"]="OFF"
            #cmake.definitions["CLANG_PLUGIN_SUPPORT"]="OFF"
            cmake.definitions["CLANG_TOOL_CLANG_FORMAT_BUILD"]="OFF"
            cmake.definitions["CLANG_TOOL_CLANG_FUZZER_BUILD"]="OFF"

            # build compiler-rt, libcxx etc.
            # cmake.definitions["LLVM_BUILD_RUNTIME"]="ON"

            # SANITIZER_ALLOW_CXXABI

            # TODO: make customizable
            # LLVM_BUILD_EXTERNAL_COMPILER_RT:BOOL

            # use uninstrumented llvm-tblgen
            # see https://stackoverflow.com/questions/56454026/building-libc-with-memorysanitizer-instrumentation-fails-due-to-memorysanitize
            #llvm_tblgen=os.path.join(self.package_folder, "bin", "llvm-tblgen")
            #cmake.definitions["LLVM_TABLEGEN"]="{}".format(llvm_tblgen)
            #if not os.path.exists(llvm_tblgen):
            #    raise Exception("Unable to find path: {}".format(llvm_tblgen))
        else:
            # use UNINSTRUMENTED llvm-ar, llvml-symbolizer, etc.
            cmake.definitions["LLVM_USE_SANITIZER"]=""
            #cmake.definitions["LLVM_TOOL_CLANG_TOOLS_EXTRA_BUILD"]="ON"
            cmake.definitions["CLANG_ENABLE_STATIC_ANALYZER"]="ON"
            cmake.definitions["CLANG_TOOL_CLANG_CHECK_BUILD"]="ON"
            cmake.definitions["CLANG_PLUGIN_SUPPORT"]="ON"
            cmake.definitions["CLANG_TOOL_CLANG_FORMAT_BUILD"]="ON"
            cmake.definitions["CLANG_ENABLE_FORMAT"]="ON"
            cmake.definitions["CLANG_TOOL_CLANG_FUZZER_BUILD"]="ON"

        # Build LLVM and tools with PGO instrumentation
        # If enabled, source-based code coverage instrumentation
        # is enabled while building llvm.
        cmake.definitions["LLVM_BUILD_INSTRUMENTED"]="OFF"

        # crt_defines['SANITIZER_CXX_ABI'] = 'libcxxabi'

        # Make libc++.so a symlink to libc++.so.x instead of a linker script that
        # also adds -lc++abi.  Statically link libc++abi to libc++ so it is not
        # necessary to pass -lc++abi explicitly.  This is needed only for Linux.
        # if utils.host_is_linux():
        #     stage2_extra_defines['LIBCXX_ENABLE_STATIC_ABI_LIBRARY'] = 'ON'
        #     stage2_extra_defines['LIBCXX_ENABLE_ABI_LINKER_SCRIPT'] = 'OFF'

        # NOTE: must match LLVM_LINK_LLVM_DYLIB
        # NOTE: This cannot be used in conjunction with BUILD_SHARED_LIBS.
        # If enabled, the target for building the libLLVM shared library is added.
        # This library contains all of LLVM’s components in a single shared library.
        # Defaults to OFF.
        # Tools will only be linked to the libLLVM shared library
        # if LLVM_LINK_LLVM_DYLIB is also ON.
        # The components in the library can be customised
        # by setting LLVM_DYLIB_COMPONENTS to a list of the desired components.
        cmake.definitions["LLVM_BUILD_LLVM_DYLIB"]="OFF"

        # If enabled, tools will be linked with the libLLVM shared library.
        # Defaults to OFF.
        # Setting LLVM_LINK_LLVM_DYLIB to ON also sets LLVM_BUILD_LLVM_DYLIB to ON.
        cmake.definitions["LLVM_LINK_LLVM_DYLIB"]="OFF"

        # LLVM_DYLIB_EXPORT_ALL

        # see lld in LLVM_ENABLE_PROJECTS
        # This option is equivalent to -DLLVM_USE_LINKER=lld,
        # except during a 2-stage build where a dependency
        # is added from the first stage to the second ensuring
        # that lld is built before stage2 begins.
        #cmake.definitions["LLVM_ENABLE_LLD"]="ON"

        # LLVM_ENABLE_LLD and LLVM_USE_LINKER can't be set at the same time
        #if cmake.definitions["LLVM_ENABLE_LLD"] != "ON":
        #  cmake.definitions["LLVM_USE_LINKER"]="lld"

        # Add -flto or -flto= flags to the compile and link command lines, enabling link-time optimization.
        # Possible values are Off, On, Thin and Full. Defaults to OFF.
        # TODO: BUG when LTO ON: https://bugs.gentoo.org/show_bug.cgi?format=multiple&id=667108
        # You can set the LLVM_ENABLE_LTO option on your stage-2 build
        # to Thin or Full to enable building LLVM with LTO.
        # These options will significantly increase link time of the binaries
        # in the distribution, but it will create much faster binaries.
        # This option should not be used if your distribution includes static archives,
        # as the objects inside the archive will be LLVM bitcode,
        # which is not portable.
        cmake.definitions["LLVM_ENABLE_LTO"]="OFF"

        # Enable building with zlib to support compression/uncompression in LLVM tools.
        # Defaults to ON.
        cmake.definitions["LLVM_ENABLE_ZLIB"]="ON"

        # Indicates whether the LLVM Interpreter will be linked with
        # the Foreign Function Interface library (libffi)
        # in order to enable calling external functions.
        # If the library or its headers are installed in a custom location,
        # you can also set the variables FFI_INCLUDE_DIR and FFI_LIBRARY_DIR
        # to the directories where ffi.h and libffi.so can be found, respectively.
        # Defaults to OFF.
        cmake.definitions["LLVM_ENABLE_FFI"]="OFF"

        # Build LLVM tools. Defaults to ON.
        # Targets for building each tool are generated in any case.
        # You can build a tool separately by invoking its target.
        # For example, you can build llvm-as
        # with a Makefile-based system
        # by executing make llvm-as at the root of your build directory.
        cmake.definitions["LLVM_BUILD_TOOLS"]="OFF" \
          if len(llvm_sanitizer) > 0 else "ON"

        cmake.definitions["COMPILER_RT_BUILD_LIBFUZZER"] = "OFF" \
          if len(llvm_sanitizer) > 0 else "ON"

        # Generate build targets for the LLVM tools.
        # Defaults to ON.
        # You can use this option to disable the generation of build targets
        # for the LLVM tools.
        cmake.definitions["LLVM_INCLUDE_TOOLS"]="ON"

        #cmake.definitions["LLVM_INCLUDE_UTILS"]="ON"
        #cmake.definitions["LLVM_BUILD_UTILS"]="ON"
        # LLVM_INSTALL_UTILS
        # LLVM_TOOLS_INSTALL_DIR

        # Enable building OProfile JIT support. Defaults to OFF.
        cmake.definitions["LLVM_USE_OPROFILE"] = "OFF"

        # NOTE: msan build requires
        # existing file ~/.conan/data/.../master/conan/stable/package/.../lib/clang/x.x.x/lib/linux/libclang_rt.msan_cxx-x86_64.a
        # same for tsan\ubsan\asan\etc.
        cmake.definitions["COMPILER_RT_BUILD_SANITIZERS"] = "ON"

        # TODO
        # builtins - a simple library that provides an implementation of the low-level target-specific hooks required by code generation and other runtime components. For example, when compiling for a 32-bit target, converting a double to a 64-bit unsigned integer is compiling into a runtime call to the "__fixunsdfdi" function. The builtins library provides optimized implementations of this and other low-level routines, either in target-independent C form, or as a heavily-optimized assembly.
        # builtins provides full support for the libgcc interfaces on supported targets and high performance hand tuned implementations of commonly used functions like __floatundidf in assembly that are dramatically faster than the libgcc implementations. It should be very easy to bring builtins to support a new target by adding the new routines needed by that target.
        cmake.definitions["COMPILER_RT_BUILD_BUILTINS"] = "OFF"

        cmake.definitions["COMPILER_RT_INCLUDE_TESTS"] = "OFF"

        # TODO
        #cmake.definitions['COMPILER_RT_BUILD_CRT'] = 'OFF'
        #cmake.definitions['COMPILER_RT_BUILD_XRAY'] = 'OFF'
        # profile - library which is used to collect coverage information.
        #cmake.definitions['COMPILER_RT_BUILD_PROFILE'] = 'OFF'

        # TODO
        #'COMPILER_RT_BAREMETAL_BUILD:BOOL': 'ON',
        #'COMPILER_RT_DEFAULT_TARGET_ONLY': 'ON',
        # COMPILER_RT_OS_DIR

        # TODO: make customizable
        #cmake.definitions["CMAKE_CXX_STANDARD"]="17"

        cmake.definitions["BUILD_SHARED_LIBS"]="ON"
        if self.options.enable_msan:
          # Static linking is not supported.
          # see https://clang.llvm.org/docs/MemorySanitizer.html
          cmake.definitions["BUILD_SHARED_LIBS"]="ON"
          # To build with MSan support you first need
          # to build libc++ with MSan support.
          cmake.definitions["LLVM_ENABLE_LIBCXX"]="ON"

        # TODO: make customizable
        #cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"]="ON"

        cmake.definitions["BUILD_TESTS"]="OFF"

        # TODO: make customizable
        # If disabled, do not try to build the OCaml and go bindings.
        cmake.definitions["LLVM_ENABLE_BINDINGS"]="OFF"

        # Install symlinks from the binutils tool names
        # to the corresponding LLVM tools.
        # For example, ar will be symlinked to llvm-ar.
        cmake.definitions["LLVM_INSTALL_BINUTILS_SYMLINKS"]="OFF"

        # TODO: make customizable
        #cmake.definitions["LLVM_INSTALL_CCTOOLS_SYMLINKS"]="ON"

        # Semicolon-separated list of targets to build,
        # or all for building all targets.
        # Case-sensitive. Defaults to all.
        # Example: -DLLVM_TARGETS_TO_BUILD="X86;PowerPC".
        # Known targets:
        # AArch64 AMDGPU ARM BPF Hexagon Lanai
        # Mips MSP430 NVPTX PowerPC RISCV Sparc SystemZ WebAssembly X86 XCore
        cmake.definitions["LLVM_TARGETS_TO_BUILD"]="X86"

        # hack (forcing -m64)
        # sanitizer_allocator.cpp.o' is incompatible with i386:x86-64 output
        # see https://bugs.llvm.org/show_bug.cgi?id=42463
        if self.options.force_x86_64:
            self.prepend_to_definition(cmake, "CMAKE_C_FLAGS", "-m64")
            self.prepend_to_definition(cmake, "CMAKE_CXX_FLAGS", "-m64")
            self.prepend_to_definition(cmake, "CMAKE_EXE_LINKER_FLAGS", "-m64")
            self.prepend_to_definition(cmake, "CMAKE_MODULE_LINKER_FLAGS", "-m64")
            self.prepend_to_definition(cmake, "CMAKE_SHARED_LINKER_FLAGS", "-m64")
            # LLVM target to use for native code generation. This is required for JIT generation. It defaults to â€œhostâ€, meaning that it shall pick the architecture of the machine where LLVM is being built. If you are cross-compiling, set it to the target architecture name.
            cmake.definitions["LLVM_TARGET_ARCH"]="x86_64"
            # Default triple for which compiler-rt runtimes will be built.
            cmake.definitions["COMPILER_RT_DEFAULT_TARGET_TRIPLE"]="x86_64-unknown-linux-gnu"
            # Default target for which LLVM will generate code.
            cmake.definitions["LLVM_DEFAULT_TARGET_TRIPLE"]="x86_64-unknown-linux-gnu"

        # TODO: make customizable
        #cmake.definitions["PYTHON_EXECUTABLE"]=""

        # Embed version control revision info (svn revision number or Git revision id).
        # The version info is provided by the LLVM_REVISION macro
        # in llvm/include/llvm/Support/VCSRevision.h.
        # Developers using git who don’t need revision info
        # can disable this option to avoid re-linking most binaries
        # after a branch switch. Defaults to ON.
        cmake.definitions["LLVM_APPEND_VC_REV"]="ON"

        # Build LLVM with exception-handling support.
        # This is necessary if you wish to link against LLVM libraries
        # and make use of C++ exceptions in your own code
        # that need to propagate through LLVM code. Defaults to OFF.
        cmake.definitions["LLVM_ENABLE_EH"]="OFF"

        # Build 32-bit executables and libraries on 64-bit systems.
        # This option is available only on some 64-bit Unix systems.
        # Defaults to OFF.
        cmake.definitions["LLVM_BUILD_32_BITS"]="OFF"

        # Enable additional time/memory expensive checking. Defaults to OFF.
        cmake.definitions["LLVM_ENABLE_EXPENSIVE_CHECKS"]="OFF"
        #cmake.definitions["LLVM_ENABLE_EXPENSIVE_CHECKS"]="ON" \
        #  if len(llvm_sanitizer) > 0 else "OFF"

        # Tell the build system that an IDE is being used.
        # This in turn disables the creation of certain
        # convenience build system targets,
        # such as the various install-* and check-* targets,
        # since IDEs don’t always deal well with a large number of targets.
        # This is usually autodetected, but it can be configured manually
        # to explicitly control the generation of those targets.
        # One scenario where a manual override may be desirable
        # is when using Visual Studio 2017’s CMake integration,
        # which would not be detected as an IDE otherwise.
        cmake.definitions["LLVM_ENABLE_IDE"]="OFF"

        # Add the -fPIC flag to the compiler command-line,
        # if the compiler supports this flag.
        # Some systems, like Windows, do not need this flag. Defaults to ON.
        cmake.definitions["LLVM_ENABLE_PIC"]="ON"

        # Enable unwind tables in the binary.
        # Disabling unwind tables can reduce the size of the libraries.
        # Defaults to ON.
        cmake.definitions["LLVM_ENABLE_UNWIND_TABLES"]="ON"

        # Generate build targets for the LLVM unit tests.
        # Defaults to ON.
        # You can use this option to disable the generation
        # of build targets for the LLVM unit tests.
        cmake.definitions["LLVM_INCLUDE_TESTS"]="OFF"

        # Build LLVM unit tests. Defaults to OFF.
        # Targets for building each unit test are generated in any case.
        # You can build a specific unit test using
        # the targets defined under unittests,
        # such as ADTTests, IRTests, SupportTests, etc.
        # (Search for add_llvm_unittest in the subdirectories of unittests
        # for a complete list of unit tests.)
        # It is possible to build all unit tests with the target UnitTests.
        cmake.definitions["LLVM_BUILD_TESTS"]="OFF"

        cmake.definitions["LLVM_BUILD_EXAMPLES"]="OFF"
        cmake.definitions["LLVM_INCLUDE_EXAMPLES"]="OFF"

        # Adds benchmarks to the list of default targets. Defaults to OFF.
        cmake.definitions["LLVM_BUILD_BENCHMARKS"]="OFF"

        # Generate build targets for the LLVM benchmarks. Defaults to ON.
        cmake.definitions["LLVM_INCLUDE_BENCHMARKS"]="OFF"

        cmake.definitions["LLVM_ENABLE_DOXYGEN"]="OFF"
        cmake.definitions["LLVM_ENABLE_DOXYGEN_QT_HELP"]="OFF"
        cmake.definitions["LLVM_DOXYGEN_SVG"]="OFF"
        cmake.definitions["LLVM_ENABLE_OCAMLDOC"]="OFF"
        cmake.definitions["LLVM_ENABLE_SPHINX"]="OFF"

        # Build LLVM with run-time type information. Defaults to OFF.
        #cmake.definitions["LLVM_ENABLE_RTTI"]="OFF"
        # TODO: make customizable
        cmake.definitions["LLVM_ENABLE_RTTI"]="ON"

        # Enable all compiler warnings. Defaults to ON.
        cmake.definitions["LLVM_ENABLE_WARNINGS"]="ON"

        # Used to decide if LLVM should be built with ABI breaking checks or not.
        # Allowed values are WITH_ASSERTS (default), FORCE_ON and FORCE_OFF.
        # WITH_ASSERTS turns on ABI breaking checks in an assertion enabled build.
        # FORCE_ON (FORCE_OFF) turns them on (off) irrespective
        # of whether normal (NDEBUG-based) assertions are enabled or not.
        # A version of LLVM built with ABI breaking checks is not ABI compatible
        # with a version built without it.
        #cmake.definitions["LLVM_ABI_BREAKING_CHECKS"]="FORCE_ON" \
        #  if len(llvm_sanitizer) > 0 else "WITH_ASSERTS"

        # Whether to build compiler-rt as part of LLVM
        # cmake.definitions["LLVM_TOOL_COMPILER_RT_BUILD"]="ON"

        # TODO: make customizable
        # Whether to build gold as part of LLVM
        #cmake.definitions["LLVM_TOOL_GOLD_BUILD"]="ON"

        # Whether to build libcxxabi as part of LLVM
        #cmake.definitions["LLVM_TOOL_LIBCXXABI_BUILD"]="ON"

        # FIXME: No rule to make target 'projects/libc/src/math/round.o'
        # see https://github.com/fwsGonzo/libriscv/issues/4
        # Whether to build libc as part of LLVM
        #cmake.definitions["LLVM_TOOL_LIBC_BUILD"]="ON"

        # Whether to build libcxx as part of LLVM
        #cmake.definitions["LLVM_TOOL_LIBCXX_BUILD"]="ON"

        # Whether to build libunwind as part of LLVM
        #cmake.definitions["LLVM_TOOL_LIBUNWIND_BUILD"]="ON"

        # sanitizers to build if supported on the target
        # (all;asan;dfsan;msan;hwasan;tsan;safestack;cfi;esan;scudo;ubsan_minimal;gwp_asan)
        cmake.definitions["COMPILER_RT_SANITIZERS_TO_BUILD"]= "asan;msan;tsan;safestack;cfi;esan"

        # TODO: custom C++ stdlib requires custom include paths
        # Default C++ stdlib to use ("libstdc++" or "libc++", empty for platform default
        #cmake.definitions["CLANG_DEFAULT_CXX_STDLIB"]="libc++"
        # Default runtime library to use ("libgcc" or "compiler-rt", empty for platform default)
        #cmake.definitions["CLANG_DEFAULT_RTLIB"]="compiler-rt"
        # Default linker to use (linker name or absolute path, empty for platform default)
        #cmake.definitions["CLANG_DEFAULT_LINKER"]="lld"
        # Use compiler-rt instead of libgcc
        #cmake.definitions["LIBCXX_USE_COMPILER_RT"]="ON"

        # Use compiler-rt instead of libgcc
        # cmake.definitions["LIBUNWIND_USE_COMPILER_RT"]="ON"

        # TODO: make customizable
        # LIBCXXABI_USE_COMPILER_RT

        # TODO: make customizable
        # LIBCXXABI_USE_LLVM_UNWINDER

        # TODO: make customizable
        # Host on which LLVM binaries will run
        #LLVM_HOST_TRIPLE:STRING=x86_64-unknown-linux-gnu

        # TODO: make customizable
        #//Whether to build llc as part of LLVM
        #LLVM_TOOL_LLC_BUILD:BOOL=ON

        # TODO: make customizable
        #//Whether to build lldb as part of LLVM
        #LLVM_TOOL_LLDB_BUILD:BOOL=OFF

        # TODO: make customizable
        #//Whether to build lld as part of LLVM
        #LLVM_TOOL_LLD_BUILD:BOOL=OFF

        # TODO: make customizable
        # Use compiler-rt builtins instead of libgcc
        #COMPILER_RT_USE_BUILTINS_LIBRARY

        # TODO:
        #cmake.definitions["SANITIZER_USE_STATIC_CXX_ABI"]="ON"

        # TODO:
        #cmake.definitions["SANITIZER_USE_STATIC_LLVM_UNWINDER"]="ON"

        # when making a debug or asserts build speed it up by building a release tablegen
        #cmake.definitions["LLVM_OPTIMIZED_TABLEGEN"]="OFF" \
        #  if len(llvm_sanitizer) > 0 else "ON"
        cmake.definitions["LLVM_OPTIMIZED_TABLEGEN"]="ON"

        # TODO
        #cmake.definitions["LLVM_ENABLE_PLUGINS"]="ON"

        # Enables code assertions.
        # Defaults to ON if and only if CMAKE_BUILD_TYPE is Debug.
        cmake.definitions["LLVM_ENABLE_ASSERTIONS"]="ON" \
          if self._lower_build_type == "debug" else "OFF"

        # The CMakeLists.txt file must be in `source_folder`
        cmake.configure(source_folder=llvm_src_dir)

        return cmake

    # Importing files copies files from the local store to your project.
    def imports(self):
        CONAN_IMPORT_PATH = os.getenv("CONAN_IMPORT_PATH", "bin")
        self.output.info("CONAN_IMPORT_PATH is %s" % CONAN_IMPORT_PATH)

    # When building a distribution of a compiler
    # it is generally advised to perform a bootstrap build of the compiler.
    # That means building a stage 1 compiler with your host toolchain,
    # then building the stage 2 compiler using the stage 1 compiler.
    # When performing a bootstrap build it is not beneficial to do anything other
    # than setting CMAKE_BUILD_TYPE to Release for the stage-1 compiler.
    # This is because the more intensive optimizations are expensive to perform
    # and the stage-1 compiler is thrown away.
    # See docs https://llvm.org/docs/AdvancedBuilds.html
    # See docs https://llvm.org/docs/HowToBuildWithPGO.html
    # Multi-stage example https://android.googlesource.com/toolchain/llvm_android/+/bd22d9779676661ae9571972dcd744c42c70ffd0/build.py
    def build(self):
        # don't hang all CPUs and force OS to kill build process
        cpu_count = max(tools.cpu_count() - 2, 1)
        self.output.info('Detected %s CPUs' % (cpu_count))

        # First, we need to build compiler,
        # than we will be able to build runtimes.
        configure_llvm_projects = "clang;clang-tools-extra;libunwind;lld;lldb;libcxx;libcxxabi;compiler-rt"
        #if (self._has_sanitizers):
        #    # we will build `libcxx;libcxxabi;compiler-rt` separately if sanitizer enabled
        #    configure_llvm_projects = "clang;clang-tools-extra;compiler-rt;libunwind;lld;lldb"

        # useful if you run `conan build` multiple times during development
        if os.path.exists("CMakeCache.txt"):
          os.remove("CMakeCache.txt")

        # NOTE: builds `libcxx;libcxxabi;compiler-rt;` separately (for sanitizers support)
        cmake = self._configure_cmake(llvm_projects = configure_llvm_projects, \
            llvm_runtimes = "",
        )

        # see https://fuchsia.googlesource.com/fuchsia/+/HEAD/docs/development/build/toolchain.md
        # -j flag for parallel builds
        cmake.build(args=["--", "-j%s" % cpu_count])
        cmake.install()

        # remove cmake cache of previous build (see above)
        if not os.path.exists("CMakeCache.txt"):
          raise ConanInvalidConfiguration("CMakeCache.txt missing")
        else:
          os.remove("CMakeCache.txt")

        llvm_sanitizer_key = ""
        # We want to enable sanitizers on `libcxx;libcxxabi;compiler-rt`,
        # but NOT on whole LLVM.
        # Sanitizer requires that all program code is instrumented.
        # This also includes any libraries that the program depends on, even libc.
        if self.options.enable_msan:
            # NOTE: force compile `libcxx;libcxxabi;compiler-rt;` with msan
            # NOTE: To build with MSan support you first need to build libc++ with MSan support.
            # MemoryWithOrigins enables both -fsanitize=memory and -fsanitize-memory-track-origins
            # see https://github.com/google/sanitizers/wiki/MemorySanitizer#origins-tracking
            # TODO: use-of-uninitialized-value in llvm-symbolizer
            llvm_sanitizer_key = "MemoryWithOrigins"
            #llvm_sanitizer_key = "Memory"
        elif self.options.enable_asan:
            llvm_sanitizer_key = "Address;Undefined"
        elif self.options.enable_ubsan:
            llvm_sanitizer_key = "Address;Undefined"
        elif self.options.enable_tsan:
            llvm_sanitizer_key = "Thread"

        # Build runtimes separately
        # NOTE: builds `libcxx;libcxxabi;compiler-rt;` separately (for sanitizers support)
        cmake = self._configure_cmake(llvm_projects = "clang;clang-tools-extra;lld", \
            llvm_runtimes = "compiler-rt;libcxx;libcxxabi;libunwind", \
            llvm_sanitizer=llvm_sanitizer_key)

        # NOTE: use uninstrumented llvm-tblgen https://stackoverflow.com/q/56454026
        llvm_tblgen = "{}/bin/llvm-tblgen".format(self.build_folder)
        if not os.path.exists(llvm_tblgen):
            raise Exception("Unable to find path: {}".format(llvm_tblgen))
        # Full path to a native TableGen executable (usually named llvm-tblgen).
        # This is intended for cross-compiling: if the user sets this variable,
        # no native TableGen will be created.
        cmake.definitions["LLVM_TABLEGEN"]=llvm_tblgen

        # llvm_cfg = "{}/bin/llvm-config".format(self.build_folder)
        # if not os.path.exists(llvm_cfg):
        #     raise Exception("Unable to find path: {}".format(llvm_cfg))
        # cmake.definitions['LLVM_CONFIG_PATH'] = llvm_cfg

        #self.prepend_to_definition(cmake, "CMAKE_CXX_FLAGS", "-stdlib=libc++")
        #self.prepend_to_definition(cmake, "CMAKE_EXE_LINKER_FLAGS", "-lc++abi -lunwind -lc++ -lm -lc")

        # -j flag for parallel builds
        cmake.build(args=["--", "-j%s" % cpu_count])
        cmake.install()

        # NOTE: builds before sanitized `libcxx;libcxxabi;compiler-rt;`
        if self.options.include_what_you_use:
            # Using the helper attributes cmake.command_line and cmake.build_config
            # cause cmake.definitions["CMAKE_PREFIX_PATH"] failed
            with tools.chdir(self._iwyu_source_subfolder):
                cmake = CMake(self)
                self.run("cmake -B build -S . %s -DCMAKE_PREFIX_PATH=%s -DIWYU_LLVM_ROOT_PATH=%s" %
                                (cmake.command_line, self.build_folder, self.build_folder))
                with tools.chdir('build'):
                    self.run('cmake --build . %s' % (cmake.build_config))
                    self.run('cmake --build . --target install')

    def package(self):
        # don't hang all CPUs and force OS to kill build process
        cpu_count = max(tools.cpu_count() - 2, 1)
        self.output.info('Detected %s CPUs' % (cpu_count))

        llvm_src_dir = os.path.join(self._llvm_source_subfolder, "llvm")

        package_bin_dir = os.path.join(self.package_folder, "bin")

        if self.options.include_what_you_use:
            iwyu_bin_dir = os.path.join(self._iwyu_source_subfolder, "build", "bin")
            self.output.info('copying %s into %s' % (iwyu_bin_dir, package_bin_dir))
            self.copytree( \
              iwyu_bin_dir, \
              package_bin_dir)

        self.copytree( \
          '{}/bin'.format(self.build_folder), \
          '{}/bin'.format(self.package_folder))

        self.copytree( \
          '{}/libexec'.format(self.build_folder), \
          '{}/libexec'.format(self.package_folder))

        # keep_path=True required by `/include/c++/v1/`
        self.copy('*', src='%s/include' % (self.build_folder), dst='include', keep_path=True)
        self.copytree( \
          '{}/include'.format(self.build_folder), \
          '{}/include'.format(self.package_folder))

        clang_src_dir = os.path.join(self._llvm_source_subfolder, "clang")
        self.copytree( \
          '{}'.format(clang_src_dir), \
          '{}/clang'.format(self.package_folder))

        tools_src_dir = os.path.join(self.build_folder, "tools")
        self.copytree( \
          '{}'.format(tools_src_dir), \
          '{}/tools'.format(self.package_folder))

        # keep_path=True required by `/lib/clang/x.x.x/include/`
        self.copy('*', src='%s/lib' % (self.build_folder), dst='lib', keep_path=True)
        self.copytree( \
          '{}/lib'.format(self.build_folder), \
          '{}/lib'.format(self.package_folder))

        self.output.info('packaged for os: %s' % (self.settings.os_build))

    # NOTE: do not append packaged paths to env_info.PATH, env_info.LD_LIBRARY_PATH, etc.
    # because it can conflict with system compiler
    # https://stackoverflow.com/q/54273632
    def package_info(self):
        self.cpp_info.includedirs = ["include", "clang/include", "tools/clang/include"]
        self.cpp_info.libdirs = ["lib", "clang/lib", "tools/clang/lib"]
        self.cpp_info.bindirs = ["bin", "libexec", "clang", "tools", "tools/clang"]
        #self.env_info.LD_LIBRARY_PATH.append(
        #    os.path.join(self.package_folder, "lib"))
        #self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        #self.env_info.PATH.append(os.path.join(self.package_folder, "libexec"))
        #for libpath in self.deps_cpp_info.lib_paths:
        #    self.env_info.LD_LIBRARY_PATH.append(libpath)

        if self.settings.os_build == "Linux":
            self.cpp_info.libs.extend(["pthread", "unwind", "z", "m", "dl", "ncurses", "tinfo"])
            if self.settings.compiler == "clang" and self._libcxx == "libstdc++":
                self.cpp_info.libs.append("atomic")
        elif self.settings.os_build == "Windows" and self.settings.compiler == "Visual Studio":
            self.cpp_info.libs.extend(["ws2_32", "Iphlpapi", "Crypt32"])

        if (self.settings.os_build == "Linux" and self.settings.compiler == "clang" and
           Version(self.settings.compiler.version.value) == "6" and self._libcxx == "libstdc++") or \
           (self.settings.os_build == "Macos" and self.settings.compiler == "apple-clang" and
           Version(self.settings.compiler.version.value) == "9.0" and self._libcxx == "libc++"):
            self.cpp_info.libs.append("atomic")

        self.cpp_info.includedirs.append(os.path.join(self.package_folder, "include"))
        self.cpp_info.includedirs.append(self.package_folder)

        bindir = os.path.join(self.package_folder, "bin")
        libexec = os.path.join(self.package_folder, "libexec")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        #self.env_info.PATH.append(bindir)
        self.output.info("Appending PATH environment variable: {}".format(libexec))
        #self.env_info.PATH.append(libexec)

        libdir = os.path.join(self.package_folder, "lib")
        self.output.info("Appending PATH environment variable: {}".format(libdir))
        #self.env_info.PATH.append(libdir)

        self.cpp_info.libs += list(\
          dict((key,value) for key, value in self.llvm_libs.items() if value == True).keys()\
        )

        self.output.info("LIBRARIES: %s" % self.cpp_info.libs)
        self.output.info("Package folder: %s" % self.package_folder)
        self.env_info.CONAN_LLVM_TOOLS_ROOT = self.package_folder

    # TODO: clang++ does not depend on arch,
    # but tooling libs depend on arch...
    # You must use same CXX ABI as LLVM libs
    # otherwise you will get link errors!
    def package_id(self):
        self.info.include_build_settings()
        if self.settings.os_build == "Windows":
            del self.info.settings.arch_build # same build is used for x86 and x86_64
        del self.info.settings.arch
        del self.info.settings.compiler
