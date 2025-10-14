#
# Copyright (C) 2024  Autodesk, Inc. All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#

INCLUDE(cxx_defaults)

SET(_target
        "PyMediaLibrary"
)

SET(_sources
        PyMediaLibrary.cpp
        PyRootNode.cpp
        PyMediaNode.cpp
        PyNode.cpp
)

ADD_LIBRARY(
        ${_target} STATIC
        ${_sources}
)

FIND_PACKAGE(Python3 REQUIRED COMPONENTS Development)

TARGET_LINK_LIBRARIES(
        ${_target}
        PUBLIC RvApp TwkMediaLibrary Python3::Python
        PRIVATE TwkPython TwkUtil
)

# WETA: rpath libpython directly to avoid picking up the system install
SET_TARGET_PROPERTIES(
        ${_target} PROPERTIES
        SKIP_INSTALL_RPATH FALSE
        INSTALL_RPATH "${Python3_LIBRARY_DIRS}"
)

TARGET_INCLUDE_DIRECTORIES(
        ${_target}
        PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}
)

RV_STAGE(TYPE "LIBRARY" TARGET ${_target})
