#include <string>
#include <string_view>
#include "sizepacks.h"


// Stores an immutable string using little memory overhead.

// It is important to use PyMem_Malloc, because glibc malloc does not free
// memory, unless malloc_trim is called. But malloc_trim is slow. Other
// allocators could be considered, but low memory overhead is rarely a priority
// for them.

class cramped_string {
public:
    cramped_string() : data(nullptr) {}
    cramped_string(const std::string_view& s) {
        from_string_view(s);
    }
    cramped_string(const cramped_string& other) {
        from_string_view(other.to_string_view());
    }
    cramped_string(cramped_string&& other) {
        data = other.data;
        other.data = nullptr;
    }
    ~cramped_string() noexcept {
        free_data();
    }

    operator std::string_view() const {
        return to_string_view();
    }

    bool operator==(const cramped_string& other) const {
        return to_string_view() == other.to_string_view();
    }

    bool operator!=(const cramped_string& other) const {
        return to_string_view() != other.to_string_view();
    }

    bool operator<(const cramped_string& other) const {
        return to_string_view() < other.to_string_view();
    }

    cramped_string& operator=(const cramped_string& other) {
        if (this != &other) {
            free_data();
            from_string_view(other.to_string_view());
        }
        return *this;
    }

    cramped_string& operator=(cramped_string&& other) {
        if (this != &other) {
            free_data();
            data = other.data;
            other.data = nullptr;
        }
        return *this;
    }

    void swap(cramped_string& other) {
        std::swap(data, other.data);
    }

private:
    void from_string_view(const std::string_view& s) {
        char buf[4];
        char* endptr = sizepacks::pack(s.size(), (char*)buf);
        data = PyMem_Malloc(endptr - buf + s.size());
        memcpy(data, buf, endptr - buf);
        memcpy((char*)data + (endptr - buf), s.data(), s.size());
    }

    std::string_view to_string_view() const {
        if (!data) {
            return std::string_view();
        }
        sizepacks::unpackinfo_t info;
        info = sizepacks::unpack((char*)data);
        return std::string_view((char*)info.endptr, info.size);
    }

    void free_data() {
        if (data) {
            PyMem_Free(data);
        }
    }

    void* data;
};

namespace std {
template <>
struct hash<cramped_string> {
  auto operator()(const cramped_string &s) const -> size_t {
    return hash<string>{}((string)s);
  }
};
}  // namespace std
