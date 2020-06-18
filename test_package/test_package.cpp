#include <cstdlib>
#include <iostream>
#include <iterator>
#include <exception>
#include <string>
#include <algorithm>
#include <chrono>
#include <cmath>
#include <memory>
#include <vector>

// __has_include is currently supported by GCC and Clang. However GCC 4.9 may have issues and
// returns 1 for 'defined( __has_include )', while '__has_include' is actually not supported:
// https://gcc.gnu.org/bugzilla/show_bug.cgi?id=63662
#if __has_include(<filesystem>)
#include <filesystem>
#else
#include <experimental/filesystem>
#endif // __has_include

/*
  TODO:
  ~/.conan/data/llvm_tools/master/conan/stable/package/de9a9bb1919df123807ce088d433998bfaaa3c53/lib/libclangTooling.a(CompilationDatabase.cpp.o): In function `clang::tooling::FixedCompilationDatabase::loadFromCommandLine(int&, char const* const*, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >&, llvm::Twine)':
  CompilationDatabase.cpp:(.text._ZN5clang7tooling24FixedCompilationDatabase19loadFromCommandLineERiPKPKcRNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEN4llvm5TwineE+0x259): undefined reference to `clang::TextDiagnosticPrinter::TextDiagnosticPrinter(llvm::raw_ostream&, clang::DiagnosticOptions*, bool)'
  CompilationDatabase.cpp:(.text._ZN5clang7tooling24FixedCompilationDatabase19loadFromCommandLineERiPKPKcRNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEN4llvm5TwineE+0x2b3): undefined reference to `clang::DiagnosticIDs::DiagnosticIDs()'
  CompilationDatabase.cpp:(.text._ZN5clang7tooling24FixedCompilationDatabase19loadFromCommandLineERiPKPKcRNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEN4llvm5TwineE+0x2ee): undefined reference to `clang::DiagnosticsEngine::DiagnosticsEngine(llvm::IntrusiveRefCntPtr<clang::DiagnosticIDs>, llvm::IntrusiveRefCntPtr<clang::DiagnosticOptions>, clang::DiagnosticConsumer*, bool)'
*/
#if 0
#include <clang/Rewrite/Core/Rewriter.h>
#include <clang/ASTMatchers/ASTMatchers.h>
#include <clang/AST/ASTContext.h>
#include <clang/ASTMatchers/ASTMatchFinder.h>
#include <clang/ASTMatchers/ASTMatchersMacros.h>
#include <clang/Frontend/CompilerInstance.h>
#include <clang/Frontend/ASTConsumers.h>
#include <clang/Frontend/FrontendActions.h>
#include <clang/Basic/SourceManager.h>
#include <clang/Tooling/Tooling.h>
#include <clang/Rewrite/Core/Rewriter.h>
#include <clang/Rewrite/Core/Rewriter.h>
#include <clang/ASTMatchers/ASTMatchers.h>
#include <clang/AST/ASTContext.h>
#include <clang/ASTMatchers/ASTMatchFinder.h>
#include <clang/ASTMatchers/ASTMatchersMacros.h>
#include <clang/AST/Type.h>
#include <clang/Frontend/CompilerInstance.h>
#include <clang/Sema/Sema.h>
#include <clang/Basic/FileManager.h>
#include <clang/Basic/LangOptions.h>
#include <clang/Basic/SourceManager.h>
#include <clang/Frontend/CompilerInstance.h>
#include <clang/Sema/Sema.h>
#include <clang/Lex/Lexer.h>
#include <clang/Frontend/FrontendAction.h>
#include <clang/Frontend/ASTConsumers.h>
#include <clang/Frontend/CompilerInstance.h>
#include <clang/Tooling/Tooling.h>
#include <clang/Rewrite/Core/Rewriter.h>
#include <clang/Driver/Options.h>
#include <clang/AST/AST.h>
#include <clang/AST/ASTContext.h>
#include <clang/AST/ASTConsumer.h>
#include <clang/AST/RecursiveASTVisitor.h>
#include <clang/Frontend/ASTConsumers.h>
#include <clang/Frontend/FrontendActions.h>
#include <clang/Frontend/CompilerInstance.h>
#include <clang/Tooling/CommonOptionsParser.h>
#include <clang/Tooling/Tooling.h>
#include <clang/Rewrite/Core/Rewriter.h>
#include <clang/Frontend/CompilerInstance.h>
#include <clang/Sema/Sema.h>
#include <clang/Lex/Lexer.h>
#include <clang/Frontend/FrontendAction.h>
#include <clang/Frontend/ASTConsumers.h>
#include <clang/Frontend/CompilerInstance.h>
#include <clang/Tooling/Tooling.h>
#include <clang/Rewrite/Core/Rewriter.h>
#include <clang/Driver/Options.h>
#include <clang/AST/AST.h>
#include <clang/AST/ASTContext.h>
#include <clang/AST/ASTConsumer.h>
#include <clang/AST/RecursiveASTVisitor.h>
#include <clang/Frontend/ASTConsumers.h>
#include <clang/Frontend/FrontendActions.h>
#include <clang/Frontend/CompilerInstance.h>
#include <clang/Tooling/CommonOptionsParser.h>
#include <clang/Tooling/Tooling.h>
#include <clang/Rewrite/Core/Rewriter.h>
#include <clang/ASTMatchers/ASTMatchers.h>
#include <clang/AST/ASTContext.h>
#include <clang/ASTMatchers/ASTMatchFinder.h>
#include <clang/ASTMatchers/ASTMatchersMacros.h>
#include <clang/Frontend/CompilerInstance.h>
#include <clang/Frontend/ASTConsumers.h>
#include <clang/Frontend/FrontendActions.h>
#include <clang/Basic/SourceManager.h>
#include <clang/Tooling/Tooling.h>
#include <clang/Rewrite/Core/Rewriter.h>
#include <clang/Rewrite/Core/Rewriter.h>
#include <clang/ASTMatchers/ASTMatchers.h>
#include <clang/AST/ASTContext.h>
#include <clang/ASTMatchers/ASTMatchFinder.h>
#include <clang/ASTMatchers/ASTMatchersMacros.h>
#include <clang/AST/Type.h>
#include <clang/Frontend/CompilerInstance.h>
#include <clang/Sema/Sema.h>
#include <clang/Basic/FileManager.h>
#include <clang/Basic/LangOptions.h>
#include <clang/Basic/SourceManager.h>
#include <clang/Frontend/CompilerInstance.h>
#include <clang/Sema/Sema.h>
#include <clang/Lex/Lexer.h>
#include <clang/Frontend/FrontendAction.h>
#include <clang/Frontend/ASTConsumers.h>
#include <clang/Frontend/CompilerInstance.h>
#include <clang/Tooling/Tooling.h>
#include <clang/Rewrite/Core/Rewriter.h>
#include <clang/Driver/Options.h>
#include <clang/AST/AST.h>
#include <clang/AST/ASTContext.h>
#include <clang/AST/ASTConsumer.h>
#include <clang/AST/RecursiveASTVisitor.h>
#include <clang/Frontend/ASTConsumers.h>
#include <clang/Frontend/FrontendActions.h>
#include <clang/Frontend/CompilerInstance.h>
#include <clang/Tooling/CommonOptionsParser.h>
#include <clang/Tooling/Tooling.h>
#include <clang/Rewrite/Core/Rewriter.h>
#include <clang/Frontend/CompilerInstance.h>
#include <clang/Sema/Sema.h>
#include <clang/Lex/Lexer.h>
#include <clang/Frontend/FrontendAction.h>
#include <clang/Frontend/ASTConsumers.h>
#include <clang/Frontend/CompilerInstance.h>
#include <clang/Tooling/Tooling.h>
#include <clang/Rewrite/Core/Rewriter.h>
#include <clang/Driver/Options.h>
#include <clang/AST/AST.h>
#include <clang/AST/ASTContext.h>
#include <clang/AST/ASTConsumer.h>
#include <clang/AST/RecursiveASTVisitor.h>
#include <clang/Frontend/ASTConsumers.h>
#include <clang/Frontend/FrontendActions.h>
#include <clang/Frontend/CompilerInstance.h>
#include <clang/Tooling/CommonOptionsParser.h>
#include <clang/Tooling/Tooling.h>
#include <clang/Rewrite/Core/Rewriter.h>

template<class T>
std::ostream& operator<<(std::ostream& os, const std::vector<T>& v)
{
    copy(v.begin(), v.end(), std::ostream_iterator<T>(os, " "));
    return os;
}


namespace cxxctp {

using MatchResult
  = clang::ast_matchers::MatchFinder::MatchResult;

// Called when the |Match| registered for |clang::AnnotateAttr|
// was successfully found in the AST.
class AnnotateMatchCallback
  : public clang::ast_matchers::MatchFinder::MatchCallback
{
public:
  AnnotateMatchCallback(
    clang::Rewriter &rewriter) {
    /// ...
  }

  void run(const MatchResult& Result) override {
    /// ...
  }

private:
  clang::Rewriter* rewriter_{nullptr};
};

// The ASTConsumer will read AST.
// It provides many interfaces to be overridden when
// certain type of AST node has been parsed,
// or after all the translation unit has been parsed.
class AnnotateConsumer
  : public clang::ASTConsumer
{
public:
  explicit AnnotateConsumer(
    clang::Rewriter &Rewriter) {
    /// ...
  }

  ~AnnotateConsumer() override = default;

  // HandleTranslationUnit() called only after
  // the entire source file is parsed.
  // Translation unit effectively represents an entire source file.
  void HandleTranslationUnit(clang::ASTContext &Context) override {
    /// ...
  }

private:
  clang::ast_matchers::MatchFinder matchFinder;
};

// We choose an ASTFrontendAction because we want to analyze
// the AST representation of the source code
class AnnotationMatchAction
  : public clang::ASTFrontendAction
{
public:
  using ASTConsumerPointer = std::unique_ptr<clang::ASTConsumer>;

  explicit AnnotationMatchAction() {
    /// ...
  }

  ASTConsumerPointer CreateASTConsumer(
    // pass a pointer to the CompilerInstance because
    // it contains a lot of contextual information
    clang::CompilerInstance&
    , llvm::StringRef filename) override;

  bool BeginSourceFileAction(
    // pass a pointer to the CompilerInstance because
    // it contains a lot of contextual information
    clang::CompilerInstance&) override {
    /// ...
    return true;
  }

  void EndSourceFileAction() override {
    /// ...
  }

private:
  // Rewriter lets you make textual changes to the source code
  clang::Rewriter rewriter_;
};

// frontend action will only consume AST and find all declarations
struct AnnotationMatchFactory
  : public clang::tooling::FrontendActionFactory
{
  AnnotationMatchFactory();

  std::unique_ptr<clang::FrontendAction> create() override {
    /// ...
  }
};

} // namespace cxxctp
#endif // 0

int main(int argc, char* argv[])
{
/*
  std::vector< const char* > args_vec{"clang_app", "-extra-arg=-DCLANG_ENABLED=1", "-help"};

  int args_arc = args_vec.size();

  const char **args_argv = &(args_vec[0]);

  TODO:
  ~/.conan/data/llvm_tools/master/conan/stable/package/de9a9bb1919df123807ce088d433998bfaaa3c53/lib/libclangTooling.a(CompilationDatabase.cpp.o): In function `clang::tooling::FixedCompilationDatabase::loadFromCommandLine(int&, char const* const*, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >&, llvm::Twine)':
  CompilationDatabase.cpp:(.text._ZN5clang7tooling24FixedCompilationDatabase19loadFromCommandLineERiPKPKcRNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEN4llvm5TwineE+0x259): undefined reference to `clang::TextDiagnosticPrinter::TextDiagnosticPrinter(llvm::raw_ostream&, clang::DiagnosticOptions*, bool)'
  CompilationDatabase.cpp:(.text._ZN5clang7tooling24FixedCompilationDatabase19loadFromCommandLineERiPKPKcRNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEN4llvm5TwineE+0x2b3): undefined reference to `clang::DiagnosticIDs::DiagnosticIDs()'
  CompilationDatabase.cpp:(.text._ZN5clang7tooling24FixedCompilationDatabase19loadFromCommandLineERiPKPKcRNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEN4llvm5TwineE+0x2ee): undefined reference to `clang::DiagnosticsEngine::DiagnosticsEngine(llvm::IntrusiveRefCntPtr<clang::DiagnosticIDs>, llvm::IntrusiveRefCntPtr<clang::DiagnosticOptions>, clang::DiagnosticConsumer*, bool)'
*/
#if 0
  // see http://llvm.org/docs/doxygen/html/classllvm_1_1cl_1_1OptionCategory.html
  llvm::cl::OptionCategory UseOverrideCategory("Use override options");

  // parse the command-line args passed to your code
  // see http://clang.llvm.org/doxygen/classclang_1_1tooling_1_1CommonOptionsParser.html
  clang::tooling::CommonOptionsParser op(args_arc, args_argv,
    UseOverrideCategory);
#endif // 0

  return EXIT_SUCCESS;
}
