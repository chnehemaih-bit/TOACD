// TC14: Extra stray tokens after semicolon
#include <iostream>
using namespace std;

int main() {
    int count = 5; unexpected_token
    cout << count << endl;
    return 0;
}
