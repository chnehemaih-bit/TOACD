// TC26: Invalid assignment with literal on LHS
#include <iostream>
using namespace std;

int main() {
    int score = 50;
    100 = score;
    cout << "Score: " << score << endl;
    return 0;
}
