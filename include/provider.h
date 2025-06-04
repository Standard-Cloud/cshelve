// provider_interface.h
#pragma once

#include <string>
#include <unordered_map>
#include <memory>
#include <vector>
#include <any>


class ProviderInterface {
public:
    using Config = std::unordered_map<std::string, std::string>;
    using Params = std::unordered_map<std::string, std::any>;
    using PathName = std::string;

    explicit ProviderInterface(): {}

    virtual ~ProviderInterface() = default;

    // Close the cloud storage provider
    virtual void close() = 0;

    // Default configuration of the provider
    virtual void configure_default(const Config& config) = 0;

    // Logging configuration of the provider
    virtual void configure_logging(const Config& config) = 0;

    // Specify custom provider parameters
    virtual void set_provider_params(const Params& provider_params) = 0;

    // Check if the key exists
    virtual bool contains(const PathName& key) const = 0;

    // Create the cloud storage provider
    virtual bool create() = 0;

    // Delete the key and its associated value
    virtual bool delete_key(const PathName& key) = 0;

    // Check if the provider exists
    virtual bool exists() const = 0;

    // Get the value associated with the key
    virtual std::unique_ptr<std::ostream> get(const PathName& key) const = 0;

    // Return all keys
    virtual std::vector<PathName> iter() const = 0;

    // Return the number of keys
    virtual std::size_t len() const = 0;

    // Set the value associated with the key
    virtual void set(const PathName& key, const std::istream& value) = 0;

    // Sync the cloud storage provider
    virtual void sync() = 0;
};
