// TC62: Brute-Force O(n^2) Two Sum Search
// Benchmark: Quadratic search can be optimized to O(n) using unordered_map
#include <iostream>
#include <vector>
using namespace std;

bool findTwoSum(const vector<int>& arr, int target) {
    int len = arr.size();
    for (int i = 0; i < len; i++) {
        for (int j = i + 1; j < len; j++) {
            if (arr[i] + arr[j] == target) {
                return true;
            }
        }
    }
    return false;
}

int main() {
    vector<int> numbers = {2, 7, 11, 15};
    cout << "Pair found: " << (findTwoSum(numbers, 9) ? "YES" : "NO") << endl;
    return 0;
}
