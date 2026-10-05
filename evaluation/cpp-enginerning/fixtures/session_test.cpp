#include "session.hpp"
#include <iostream>
int main() {
    int checks = 0, failures = 0;
    auto check = [&](bool value) { ++checks; if (!value) ++failures; };
    { ManualQueue q; Session s(q); s.start(7); q.complete(0); q.complete(0);
      check(s.published() == std::vector<int>{7}); }
    { ManualQueue q; Session s(q); s.start(7); s.cancel(); q.complete(0);
      check(s.published().empty()); }
    std::cout << "checks=" << checks << " failures=" << failures << '\n';
    return failures == 0 ? 0 : 1;
}
