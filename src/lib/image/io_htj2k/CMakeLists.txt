#
# Copyright (C) 2025 Sam Richards
# SPDX-License-Identifier: Apache-2.0
#

INCLUDE(cxx_defaults)

SET(_target
    "io_htj2k"
)

SET(_sources
    init.cpp
)

ADD_LIBRARY(
  ${_target} SHARED
  ${_sources}
)

SET_TARGET_PROPERTIES(
  ${_target}
  PROPERTIES PREFIX ""
)

FIND_PACKAGE(openjph REQUIRED)

TARGET_LINK_LIBRARIES(
  ${_target}
  PRIVATE IOhtj2k openjph
)

RV_STAGE(TYPE "IMAGE_FORMAT" TARGET ${_target})
