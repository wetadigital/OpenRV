#
# Copyright (C) 2022  Autodesk, Inc. All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#

INCLUDE(cxx_defaults)

SET(_target
    "ImGuiPythonBridge"
)

SET(_sources
    ImGuiPythonBridge.cpp
)

ADD_LIBRARY(
  ${_target} STATIC
  ${_sources}
)
TARGET_INCLUDE_DIRECTORIES(
  ${_target}
  PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}
)

FIND_PACKAGE(Python3 REQUIRED COMPONENTS Development)

TARGET_LINK_LIBRARIES(
  ${_target}
  PUBLIC Python3::Python
)

IF(RV_TARGET_DARWIN)
  TARGET_COMPILE_OPTIONS(
    ${_target}
    PRIVATE "-Wno-deprecated-writable-strings"
  )
ENDIF()

RV_STAGE(TYPE "LIBRARY" TARGET ${_target})
