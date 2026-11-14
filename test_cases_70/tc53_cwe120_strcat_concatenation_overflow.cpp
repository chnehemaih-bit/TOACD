// TC53: Buffer Overflow via strcat() (CWE-120)
// Vulnerability: strcat() appends without validating available buffer capacity
#include <iostream>
#include <cstring>
using namespace std;

int main() {
    char buffer[20] = "BasePrefix_";
    const char* extension = "SuperLongExtensionPayloadDataExceedingLimit";
    strcat(buffer, extension);
    cout << "Combined: " << buffer << endl;
    return 0;
}
