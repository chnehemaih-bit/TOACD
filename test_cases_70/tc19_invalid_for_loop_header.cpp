// TC19: Missing parentheses in for loop header
#include <iostream>
using namespace std;

int main() {
    for int idx = 0; idx < 10; idx++ {
        cout << idx << endl;
    }
    return 0;
}
