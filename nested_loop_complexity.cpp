#include <iostream>
using namespace std;

int main() {
    for (int i = 0; i < 1000; i++) {
        for (int j = 0; j < 1000; j++) {
            for (int k = 0; k < 1000; k++) {
                cout << i + j + k << endl;
            }
        }
    }

    return 0;
}
