// TC56: Heap Memory Leak via missing free() (CWE-401)
// Vulnerability: Memory allocated via malloc() is never deallocated
#include <iostream>
#include <cstdlib>
using namespace std;

void processRecords() {
    char* records = (char*)malloc(1024 * sizeof(char));
    records[0] = 'A';
    cout << "Record: " << records[0] << endl;
    // Missing: free(records);
}

int main() {
    processRecords();
    return 0;
}
