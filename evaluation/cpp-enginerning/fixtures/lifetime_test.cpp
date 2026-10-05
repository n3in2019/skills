#include "lifetime.hpp"
#include <iostream>

int main() {
    int failures = 0;
    const auto check = [&](bool ok) { if (!ok) ++failures; };
    Trace good;
    check(process(good, 7, false) == 8);
    check(good.events == std::vector<std::string>{"acquire", "validate", "prepare", "dispatch", "complete", "release"});
    check(!good.active);
    Trace invalid;
    check(process(invalid, -1, false) == -1);
    check(invalid.events == std::vector<std::string>{"acquire", "validate", "release"});
    check(!invalid.active);
    Trace failed;
    bool caught = false;
    try { process(failed, 7, true); }
    catch (const std::runtime_error& e) { caught = std::string(e.what()) == "dispatch failed"; }
    check(caught);
    check(failed.events == std::vector<std::string>{"acquire", "validate", "prepare", "dispatch", "release"});
    check(!failed.active);
    std::cout << "checks=9 failures=" << failures << '\n';
    return failures == 0 ? 0 : 1;
}
