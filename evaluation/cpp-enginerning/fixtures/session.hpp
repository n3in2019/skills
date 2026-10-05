#pragma once
#include <functional>
#include <string>
#include <utility>
#include <vector>

struct ManualQueue {
    // Single-threaded. Work may be invoked later and more than once.
    std::vector<std::function<void()>> pending;
    void post(std::function<void()> fn) { pending.push_back(std::move(fn)); }
    void complete(unsigned index) { auto fn = pending.at(index); fn(); }
};
class Session {
public:
    explicit Session(ManualQueue& queue) : queue_(queue) {}
    // All methods/callbacks run on one thread; Session outlives queued callbacks.
    // Latest start wins; cancel suppresses publication, not queued work.
    // Each accepted operation may publish at most once.
    void start(int value) {
        active_ = true;
        queue_.post([this, value] {
            if (!active_) return;
            published_.push_back(value);
            active_ = false;
        });
    }
    void cancel() { active_ = false; }
    const std::vector<int>& published() const { return published_; }
private:
    ManualQueue& queue_;
    bool active_ = false;
    std::vector<int> published_;
};
