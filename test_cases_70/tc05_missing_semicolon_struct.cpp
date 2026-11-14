// TC05: Missing semicolon after struct definition
#include <iostream>
using namespace std;

struct Coordinate {
    int x;
    int y;
}

int main() {
    Coordinate pt;
    pt.x = 10;
    pt.y = 20;
    cout << "Point: " << pt.x << ", " << pt.y << endl;
    return 0;
}
