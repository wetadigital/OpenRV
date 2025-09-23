#
# Copyright (C) 2022  Autodesk, Inc. All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#

INCLUDE(cxx_defaults)

SET(_target
    "IOjpeg"
)

SET(_sources
    IOjpeg.cpp
)

ADD_LIBRARY(
  ${_target} STATIC
  ${_sources}
)
TARGET_INCLUDE_DIRECTORIES(
  ${_target}
  PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}
)

FIND_PACKAGE(jpegturbo REQUIRED)

TARGET_LINK_LIBRARIES(
  ${_target}
  PUBLIC TwkFB TwkUtil jpegturbo::jpegturbo
  PRIVATE exif
)

RV_STAGE(TYPE "LIBRARY" TARGET ${_target})
