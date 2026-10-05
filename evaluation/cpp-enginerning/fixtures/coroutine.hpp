#pragma once
#include <coroutine>
#include <exception>
#include <memory>
#include <utility>

struct Task {
    struct promise_type {
        Task get_return_object() { return Task{std::coroutine_handle<promise_type>::from_promise(*this)}; }
        std::suspend_always initial_suspend() noexcept { return {}; }
        std::suspend_always final_suspend() noexcept { return {}; }
        void return_void() noexcept {}
        void unhandled_exception() { std::terminate(); }
    };
    explicit Task(std::coroutine_handle<promise_type> handle) : handle(handle) {}
    Task(Task&& other) noexcept : handle(std::exchange(other.handle, {})) {}
    Task(const Task&) = delete;
    ~Task() { if (handle) handle.destroy(); }
    void resume() { if (handle && !handle.done()) handle.resume(); }
    std::coroutine_handle<promise_type> handle;
};

// The returned task is first resumed after make_task has returned.
inline Task make_task(std::shared_ptr<int> state) {
    auto work = [state]() -> Task {
        co_await std::suspend_always{};
        ++*state;
    };
    return work();
}
// Positive control: owning parameter is stored in coroutine frame.
inline Task make_safe_task(std::shared_ptr<int> state) {
    co_await std::suspend_always{};
    ++*state;
}
