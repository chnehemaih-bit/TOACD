// TC42: Accessing variable outside its lexical scope
#include <iostream>
using namespace std;

int main() {
    {
        int local_secret = 999;
    }
    cout << "Secret is: " << local_secret << endl;
    return 0;
}
