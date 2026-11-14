// TC64: Inefficient Vector Growth without reserve()
// Benchmark: Repeated dynamic reallocation copies entire buffer; use v.reserve(N)
#include <iostream>
#include <vector>
using namespace std;

int main() {
    vector<int> items;
    for (int i = 0; i < 100000; i++) {
        items.push_back(i);
    }
    cout << "Items added: " << items.size() << endl;
    return 0;
}
