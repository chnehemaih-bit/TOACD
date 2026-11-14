// TC45: Non-void function missing return statement
#include <iostream>
using namespace std;

int computeStatus(int flag) {
    if (flag > 0) {
        return 1;
    }
    // Missing return when flag <= 0
}

int main() {
    cout << computeStatus(-1) << endl;
    return 0;
}
