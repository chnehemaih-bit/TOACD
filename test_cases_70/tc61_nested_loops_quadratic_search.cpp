// TC61: Inefficient O(n^2) Nested Loop Duplicate Check
// Benchmark: Quadratic time complexity can be reduced to O(n) using unordered_set
#include <iostream>
#include <vector>
using namespace std;

bool hasDuplicates(const vector<int>& nums) {
    int n = nums.size();
    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            if (nums[i] == nums[j]) {
                return true;
            }
        }
    }
    return false;
}

int main() {
    vector<int> data = {1, 2, 3, 4, 5, 2};
    cout << "Has dups: " << (hasDuplicates(data) ? "YES" : "NO") << endl;
    return 0;
}
