// TC35: Misplaced keyword inside expression
#include <iostream>
using namespace std;

int main() {
    int x = return 10;
    cout << x << endl;
    return 0;
}
