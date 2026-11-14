// TC44: Use of uninitialized variable (CWE-457)
#include <iostream>
using namespace std;

int main() {
    int uninit_counter;
    int total = uninit_counter + 10;
    cout << "Total: " << total << endl;
    return 0;
}
