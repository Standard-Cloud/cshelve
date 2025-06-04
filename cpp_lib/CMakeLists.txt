# CMakeList.txt : CMake project for sftp, include source and define
# project specific logic here.
#
cmake_minimum_required (VERSION 3.21)
set( CMAKE_CXX_COMPILER g++)

# Enable Hot Reload for MSVC compilers if supported.
if (POLICY CMP0141)
  cmake_policy(SET CMP0141 NEW)
  set(CMAKE_MSVC_DEBUG_INFORMATION_FORMAT "$<IF:$<AND:$<C_COMPILER_ID:MSVC>,$<CXX_COMPILER_ID:MSVC>>,$<$<CONFIG:Debug,RelWithDebInfo>:EditAndContinue>,$<$<CONFIG:Debug,RelWithDebInfo>:ProgramDatabase>>")
endif()

project ("cshelve"
  VERSION 0.1.0
  DESCRIPTION "C++ library for SFTP operations"
  LANGUAGES CXX)

find_package(CURL REQUIRED)

# Add source to this project's executable.
add_library(cshelve SHARED "${CMAKE_SOURCE_DIR}/../src/sftp.cpp")
target_include_directories(cshelve PUBLIC "${CMAKE_SOURCE_DIR}/../include")

if (CMAKE_VERSION VERSION_GREATER 3.12)
  set_property(TARGET cshelve PROPERTY CXX_STANDARD 20)
endif()

target_link_libraries(cshelve PRIVATE CURL::libcurl)
set_target_properties(cshelve PROPERTIES LINKER_LANGUAGE CXX)
