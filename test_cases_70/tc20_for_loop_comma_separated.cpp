// TC20: Malformed for loop using commas instead of semicolons
#include <iostream>
using namespace std;

int main() {
    for (int k = 0, k < 10, k++) {
        cout << k << endl;
    }
    return 0;
}
