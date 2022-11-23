
// Packing/unpacking string sizes.

namespace sizepacks {

#ifdef __GNUC__
#define PACK( __Declaration__ ) __Declaration__ __attribute__((__packed__))
#endif

#ifdef _MSC_VER
#define PACK( __Declaration__ ) __pragma( pack(push, 1) ) __Declaration__ __pragma( pack(pop))
#endif

PACK(struct pack64 {
    char header = 0xd3u;
    size_t size;
});

PACK(struct pack32 {
    char header = 0xd2u;
    uint32_t size;
});

PACK(struct pack16 {
    char header = 0xd1u;
    uint16_t size;
});

PACK(struct pack8 {
    char header = 0xd0u;
    uint8_t size;
});


// size, startptr -> endptr
char* pack(size_t d, char* buf)
{
    if(d < (1LL<<16)) {
        if(d < (1<<8)) {
            *(pack8*)buf = pack8{(char)0xd0, (uint8_t)d};
            return buf + sizeof(pack8);
        } else {
            *(pack16*)buf = pack16{(char)0xd1, (uint16_t)(d)};
            return buf + sizeof(pack16);
        }
    } else {
        if(d < (1LL<<32)) {
            *(pack32*)buf = pack32{(char)0xd2, (uint32_t)(d)};
            return buf + sizeof(pack32);
        } else {
            *(pack64*)buf = pack64{(char)0xd3, (uint64_t)d};
            return buf + sizeof(pack64);
        }
    }
}

struct unpackinfo_t {
    size_t size;
    char* endptr;
};

// startptr -> size, endptr
unpackinfo_t unpack(char* buf) {
    switch(buf[0]) {
        case (char)0xd0:
            return {
                ((pack8*)buf)->size,
                buf + sizeof(pack8)
            };
        case (char)0xd1:
            return {
                ((pack16*)buf)->size,
                buf + sizeof(pack16)
            };
        case (char)0xd2:
            return {
                ((pack32*)buf)->size,
                buf + sizeof(pack32)
            };
        case (char)0xd3:
            return {
                ((pack64*)buf)->size,
                buf + sizeof(pack64)
            };
        default:
            return {0, buf};
    }
}

} // namespace sizepacks
