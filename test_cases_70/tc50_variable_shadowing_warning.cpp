// TC50: Variable shadowing across nested scopes
#include <iostream>
using namespace std;

int main() {
    int count = 100;
    if (count > 50) {
        int count = 20;
        cout << "Inner count: " << count << endl;
    }
    cout << "Outer count: " << count << endl;
    return 0;
}
