#pragma once

#include <curl/curl.h>


typedef struct sftp_s sftp_t;
typedef struct data_s data_t;

extern "C" {
    sftp_t* sftp_init() __attribute__((visibility("default")));
    data_t* sftp_get(const sftp_t *sftp, const char *remote_path) __attribute__((visibility("default")));
}

struct sftp_s
{
    CURL *handler;
};

struct data_s
{
    void *data;
    size_t size;
};
