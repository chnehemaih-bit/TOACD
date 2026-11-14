// TC08: Unmatched brace in if block
#include <iostream>
using namespace std;

int main() {
    int threshold = 50;
    if (threshold > 10) {
        int alert = 1;
        cout << "Alert triggered" << endl;
    // Missing closing brace for if block
    return 0;
}
