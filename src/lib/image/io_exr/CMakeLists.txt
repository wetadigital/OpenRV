#
# Copyright (C) 2022  Autodesk, Inc. All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#

INCLUDE(cxx_defaults)

SET(_target
    "io_exr"
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

FIND_PACKAGE(openexr REQUIRED)

TARGET_LINK_LIBRARIES(
  ${_target}
  PRIVATE IOexr Boost::program_options openexr::openexr
)

RV_STAGE(TYPE "IMAGE_FORMAT" TARGET ${_target})
