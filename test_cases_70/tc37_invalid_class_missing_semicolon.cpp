// TC37: Class declaration missing trailing semicolon
#include <iostream>
using namespace std;

class Vehicle {
public:
    int speed;
}

int main() {
    Vehicle car;
    car.speed = 100;
    cout << car.speed << endl;
    return 0;
}
