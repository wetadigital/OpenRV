#
# Copyright (C) 2025 Sam Richards
# SPDX-License-Identifier: Apache-2.0
#

INCLUDE(cxx_defaults)

SET(_target
    "IOhtj2k"
)

SET(_sources
    IOhtj2k.cpp
)

ADD_LIBRARY(
  ${_target} STATIC
  ${_sources}
)

TARGET_INCLUDE_DIRECTORIES(
  ${_target}
  PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}
)

TARGET_LINK_LIBRARIES(
  ${_target}
  PUBLIC TwkFB
  PRIVATE  TwkUtil OpenJph::OpenJph
  )


RV_STAGE(TYPE "LIBRARY" TARGET ${_target})
