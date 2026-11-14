// TC11: Unmatched extra parenthesis in expression
#include <iostream>
using namespace std;

int main() {
    int a = 10, b = 20;
    int result = ((a * 2) + b));
    cout << "Result: " << result << endl;
    return 0;
}
