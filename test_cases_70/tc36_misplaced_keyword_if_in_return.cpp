// TC36: Misplaced conditional keyword inside return
#include <iostream>
using namespace std;

int checkPositive(int n) {
    return if (n > 0);
}

int main() {
    cout << checkPositive(5) << endl;
    return 0;
}
