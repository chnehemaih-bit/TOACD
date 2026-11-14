// TC68: Inefficient Bubble Sort O(n^2)
// Benchmark: Bubble sort has O(n^2) average/worst case; replace with std::sort O(n log n)
#include <iostream>
#include <vector>
using namespace std;

void bubbleSort(vector<int>& arr) {
    int n = arr.size();
    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < n - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                swap(arr[j], arr[j + 1]);
            }
        }
    }
}

int main() {
    vector<int> nums = {64, 34, 25, 12, 22, 11, 90};
    bubbleSort(nums);
    cout << "Sorted first element: " << nums[0] << endl;
    return 0;
}
