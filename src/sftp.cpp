#include "sftp.h"

sftp_t* sftp_init()
{
    sftp_t *sftp = (sftp_t *)calloc(1, sizeof(sftp_t));

    if (!sftp) {
        return NULL; // Memory allocation failed
    }

    curl_global_init(CURL_GLOBAL_ALL);
    sftp->handler = curl_easy_init();

    if (!sftp->handler) {
        free(sftp);
        return NULL; // CURL initialization failed
    }

    curl_easy_setopt(sftp->handler, CURLOPT_VERBOSE, 1L);
    
    return sftp;
}


static size_t _write_callback(void *ptr, size_t size, size_t nmemb, void *userdata)
{
    data_t *data = (data_t *)userdata;

    if (!data) {
        return 0; // No userdata provided
    }

    size_t total_size = size * nmemb;
    
    // Allocate or reallocate memory for data->data
    data->data = malloc(total_size * sizeof(char));
    if (!data->data) {
        return 0; // Memory allocation failed
    }
    
    memcpy(data->data, ptr, total_size);
    data->size = total_size;

    return nmemb;
}


data_t* sftp_get(const sftp_t *sftp, const char *remote_path)
{
    data_t *data = (data_t *)calloc(1, sizeof(data_t));

    if (!data) {
        return NULL; // Memory allocation failed
    }

    curl_easy_setopt(sftp->handler, CURLOPT_URL, "sftp://cshelve:cloud-shelve@sftp-password/upload/filename");
    curl_easy_setopt(sftp->handler, CURLOPT_WRITEDATA, data);
    //curl_easy_setopt(sftp->handler, CURLOPT_WRITEFUNCTION, _write_callback);
    
    CURLcode res = curl_easy_perform(sftp->handler);

    if(res != CURLE_OK) {
        fprintf(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(res));
    }
    return data;
}

