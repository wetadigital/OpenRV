#
# Copyright (C) 2022  Autodesk, Inc. All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#

INCLUDE(cxx_defaults)

SET(_target
    "TwkImg"
)

SET(_sources
    TwkImgCineonIff.cpp TwkImgSgiIff.cpp
)

ADD_LIBRARY(
  ${_target} STATIC
  ${_sources}
)

TARGET_INCLUDE_DIRECTORIES(
  ${_target}
  PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}
)

FIND_PACKAGE(openexr REQUIRED)
FIND_PACKAGE(tiff REQUIRED)

TARGET_LINK_LIBRARIES(
  ${_target}
  PUBLIC TwkMath openexr::openexr
  PRIVATE TwkUtil tiff::tiff
)

RV_STAGE(TYPE "LIBRARY" TARGET ${_target})
