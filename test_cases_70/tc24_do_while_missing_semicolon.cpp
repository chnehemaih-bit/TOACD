// TC24: Do-while missing trailing semicolon
#include <iostream>
using namespace std;

int main() {
    int step = 0;
    do {
        step++;
    } while (step < 3)
    return 0;
}
