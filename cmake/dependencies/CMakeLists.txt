#
# Copyright (C) 2022  Autodesk, Inc. All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#

INCLUDE(rv_create_std_deps_vars)
INCLUDE(rv_make_std_lib_name)
INCLUDE(rv_copy_lib_bin_folders)

IF(NOT TARGET dependencies)
  ADD_CUSTOM_TARGET(dependencies)
ENDIF()

IF(NOT DEFINED RV_DEPS_LIST)
  SET(RV_DEPS_LIST
      ""
      CACHE INTERNAL ""
  )
ENDIF()

FIND_PACKAGE(Git QUIET)
IF(GIT_FOUND
   AND EXISTS "${PROJECT_SOURCE_DIR}/.git"
)
  # Update submodules as needed
  OPTION(GIT_SUBMODULE "Check submodules during build" ON)
  IF(GIT_SUBMODULE)
    MESSAGE(STATUS "Updating submodules")
    EXECUTE_PROCESS(
      COMMAND ${GIT_EXECUTABLE} submodule update --init --recursive
      WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
      RESULT_VARIABLE GIT_SUBMOD_RESULT
    )
    IF(NOT GIT_SUBMOD_RESULT EQUAL "0")
      MESSAGE(WARNING "Unable to init or update git submodules (${GIT_SUBMOD_RESULT})")
    ENDIF()
  ENDIF()
ENDIF()

IF(NOT EXISTS "${PROJECT_SOURCE_DIR}/src/pub/CMakeLists.txt")
  MESSAGE(FATAL_ERROR "Unable to find required git submodules. GIT_SUBMODULE was turned off or failed. Please update submodules and try again.")
ENDIF()

IF(RV_TARGET_WINDOWS)
  INCLUDE(expat)
ENDIF()

IF(RV_TARGET_WINDOWS)
  INCLUDE(atomic_ops)
ENDIF()
INCLUDE(zlib)
INCLUDE(doctest)
INCLUDE(png)
# src/pub: lmcs: src/pub will be removed eventually, this path will needed to change.
ADD_SUBDIRECTORY(../../src/pub/lcms src/pub/lcms) # required by raw
INCLUDE(raw) # depends on jpeg, zlib
INCLUDE(webp)
IF(RV_TARGET_WINDOWS)
  INCLUDE(pcre2)
ENDIF()

INCLUDE(bmd.cmake)
INCLUDE(spdlog)

LIST(REMOVE_DUPLICATES RV_DEPS_LIST)
SET(RV_DEPS_LIST
    ${RV_DEPS_LIST}
    CACHE INTERNAL ""
)

IF(RV_DEPS_BMD_VERSION)
  MESSAGE(STATUS "Using BMD:          ${RV_DEPS_BMD_VERSION}")
ENDIF()
IF(RV_TARGET_WINDOWS)
  MESSAGE(STATUS "Using atomic_ops:   ${RV_DEPS_ATOMIC_OPS_VERSION}")
ENDIF()
IF(RV_TARGET_WINDOWS)
  MESSAGE(STATUS "Using PCRE2:        ${RV_DEPS_PCRE2_VERSION}")
ENDIF()
MESSAGE(STATUS "Using PNG:          ${RV_DEPS_PNG_VERSION}")

MESSAGE(STATUS "Using Raw:          ${RV_DEPS_RAW_VERSION}")
MESSAGE(STATUS "Using WebP:         ${RV_DEPS_WEBP_VERSION}")
MESSAGE(STATUS "Using zlib:         ${RV_DEPS_ZLIB_VERSION}")
MESSAGE(STATUS "Using spdlog:       ${RV_DEPS_SPDLOG_VERSION}")
