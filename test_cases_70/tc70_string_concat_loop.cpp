// TC70: Quadratic String Concatenation in Loop
// Benchmark: 'str = str + part' creates new temporary strings every loop; use '+=' or stringstream
#include <iostream>
#include <string>
using namespace std;

int main() {
    string combined = "";
    for (int i = 0; i < 5000; i++) {
        combined = combined + to_string(i) + ",";
    }
    cout << "Combined length: " << combined.length() << endl;
    return 0;
}
