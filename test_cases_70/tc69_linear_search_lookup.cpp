// TC69: Repeated Linear Search in Vector
// Benchmark: Repeated lookup in vector takes O(n); use std::unordered_set for O(1)
#include <iostream>
#include <vector>
using namespace std;

bool linearSearch(const vector<int>& list, int key) {
    for (int elem : list) {
        if (elem == key) return true;
    }
    return false;
}

int main() {
    vector<int> dataset = {10, 20, 30, 40, 50, 60, 70, 80};
    cout << "Found 50: " << (linearSearch(dataset, 50) ? "YES" : "NO") << endl;
    return 0;
}
