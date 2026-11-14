// TC55: Memory Leak via missing delete[] (CWE-401)
// Vulnerability: Dynamic memory allocated with new[] is never freed before exit
#include <iostream>
using namespace std;

void allocateDataset() {
    int* large_block = new int[50000];
    large_block[0] = 123;
    cout << "Dataset head: " << large_block[0] << endl;
    // Missing: delete[] large_block;
}

int main() {
    allocateDataset();
    return 0;
}
