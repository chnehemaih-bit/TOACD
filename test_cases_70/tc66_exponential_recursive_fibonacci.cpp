// TC66: Naive Exponential Recursive Fibonacci
// Benchmark: O(2^n) branching recursion redundant calls; optimize to O(n) DP
#include <iostream>
using namespace std;

int fibonacci(int n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

int main() {
    int n = 35;
    cout << "Fib(" << n << ") = " << fibonacci(n) << endl;
    return 0;
}
