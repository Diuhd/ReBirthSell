#include <cstdlib>
#include <cstdio>
#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>

/*
{"server_ip": "127.0.0.1"}
*/

int main() {
    std::string ip;
    std::cout << "Update Options: DEFAULT/&LOCALHOST";
    std::cin >> ip;
    std::string path = "client\\config\\config.json";
    std::string templ = "{\"server_ip\": \"" + ip + "\"}";
    std::cout << templ << std::endl;
    std::ofstream file(path);
    if (file.is_open()) {
        file << templ;
        file.close();
    }
    return 0;
}
