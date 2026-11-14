# 70 Comprehensive C++ Test Cases & Benchmarks
### Project: SecAICodeTutor - Intelligent Secure Code Analyzer & Tutor

This suite contains exactly **70 curated C++ test cases** covering every facet of modern compiler diagnostics, static code analysis (SAST), semantic verification, and algorithmic complexity evaluation.

## Category Breakdown

| Category | Range | Count | Key Focus |
|---|---|---|---|
| **Syntax & Punctuation** | TC01 – TC15 | 15 | Semicolons, braces `{}`, parens `()`, string literals, dangling tokens |
| **Control Flow & Loops** | TC16 – TC25 | 10 | If/else, while, for loops, switch-case constructs, break keywords |
| **Declarations & Types** | TC26 – TC40 | 15 | Lvalues, duplicate types, array brackets, function bodies, namespaces |
| **Semantics & Scope** | TC41 – TC50 | 10 | Undeclared IDs, scope boundaries, uninitialized variables, type mismatches |
| **Cybersecurity & Threats** | TC51 – TC60 | 10 | CWE-120, CWE-121, CWE-134, CWE-401, CWE-835, CWE-416, CWE-476 |
| **Complexity & Optimization** | TC61 – TC70 | 10 | O(n²) loops, std::endl vs '\n', vector reserve, Fibonacci recursion |

## Complete Test Case Index

| ID | File Name | Category | Target Class | Severity | Description |
|---|---|---|---|---|---|
| TC01 | `tc01_missing_semicolon_var.cpp` | Syntax & Punctuation | `MISSING_SEMICOLON` | HIGH | Missing semicolon at the end of a variable declaration statement |
| TC02 | `tc02_missing_semicolon_return.cpp` | Syntax & Punctuation | `MISSING_SEMICOLON` | HIGH | Missing semicolon after the return statement in function |
| TC03 | `tc03_missing_semicolon_assignment.cpp` | Syntax & Punctuation | `MISSING_SEMICOLON` | HIGH | Missing semicolon after arithmetic assignment expression |
| TC04 | `tc04_missing_semicolon_call.cpp` | Syntax & Punctuation | `MISSING_SEMICOLON` | HIGH | Missing semicolon after function call statement |
| TC05 | `tc05_missing_semicolon_struct.cpp` | Syntax & Punctuation | `MISSING_SEMICOLON` | HIGH | Missing semicolon after struct declaration closing brace |
| TC06 | `tc06_unmatched_brace_open.cpp` | Syntax & Punctuation | `UNMATCHED_BRACE` | HIGH | Unmatched opening brace; missing function closing curly brace |
| TC07 | `tc07_unmatched_brace_extra_close.cpp` | Syntax & Punctuation | `UNMATCHED_BRACE` | HIGH | Extra closing curly brace with no matching opening brace |
| TC08 | `tc08_unmatched_brace_if_block.cpp` | Syntax & Punctuation | `UNMATCHED_BRACE` | HIGH | Unmatched brace inside nested if-condition block |
| TC09 | `tc09_unmatched_brace_loop.cpp` | Syntax & Punctuation | `UNMATCHED_BRACE` | HIGH | Unmatched brace in while loop body |
| TC10 | `tc10_unmatched_paren_if.cpp` | Syntax & Punctuation | `UNMATCHED_PARANTHESES` | HIGH | Unmatched opening parenthesis in conditional evaluation |
| TC11 | `tc11_unmatched_paren_expr.cpp` | Syntax & Punctuation | `UNMATCHED_PARANTHESES` | HIGH | Unmatched extra closing parenthesis in arithmetic expression |
| TC12 | `tc12_unterminated_string_basic.cpp` | Syntax & Punctuation | `UNTERMINATED_STRING` | CRITICAL | String literal opened with double quotes but never closed |
| TC13 | `tc13_unterminated_string_cout.cpp` | Syntax & Punctuation | `UNTERMINATED_STRING` | CRITICAL | Unterminated string literal in streaming output operator |
| TC14 | `tc14_extra_tokens_stray.cpp` | Syntax & Punctuation | `EXTRA_TOKENS` | MEDIUM | Extra stray identifier token following a valid statement |
| TC15 | `tc15_dangling_operator.cpp` | Syntax & Punctuation | `EXTRA_TOKENS` | HIGH | Dangling binary operator missing its right-hand operand |
| TC16 | `tc16_invalid_conditional_if.cpp` | Control Flow & Loops | `INVALID_CONDITIONAL` | HIGH | If statement missing enclosing condition parentheses |
| TC17 | `tc17_orphan_else_no_if.cpp` | Control Flow & Loops | `MISPLACED_KEYWORD` | HIGH | Orphan else branch without a preceding if statement |
| TC18 | `tc18_invalid_while_loop.cpp` | Control Flow & Loops | `INVALID_LOOP` | HIGH | While loop missing enclosing condition parentheses |
| TC19 | `tc19_invalid_for_loop_header.cpp` | Control Flow & Loops | `INVALID_LOOP` | HIGH | For loop missing enclosing parentheses around loop header |
| TC20 | `tc20_for_loop_comma_separated.cpp` | Control Flow & Loops | `INVALID_LOOP` | HIGH | For loop using commas instead of semicolons in loop header |
| TC21 | `tc21_invalid_switch_no_paren.cpp` | Control Flow & Loops | `INVALID_SWITCH` | HIGH | Switch statement missing parentheses around switch variable |
| TC22 | `tc22_switch_case_missing_colon.cpp` | Control Flow & Loops | `INVALID_SWITCH` | HIGH | Switch case label missing the required colon delimiter |
| TC23 | `tc23_switch_duplicate_default.cpp` | Control Flow & Loops | `INVALID_SWITCH` | MEDIUM | Multiple default labels inside a single switch statement |
| TC24 | `tc24_do_while_missing_semicolon.cpp` | Control Flow & Loops | `MISSING_SEMICOLON` | HIGH | Do-while loop statement missing the required terminal semicolon |
| TC25 | `tc25_break_outside_loop.cpp` | Control Flow & Loops | `MISPLACED_KEYWORD` | HIGH | Break statement used outside of any loop or switch construct |
| TC26 | `tc26_invalid_assignment_literal_lhs.cpp` | Declarations & Types | `INVALID_ASSIGNMENT` | HIGH | Literal constant assigned as left-hand side lvalue |
| TC27 | `tc27_invalid_assignment_expression_lhs.cpp` | Declarations & Types | `INVALID_ASSIGNMENT` | HIGH | Expression assigned as left-hand side lvalue |
| TC28 | `tc28_duplicate_type_specifier.cpp` | Declarations & Types | `INVALID_TYPE` | HIGH | Duplicate type keyword in variable declaration |
| TC29 | `tc29_conflicting_type_specifiers.cpp` | Declarations & Types | `INVALID_TYPE` | HIGH | Two conflicting primitive type specifiers in single declaration |
| TC30 | `tc30_missing_identifier_declaration.cpp` | Declarations & Types | `INVALID_DECLARATION` | HIGH | Variable declaration missing identifier name before assignment |
| TC31 | `tc31_invalid_array_decl_unclosed_bracket.cpp` | Declarations & Types | `INVALID_ARRAY_DECL` | HIGH | Array declaration missing closing square bracket |
| TC32 | `tc32_array_negative_size.cpp` | Declarations & Types | `INVALID_ARRAY_DECL` | HIGH | Array declared with an illegal negative dimension size |
| TC33 | `tc33_invalid_function_decl_no_body.cpp` | Declarations & Types | `INVALID_FUNCTION_DECL` | HIGH | Function definition missing required enclosing curly braces |
| TC34 | `tc34_function_param_missing_type.cpp` | Declarations & Types | `INVALID_FUNCTION_DECL` | HIGH | Function parameter missing its type specifier |
| TC35 | `tc35_misplaced_keyword_in_expr.cpp` | Declarations & Types | `MISPLACED_KEYWORD` | HIGH | Return keyword misplaced inside an assignment expression |
| TC36 | `tc36_misplaced_keyword_if_in_return.cpp` | Declarations & Types | `MISPLACED_KEYWORD` | HIGH | Conditional if keyword used directly in return statement |
| TC37 | `tc37_invalid_class_missing_semicolon.cpp` | Declarations & Types | `INVALID_CLASS_DECL` | HIGH | Class declaration missing trailing semicolon after closing brace |
| TC38 | `tc38_invalid_namespace_no_braces.cpp` | Declarations & Types | `INVALID_NAMESPACE_DECL` | HIGH | Namespace declaration missing required block curly braces |
| TC39 | `tc39_reserved_keyword_as_identifier.cpp` | Declarations & Types | `INVALID_DECLARATION` | HIGH | Language reserved keyword 'class' used as an identifier name |
| TC40 | `tc40_void_variable_declaration.cpp` | Declarations & Types | `INVALID_TYPE` | HIGH | Variable declared with illegal incomplete void type |
| TC41 | `tc41_undeclared_identifier.cpp` | Semantics & Scope | `UNDECLARED_IDENTIFIER` | HIGH | Usage of variable without prior declaration in symbol table |
| TC42 | `tc42_out_of_scope_variable.cpp` | Semantics & Scope | `OUT_OF_SCOPE` | HIGH | Attempt to access block-scoped local variable outside its scope |
| TC43 | `tc43_duplicate_variable_redecl.cpp` | Semantics & Scope | `REDECLARATION` | HIGH | Duplicate declaration of same identifier in identical scope |
| TC44 | `tc44_uninitialized_variable_read.cpp` | Semantics & Scope | `UNINITIALIZED_VARIABLE` | MEDIUM | Reading uninitialized stack variable leading to garbage or undefined behavior (CWE-457) |
| TC45 | `tc45_non_void_func_missing_return.cpp` | Semantics & Scope | `MISSING_RETURN` | HIGH | Non-void function missing return statement in control flow path |
| TC46 | `tc46_void_func_returning_value.cpp` | Semantics & Scope | `INVALID_RETURN` | HIGH | Void return type function attempting to return a value |
| TC47 | `tc47_type_mismatch_pointer_int.cpp` | Semantics & Scope | `TYPE_MISMATCH` | HIGH | Assigning integer literal directly to pointer without cast |
| TC48 | `tc48_division_by_zero_constant.cpp` | Semantics & Scope | `DIVISION_BY_ZERO` | CRITICAL | Arithmetic division with literal zero divisor causing runtime SIGFPE |
| TC49 | `tc49_calling_non_function.cpp` | Semantics & Scope | `SEMANTIC_ERROR` | HIGH | Attempting to invoke integer variable as if it were a function |
| TC50 | `tc50_variable_shadowing_warning.cpp` | Semantics & Scope | `VARIABLE_SHADOWING` | LOW | Inner scope variable shadows outer scope variable with same identifier |
| TC51 | `tc51_cwe120_gets_buffer_overflow.cpp` | Cybersecurity & Threats | `CWE-120` | CRITICAL | Insecure gets() usage vulnerable to arbitrary stack buffer overflow (CWE-120 / CWE-242) |
| TC52 | `tc52_cwe121_strcpy_stack_overflow.cpp` | Cybersecurity & Threats | `CWE-121` | CRITICAL | Unbounded string copy using strcpy() causing stack overflow (CWE-121) |
| TC53 | `tc53_cwe120_strcat_concatenation_overflow.cpp` | Cybersecurity & Threats | `CWE-120` | HIGH | Unbounded string concatenation using strcat() resulting in buffer overrun |
| TC54 | `tc54_cwe134_format_string_vulnerability.cpp` | Cybersecurity & Threats | `CWE-134` | CRITICAL | Controlled format string in printf() allowing memory read/write exploits (CWE-134) |
| TC55 | `tc55_cwe401_memory_leak_new_array.cpp` | Cybersecurity & Threats | `CWE-401` | HIGH | Dynamic array heap allocation via new[] without corresponding delete[] (CWE-401) |
| TC56 | `tc56_cwe401_malloc_without_free.cpp` | Cybersecurity & Threats | `CWE-401` | HIGH | Heap allocation using malloc() abandoned without calling free() (CWE-401) |
| TC57 | `tc57_cwe835_infinite_loop_dos.cpp` | Cybersecurity & Threats | `CWE-835` | HIGH | Unbounded infinite loop leading to CPU resource exhaustion / Denial of Service (CWE-835) |
| TC58 | `tc58_cwe190_integer_overflow.cpp` | Cybersecurity & Threats | `CWE-190` | MEDIUM | Integer multiplication overflow leading to unexpected wraparound values (CWE-190) |
| TC59 | `tc59_cwe416_use_after_free.cpp` | Cybersecurity & Threats | `CWE-416` | CRITICAL | Dereferencing pointer after releasing allocated memory (CWE-416 Use After Free) |
| TC60 | `tc60_cwe476_null_pointer_dereference.cpp` | Cybersecurity & Threats | `CWE-476` | CRITICAL | Direct dereference of nullptr without validation check (CWE-476) |
| TC61 | `tc61_nested_loops_quadratic_search.cpp` | Complexity & Optimization | `COMPLEXITY_O(N^2)` | MEDIUM | Inefficient O(n^2) nested loop search for duplicate detection; optimizable to O(n) hash set |
| TC62 | `tc62_quadratic_two_sum_search.cpp` | Complexity & Optimization | `COMPLEXITY_O(N^2)` | MEDIUM | Brute-force O(n^2) pair sum search; optimizable to O(n) hash table lookup |
| TC63 | `tc63_repeated_endl_io_flushing.cpp` | Complexity & Optimization | `INEFFICIENT_IO` | LOW | Excessive stream flushing via std::endl in tight loop; optimizable to '\n' + fast I/O |
| TC64 | `tc64_vector_reallocation_no_reserve.cpp` | Complexity & Optimization | `INEFFICIENT_MEMORY` | LOW | Repeated std::vector reallocation without reserve(); causes multiple amortized heap copies |
| TC65 | `tc65_strlen_in_for_condition.cpp` | Complexity & Optimization | `COMPLEXITY_O(N^2)` | MEDIUM | Calling strlen() repeatedly inside loop header condition; turns linear scan into O(n^2) |
| TC66 | `tc66_exponential_recursive_fibonacci.cpp` | Complexity & Optimization | `COMPLEXITY_O(2^N)` | HIGH | Exponential O(2^n) naive recursion; can be transformed into O(n) iterative dynamic programming |
| TC67 | `tc67_pass_by_value_large_string.cpp` | Complexity & Optimization | `INEFFICIENT_COPY` | LOW | Passing large std::string by value causes deep heap duplication; pass by const reference |
| TC68 | `tc68_bubble_sort_quadratic.cpp` | Complexity & Optimization | `COMPLEXITY_O(N^2)` | MEDIUM | Naive bubble sort O(n^2) algorithm; can be replaced with O(n log n) std::sort |
| TC69 | `tc69_linear_search_lookup.cpp` | Complexity & Optimization | `COMPLEXITY_O(N)` | LOW | Repeated linear scan O(n) lookup over vector; replace with O(1) hash lookup |
| TC70 | `tc70_string_concat_loop.cpp` | Complexity & Optimization | `INEFFICIENT_MEMORY` | LOW | Repeated string concatenation with '+' operator in loop causing quadratic memory reallocation |
