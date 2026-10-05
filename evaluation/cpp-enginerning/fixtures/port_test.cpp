#include "port.hpp"
#include <iostream>
#include <utility>

int main() {
    unsigned checks = 0, failures = 0;
    for (auto [text, expected] : {std::pair{"0", 0}, {"1", 1}, {"8080", 8080}, {"65535", 65535}}) {
        std::uint16_t out = 17;
        ++checks;
        if (!parse_port(text, out) || out != expected) ++failures;
    }
    for (auto text : {"", "-1", "+1", " 1", "65536", "99999999999999999999"}) {
        std::uint16_t out = 17;
        ++checks;
        if (parse_port(text, out) || out != 17) ++failures;
    }
    std::uint16_t max = 0;
    ++checks;
    if (!parse_port("65535", max) || max != 65535) ++failures;
    std::cout << "checks=" << checks << " failures=" << failures << '\n';
    return failures == 0 ? 0 : 1;
}
