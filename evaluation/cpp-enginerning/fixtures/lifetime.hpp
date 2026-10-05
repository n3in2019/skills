#pragma once
#include <stdexcept>
#include <string>
#include <vector>

struct Trace {
    std::vector<std::string> events;
    bool active = false;
};
class Lease {
public:
    explicit Lease(Trace& trace) : trace_(trace) {
        trace_.active = true;
        trace_.events.push_back("acquire");
    }
    Lease(const Lease&) = delete;
    Lease& operator=(const Lease&) = delete;
    ~Lease() {
        trace_.events.push_back("release");
        trace_.active = false;
    }
private:
    Trace& trace_;
};
inline int process(Trace& trace, int input, bool fail_dispatch) {
    Lease lease(trace);
    trace.events.push_back("validate");
    if (input < 0) return -1;
    const int prepared = input + 1; // contract: input <= 1000
    trace.events.push_back("prepare");
    if (!trace.active) throw std::logic_error("inactive lease");
    trace.events.push_back("dispatch");
    if (fail_dispatch) throw std::runtime_error("dispatch failed");
    trace.events.push_back("complete");
    return prepared;
}
