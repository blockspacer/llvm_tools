import os, re, stat, fnmatch, platform, glob, traceback, shutil
from conans import ConanFile, CMake, tools
from conans.tools import Version
from conans.errors import ConanInvalidConfiguration
from conans.model.version import Version

class LLVMToolsConan(ConanFile):
    name = "llvm_tools"

    version = "master"
    # TODO: llvmorg-9.0.1
    llvm_version = "release/10.x"
    iwyu_version = "clang_10"

    description = "conan package for LLVM TOOLS"
    topics = ("c++", "conan", "clang", "include-what-you-use", "llvm", "iwyu")
    #url = "https://github.com/bincrafters/conan-folly" # TODO
    #homepage = "https://github.com/facebook/folly" # TODO
    #license = "Apache-2.0" # TODO

    # Constrains build_type inside a recipe to Release!
    settings = {"os", "build_type", "compiler", "arch"}

    options = {
        # hack (forcing -m64)
        # sanitizer_allocator.cpp.o' is incompatible with i386:x86-64 output
        # see https://bugs.llvm.org/show_bug.cgi?id=42463
        "force_x86_64": [True, False],
        "link_ltinfo": [True, False],
        "include_what_you_use": [True, False],
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
                       "scripts/*"]

    generators = 'cmake_find_package', "cmake", "cmake_paths"

    llvm_repo_url = "https://github.com/llvm/llvm-project.git"
    iwyu_repo_url = "https://github.com/include-what-you-use/include-what-you-use.git"

    llvm_libs = {
        'LLVMCore': 0,
        'LLVMAnalysis': 0,
        'LLVMSupport': 0,
        'LLVMipo': 0,
        'LLVMIRReader': 0,
        'LLVMBinaryFormat': 0,
        'LLVMBitReader': 0,
        'LLVMBitWriter': 0,
        'LLVMMC': 0,
        'LLVMMCParser': 0,
        'LLVMTransformUtils': 0,
        'LLVMScalarOpts': 0,
        'LLVMLTO': 0,
        'LLVMCoroutines': 0,
        'LLVMCoverage': 0,
        'LLVMInstCombine': 0,
        'LLVMInstrumentation': 0,
        'LLVMLinker': 0,
        'LLVMObjCARCOpts': 0,
        'LLVMObject': 0,
        'LLVMPasses': 0,
        'LLVMProfileData': 0,
        'LLVMTarget': 0,
        'LLVMLibDriver': 0,
        'LLVMLineEditor': 0,
        'LLVMMIRParser': 0,
        'LLVMOption': 0,
        'LLVMRuntimeDyld': 0,
        'LLVMSelectionDAG': 0,
        'LLVMSymbolize': 0,
        'LLVMTableGen': 0,
        'LLVMVectorize': 0,
        'clangARCMigrate': 0,
        'clangAnalysis': 0,
        'clangAST': 0,
        'clangASTMatchers': 0,
        'clangBasic': 0,
        'clangCodeGen': 0,
        'clangDriver': 0,
        'clangDynamicASTMatchers': 0,
        'clangEdit': 0,
        'clangFormat': 0,
        'clangFrontend': 0,
        'clangFrontendTool': 0,
        'clangIndex': 0,
        'clangLex': 0,
        'clangParse': 0,
        'clangRewrite': 0,
        'clangRewriteFrontend': 0,
        'clangSema': 0,
        'clangSerialization': 0,
        'clangStaticAnalyzerCheckers': 0,
        'clangStaticAnalyzerCore': 0,
        'clangStaticAnalyzerFrontend': 0,
        'clangTooling': 0,
        'clangToolingCore': 0,
        'clangToolingRefactoring': 0,
        'clangStaticAnalyzerCore': 0,
        'clangDynamicASTMatchers': 0,
        'clangCodeGen': 0,
        'clangFrontendTool': 0,
        'clang': 0,
        'clangEdit': 0,
        'clangRewriteFrontend': 0,
        'clangDriver': 0,
        'clangSema': 0,
        'clangASTMatchers': 0,
        'clangSerialization': 0,
        'clangBasic': 0,
        'clangAST': 0,
        'clangTooling': 0,
        'clangStaticAnalyzerFrontend': 0,
        'clangFormat': 0,
        'clangLex': 0,
        'clangFrontend': 0,
        'clangRewrite': 0,
        'clangToolingCore': 0,
        'clangIndex': 0,
        'clangAnalysis': 0,
        'clangParse': 0,
        'clangStaticAnalyzerCheckers': 0,
        'clangARCMigrate': 0,
    }

    @property
    def _llvm_source_subfolder(self):
        return "llvm_project"

    @property
    def _iwyu_source_subfolder(self):
        return "iwyu"

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
        if self.options.include_what_you_use \
            and not self.options.enable_msan \
            and not self.options.enable_tsan \
            and not self.options.enable_ubsan \
            and not self.options.enable_asan:
            self.run('git clone -b {} --progress --depth 100 --recursive --recurse-submodules {} {}'.format(self.iwyu_version, self.iwyu_repo_url, self._iwyu_source_subfolder))

    def _configure_cmake(self, llvm_projects, llvm_runtimes, llvm_sanitizer=""):
        self.output.info('configuring LLVM')

        llvm_src_dir = os.path.join(self._llvm_source_subfolder, "llvm")
        self.output.info('llvm_src_dir is {}'.format(llvm_src_dir))

        cmake = CMake(self, set_cmake_flags=True)
        cmake.verbose = True

        # don't hang all CPUs and force OS to kill build process
        cpu_count = max(tools.cpu_count() - 3, 1)
        self.output.info('Detected %s CPUs' % (cpu_count))

        # Semicolon-separated list of projects to build (clang;clang-tools-extra;compiler-rt;debuginfo-tests;libc;libclc;libcxx;libcxxabi;libunwind;lld;lldb;llgo;mlir;openmp;parallel-libs;polly;pstl), or "all".
        cmake.definitions["LLVM_ENABLE_PROJECTS"]=llvm_projects

        # see Building LLVM with CMake https://llvm.org/docs/CMake.html
        cmake.definitions["LLVM_PARALLEL_COMPILE_JOBS"]=cpu_count
        cmake.definitions["LLVM_COMPILER_JOBS"]=cpu_count
        cmake.definitions["LLVM_PARALLEL_LINK_JOBS"]=1
        #cmake.definitions["LLVM_LINK_LLVM_DYLIB"]=1

        # This should speed up building debug builds
        # see https://www.productive-cpp.com/improving-cpp-builds-with-split-dwarf/
        #cmake.definitions["LLVM_USE_SPLIT_DWARF"]="ON"

        # force Release build
        #cmake.definitions["CMAKE_BUILD_TYPE"]="Release"

        if self.options.link_ltinfo:
            # https://github.com/MaskRay/ccls/issues/556
            cmake.definitions["CMAKE_CXX_LINKER_FLAGS"]="-ltinfo"

        # Semicolon-separated list of runtimes to build (libcxx;libcxxabi;libunwind;compiler-rt), or "all".
        cmake.definitions["LLVM_ENABLE_RUNTIMES"]=llvm_runtimes

        if len(llvm_sanitizer) > 0:
            cmake.definitions["LLVM_USE_SANITIZER"]=llvm_sanitizer
            self.output.info('LLVM_USE_SANITIZER = {}'.format(llvm_sanitizer))
            #
            # see libcxx in LLVM_ENABLE_PROJECTS
            # compile using libc++ instead of the system default
            #cmake.definitions["LLVM_ENABLE_LIBCXX"]="ON"
            #
            # see lld in LLVM_ENABLE_PROJECTS
            # This option is equivalent to -DLLVM_USE_LINKER=lld, except during a 2-stage build where a dependency is added from the first stage to the second ensuring that lld is built before stage2 begins.
            #cmake.definitions["LLVM_ENABLE_LLD"]="ON"
            #
            # Add -flto or -flto= flags to the compile and link command lines, enabling link-time optimization. Possible values are Off, On, Thin and Full. Defaults to OFF.
            # TODO: BUG when LTO ON: https://bugs.gentoo.org/show_bug.cgi?format=multiple&id=667108
            #cmake.definitions["LLVM_ENABLE_LTO"]="ON"

            # TODO
            # LLVM_USE_LINKER

            #
            # sanitizer needs only libc++ and libc++abi
            cmake.definitions["LLVM_BUILD_TOOLS"]="OFF"
            cmake.definitions["LLVM_TOOL_CLANG_TOOLS_EXTRA_BUILD"]="OFF"
            cmake.definitions["CLANG_ENABLE_STATIC_ANALYZER"]="OFF"
            cmake.definitions["CLANG_TOOL_CLANG_CHECK_BUILD"]="OFF"
            cmake.definitions["CLANG_PLUGIN_SUPPORT"]="OFF"
            cmake.definitions["CLANG_TOOL_CLANG_FORMAT_BUILD"]="OFF"
            cmake.definitions["CLANG_ENABLE_FORMAT"]="OFF"
            cmake.definitions["CLANG_TOOL_CLANG_FUZZER_BUILD"]="OFF"

            cmake.definitions["LLVM_BUILD_RUNTIME"]="ON"
            cmake.definitions["LLVM_BUILD_RUNTIMES"]="ON"

            cmake.definitions["LLVM_BUILD_UTILS"]="ON"


            # LLVM_BUILD_EXTERNAL_COMPILER_RT:BOOL

            # Build LLVM and tools with PGO instrumentation
            # LLVM_BUILD_INSTRUMENTED

            # use uninstrumented llvm-tblgen
            # see https://stackoverflow.com/questions/56454026/building-libc-with-memorysanitizer-instrumentation-fails-due-to-memorysanitize
            llvm_tblgen=os.path.join(self.package_folder, "bin", "llvm-tblgen")
            cmake.definitions["LLVM_TABLEGEN"]="{}".format(llvm_tblgen)
            if not os.path.exists(llvm_tblgen):
                raise Exception("Unable to find path: {}".format(llvm_tblgen))
        else:
            cmake.definitions["LLVM_BUILD_TOOLS"]="ON"
            cmake.definitions["LLVM_TOOL_CLANG_TOOLS_EXTRA_BUILD"]="ON"
            cmake.definitions["CLANG_ENABLE_STATIC_ANALYZER"]="ON"
            cmake.definitions["CLANG_TOOL_CLANG_CHECK_BUILD"]="ON"
            cmake.definitions["CLANG_PLUGIN_SUPPORT"]="ON"
            cmake.definitions["CLANG_TOOL_CLANG_FORMAT_BUILD"]="ON"
            cmake.definitions["CLANG_ENABLE_FORMAT"]="ON"
            cmake.definitions["CLANG_TOOL_CLANG_FUZZER_BUILD"]="ON"
            # LLVM_USE_SANITIZER Defaults to empty string.
            cmake.definitions["LLVM_USE_SANITIZER"]=""

        # NOTE: msan build requires
        # existing file ~/.conan/data/llvm_tools/master/conan/stable/package/.../lib/clang/10.0.1/lib/linux/libclang_rt.msan_cxx-x86_64.a
        # same for tsan\ubsan\asan\etc.
        cmake.definitions["COMPILER_RT_BUILD_SANITIZERS"]="ON"

        #cmake.definitions["CMAKE_CXX_STANDARD"]="17"
        cmake.definitions["BUILD_SHARED_LIBS"]="OFF"
        #cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"]="ON"
        cmake.definitions["BUILD_TESTS"]="OFF"

        # If disabled, do not try to build the OCaml and go bindings.
        cmake.definitions["LLVM_ENABLE_BINDINGS"]="OFF"

        # Install symlinks from the binutils tool names to the corresponding LLVM tools. For example, ar will be symlinked to llvm-ar.
        #cmake.definitions["LLVM_INSTALL_BINUTILS_SYMLINKS"]="ON"

        #cmake.definitions["LLVM_INSTALL_CCTOOLS_SYMLINKS"]="ON"

        # hack (forcing -m64)
        # sanitizer_allocator.cpp.o' is incompatible with i386:x86-64 output
        # see https://bugs.llvm.org/show_bug.cgi?id=42463
        if self.options.force_x86_64:
            # breaks find for LLVMConfig.cmake
            #cmake.definitions["LLVM_LIBDIR_SUFFIX"]="64"

            cmake.definitions["CMAKE_C_FLAGS"]="-m64"
            cmake.definitions["CMAKE_CXX_FLAGS"]="-m64"
            cmake.definitions["CMAKE_EXE_LINKER_FLAGS"]="-m64"
            cmake.definitions["CMAKE_MODULE_LINKER_FLAGS"]="-m64"
            cmake.definitions["CMAKE_SHARED_LINKER_FLAGS"]="-m64"
            cmake.definitions["LLVM_BUILD_32_BITS"]="OFF"
            #cmake.definitions["LLVM_BUILD_32_BITS"]="ON"
            # LLVM target to use for native code generation. This is required for JIT generation. It defaults to “host”, meaning that it shall pick the architecture of the machine where LLVM is being built. If you are cross-compiling, set it to the target architecture name.
            cmake.definitions["LLVM_TARGET_ARCH"]="x86_64"
            #cmake.definitions["LLVM_TARGET_ARCH"]="x86"
            # Semicolon-separated list of targets to build, or all for building all targets. Case-sensitive. Defaults to all. Example: -DLLVM_TARGETS_TO_BUILD="X86;PowerPC".
            #cmake.definitions["LLVM_TARGETS_TO_BUILD"]="x86"
            # Default triple for which compiler-rt runtimes will be built.
            cmake.definitions["COMPILER_RT_DEFAULT_TARGET_TRIPLE"]="x86_64-unknown-linux-gnu"
            # Default target for which LLVM will generate code.
            cmake.definitions["LLVM_DEFAULT_TARGET_TRIPLE"]="x86_64-unknown-linux-gnu"

        #cmake.definitions["PYTHON_EXECUTABLE"]=""

        cmake.definitions["LLVM_INCLUDE_TESTS"]="OFF"
        cmake.definitions["LLVM_BUILD_TESTS"]="OFF"
        cmake.definitions["LLVM_BUILD_EXAMPLES"]="OFF"
        cmake.definitions["LLVM_INCLUDE_EXAMPLES"]="OFF"
        cmake.definitions["LLVM_BUILD_BENCHMARKS"]="OFF"
        cmake.definitions["LLVM_INCLUDE_BENCHMARKS"]="OFF"
        cmake.definitions["LLVM_ENABLE_DOXYGEN"]="OFF"
        cmake.definitions["LLVM_ENABLE_OCAMLDOC"]="OFF"
        cmake.definitions["LLVM_ENABLE_SPHINX"]="OFF"
        cmake.definitions["LLVM_ENABLE_RTTI"]="OFF"
        #cmake.definitions["LLVM_ENABLE_RTTI"]="ON"

        # Whether to build compiler-rt as part of LLVM
        cmake.definitions["LLVM_TOOL_COMPILER_RT_BUILD"]="ON"

        # TODO
        # Whether to build gold as part of LLVM
        cmake.definitions["LLVM_TOOL_GOLD_BUILD"]="ON"

        # Whether to build libcxxabi as part of LLVM
        cmake.definitions["LLVM_TOOL_LIBCXXABI_BUILD"]="ON"

        # Whether to build libcxx as part of LLVM
        cmake.definitions["LLVM_TOOL_LIBCXX_BUILD"]="ON"

        # Whether to build libunwind as part of LLVM
        cmake.definitions["LLVM_TOOL_LIBUNWIND_BUILD"]="ON"

        # sanitizers to build if supported on the target (all;asan;dfsan;msan;tsan;safestack;cfi;esan;scudo)
        cmake.definitions["COMPILER_RT_SANITIZERS_TO_BUILD"]="asan;msan;tsan;safestack;cfi;esan"

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

        # LIBCXXABI_USE_COMPILER_RT

        # LIBCXXABI_USE_LLVM_UNWINDER

        # Host on which LLVM binaries will run
        #LLVM_HOST_TRIPLE:STRING=x86_64-unknown-linux-gnu

        #//Whether to build llc as part of LLVM
        #LLVM_TOOL_LLC_BUILD:BOOL=ON

        #//Whether to build lldb as part of LLVM
        #LLVM_TOOL_LLDB_BUILD:BOOL=OFF

        #//Whether to build lld as part of LLVM
        #LLVM_TOOL_LLD_BUILD:BOOL=OFF

        #COMPILER_RT_USE_BUILTINS_LIBRARY

        # when making a debug or asserts build speed it up by building a release tablegen
        cmake.definitions["LLVM_OPTIMIZED_TABLEGEN"]="ON"

        cmake.definitions["LVM_ENABLE_PLUGINS"]="ON"

        cmake.definitions["LLVM_ENABLE_ASSERTIONS"]="OFF"

        # The CMakeLists.txt file must be in `source_folder`
        cmake.configure(source_folder=llvm_src_dir)

        return cmake

    # TODO: remove
    #def _configure_cmake_iwyu(self, llvm_src_dir):
    #    self.output.info('configuring IWYU')
    #    self.output.info('os.getcwd() %s' % (os.getcwd()))

    #    cmake = CMake(self, set_cmake_flags=True)
    #    cmake.verbose = True

    #    # don't hang all CPUs and force OS to kill build process
    #    cpu_count = max(tools.cpu_count() - 3, 1)
    #    self.output.info('Detected %s CPUs' % (cpu_count))

    #    #cmake.definitions["IWYU_LLVM_ROOT_PATH"]=llvm_src_dir
    #    #cmake.definitions["CMAKE_PREFIX_PATH"]=llvm_src_dir

    #    cmake.definitions["IWYU_LLVM_ROOT_PATH"]=self.build_folder
    #    cmake.definitions["CMAKE_PREFIX_PATH"]=self.build_folder
    #    cmake.definitions["CMAKE_MODULE_PATH"]=self.build_folder
    #    self.output.info('IWYU_LLVM_ROOT_PATH %s' % (cmake.definitions#["IWYU_LLVM_ROOT_PATH"]))
    #    self.output.info('CMAKE_PREFIX_PATH %s' % (cmake.definitions#["CMAKE_PREFIX_PATH"]))
    #    self.output.info('CMAKE_MODULE_PATH %s' % (cmake.definitions#["CMAKE_MODULE_PATH"]))

    #    # The CMakeLists.txt file must be in `source_folder`
    #    cmake.configure(source_folder=self._iwyu_source_subfolder, #build_folder=self._iwyu_source_subfolder)

    #    return cmake

    # Importing files copies files from the local store to your project.
    def imports(self):
        dest = os.getenv("CONAN_IMPORT_PATH", "bin")
        self.output.info("CONAN_IMPORT_PATH is %s" % CONAN_IMPORT_PATH)

    def build(self):
        # don't hang all CPUs and force OS to kill build process
        cpu_count = max(tools.cpu_count() - 2, 1)
        self.output.info('Detected %s CPUs' % (cpu_count))

        configure_llvm_projects = "clang;clang-tools-extra;libunwind;lld;lldb;libcxx;libcxxabi;compiler-rt"
        if self.options.enable_msan:
            # we will build `libcxx;libcxxabi;compiler-rt` separately if sanitizer enabled
            configure_llvm_projects = "clang;clang-tools-extra;compiler-rt;libunwind;lld;lldb"

        # NOTE: builds `libcxx;libcxxabi;compiler-rt;` separately (for sanitizers support)
        # TODO: libc;
        cmake = self._configure_cmake(llvm_projects = configure_llvm_projects, \
            #llvm_runtimes = "compiler-rt;libunwind" \
            llvm_runtimes = "",
        )
        # -j flag for parallel builds
        cmake.build(args=["--", "-j%s" % cpu_count])
        cmake.install()

        if self.options.enable_msan:
            # NOTE: force compile `libcxx;libcxxabi;compiler-rt;` with msan
            # NOTE: To build with MSan support you first need to build libc++ with MSan support.
            # MemoryWithOrigins enables both -fsanitize=memory and -fsanitize-memory-track-origins
            # see https://github.com/google/sanitizers/wiki/MemorySanitizer#origins-tracking
            llvm_sanitizer_key = "MemoryWithOrigins" # TODO: Address;Undefined support
        elif self.options.enable_asan:
            llvm_sanitizer_key = "Address;Undefined"
        elif self.options.enable_ubsan:
            llvm_sanitizer_key = "Address;Undefined"
        elif self.options.enable_tsan:
            llvm_sanitizer_key = "Thread"

        # required for builds with `-stdlib=libc++ -lc++abi`
        if (self.options.enable_msan \
            or self.options.enable_asan \
            or self.options.enable_ubsan \
            or self.options.enable_tsan):
            # NOTE: builds `libcxx;libcxxabi;compiler-rt;` separately (for sanitizers support)
            # NOTE: use uninstrumented llvm-tblgen https://stackoverflow.com/q/56454026
            cmake = self._configure_cmake(llvm_projects = "libcxx;libcxxabi;compiler-rt", \
                #llvm_runtimes = "compiler-rt;libcxx;libcxxabi", \
                llvm_runtimes = "", \
                llvm_sanitizer=llvm_sanitizer_key)

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

    # https://stackoverflow.com/a/13814557
    def copytree(self, src, dst, symlinks=False, ignore=None, verbose=False):
        if not os.path.exists(dst):
            os.makedirs(dst)
        ignore_list = ['.travis.yml', '.git']
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

    def package(self):
        self.output.info('self.settings.os: %s' % (self.settings.os))
        self.output.info('self.settings.build_type: %s' % (self.settings.build_type))

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

        # keep_path=True required by `/include/c++/v1/`
        self.copytree( \
          '{}/include'.format(self.build_folder), \
          '{}/include'.format(self.package_folder))

        # keep_path=True required by `/lib/clang/10.0.1/include/`
        self.copytree( \
          '{}/lib'.format(self.build_folder), \
          '{}/lib'.format(self.package_folder))

    def package_info(self):
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.bindirs = ["bin", "libexec"]
        self.env_info.LD_LIBRARY_PATH.append(
            os.path.join(self.package_folder, "lib"))
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.env_info.PATH.append(os.path.join(self.package_folder, "libexec"))
        for libpath in self.deps_cpp_info.lib_paths:
            self.env_info.LD_LIBRARY_PATH.append(libpath)

        if self.settings.os == "Linux":
            self.cpp_info.libs.extend(["pthread", "m", "dl"])
            if self.settings.compiler == "clang" and self.settings.compiler.libcxx == "libstdc++":
                self.cpp_info.libs.append("atomic")
        elif self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            self.cpp_info.libs.extend(["ws2_32", "Iphlpapi", "Crypt32"])

        if (self.settings.os == "Linux" and self.settings.compiler == "clang" and
           Version(self.settings.compiler.version.value) == "6" and self.settings.compiler.libcxx == "libstdc++") or \
           (self.settings.os == "Macos" and self.settings.compiler == "apple-clang" and
           Version(self.settings.compiler.version.value) == "9.0" and self.settings.compiler.libcxx == "libc++"):
            self.cpp_info.libs.append("atomic")

        self.cpp_info.includedirs.append(os.path.join(self.package_folder, "include"))
        self.cpp_info.includedirs.append(self.package_folder)

        bindir = os.path.join(self.package_folder, "bin")
        libexec = os.path.join(self.package_folder, "libexec")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)
        self.output.info("Appending PATH environment variable: {}".format(libexec))
        self.env_info.PATH.append(libexec)

        libdir = os.path.join(self.package_folder, "lib")
        self.output.info("Appending PATH environment variable: {}".format(libdir))
        self.env_info.PATH.append(libdir)

        self.cpp_info.libs += list(self.llvm_libs.keys())

        self.output.info("LIBRARIES: %s" % self.cpp_info.libs)
        self.output.info("Package folder: %s" % self.package_folder)
        self.env_info.CONAN_LLVM_TOOLS_ROOT = self.package_folder
