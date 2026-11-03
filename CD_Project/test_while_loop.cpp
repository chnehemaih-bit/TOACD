#include <iostream>
using namespace std;

int main() {
    int x = 5;
    while x > 0 { //missing brackets
        cout << x << endl;
        x--;
    }
    return 0;
}
