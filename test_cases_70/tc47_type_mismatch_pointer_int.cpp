// TC47: Type mismatch in pointer assignment
#include <iostream>
using namespace std;

int main() {
    int* ptr = 500;
    cout << *ptr << endl;
    return 0;
}
