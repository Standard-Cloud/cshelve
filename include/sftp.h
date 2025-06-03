#pragma once
#include <stddef.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include <curl/curl.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct sftp_s sftp_t;
typedef struct data_s data_t;

sftp_t* sftp_init(void) __attribute__((visibility("default")));
data_t* sftp_get(const sftp_t *sftp, const char *remote_path) __attribute__((visibility("default")));

struct sftp_s
{
    CURL *handler;
};

struct data_s
{
    void *data;
    size_t size;
};

#ifdef __cplusplus
}
#endif
