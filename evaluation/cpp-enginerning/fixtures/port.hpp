#pragma once
#include <charconv>
#include <cstdint>
#include <string_view>
#include <system_error>

// Decimal digits only, 0..65535 inclusive. Invalid input leaves out unchanged.
inline bool parse_port(std::string_view text, std::uint16_t& out) {
    if (text.empty()) return false;
    unsigned value = 0;
    const auto parsed = std::from_chars(text.data(), text.data() + text.size(), value);
    if (parsed.ec != std::errc{} || value > 65535) return false;
    out = static_cast<std::uint16_t>(value);
    return true;
}
