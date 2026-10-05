#pragma once
#include <functional>
#include <string>
#include <string_view>
#include <utility>

class Queue {
public:
    // Stores work and executes it later, after post returns, on the same thread.
    void post(std::function<void()> work);
};
class Printer {
public:
    explicit Printer(Queue& queue) : queue_(queue) {}
    // Caller can destroy Printer immediately after submit returns.
    void submit(std::string message) {
        std::string_view view = message;
        queue_.post([this, view] { emit(view); });
    }
private:
    void emit(std::string_view message);
    Queue& queue_;
};
// Borrowed pointer, valid while owner is alive; caller consumes synchronously.
inline const int* peek(const int& owner) noexcept { return &owner; }
