#include "../fixtures/coroutine.hpp"
#include <cassert>
#include <iostream>
#include <string_view>

int main(int argc, char** argv) {
    assert(argc == 2);
    const std::string_view mode(argv[1]);
    if (mode == "safe") {
        std::weak_ptr<int> weak;
        {
            auto owner = std::make_shared<int>(41);
            weak = owner;
            auto task = make_safe_task(owner);
            assert(owner.use_count() == 2);
            owner.reset();
            assert(!weak.expired());
            assert(*weak.lock() == 41);
            task.resume(); // initial_suspend -> explicit co_await
            assert(*weak.lock() == 41);
            assert(!task.handle.done());
            task.resume(); // increment -> final_suspend
            assert(*weak.lock() == 42);
            assert(task.handle.done());
            task.resume(); // documented Task guard is harmless at final suspend
            assert(*weak.lock() == 42);
        }
        assert(weak.expired());
        std::cout << "PASS safe: owned until frame destruction; increment on second resume\n";
    } else if (mode == "ownership") {
        auto owner = std::make_shared<int>(41);
        std::weak_ptr<int> weak = owner;
        auto task = make_task(owner);
        assert(owner.use_count() == 1);
        owner.reset();
        assert(weak.expired());
        std::cout << "OBSERVED make_task: state already destroyed before first resume\n";
    } else if (mode == "unsafe") {
        auto owner = std::make_shared<int>(41); // retain pointee to isolate dangling closure
        auto task = make_task(owner);
        task.resume();
        assert(*owner == 41);
        task.resume(); // dangling closure member state is accessed here
        assert(*owner == 42);
        std::cout << "unsafe completed without an observed failure\n";
    } else {
        return 2;
    }
}
