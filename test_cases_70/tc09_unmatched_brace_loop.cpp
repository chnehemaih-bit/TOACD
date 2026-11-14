// TC09: Unmatched brace in while loop body
#include <iostream>
using namespace std;

int main() {
    int counter = 0;
    while (counter < 5) {
        counter++;
        cout << counter << endl;
    // Missing closing brace for while loop
    return 0;
}
