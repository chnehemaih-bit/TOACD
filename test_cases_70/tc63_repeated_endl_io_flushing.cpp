// TC63: Inefficient I/O Flushing via std::endl
// Benchmark: std::endl forces costly OS buffer flush on every iteration; use '\n'
#include <iostream>
using namespace std;

int main() {
    for (int i = 0; i < 10000; i++) {
        cout << "Iteration " << i << endl;
    }
    return 0;
}
