#
# Copyright (C) 2022  Autodesk, Inc. All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#

INCLUDE(cxx_defaults)

SET(_target
    "PyTwkApp"
)

SET(_sources
    PyInterface.cpp
    PyEventType.cpp
    PyFunctionAction.cpp
    PyCommands.cpp
    PyMenuState.cpp
    PyMu.cpp
    PyMuSymbolType.cpp
)

FIND_PACKAGE(
  ${RV_QT_PACKAGE_NAME}
  COMPONENTS Core
  REQUIRED
)

ADD_LIBRARY(
  ${_target} STATIC
  ${_sources}
)
TARGET_INCLUDE_DIRECTORIES(
  ${_target}
  PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}
)

FIND_PACKAGE(imgui REQUIRED)
FIND_PACKAGE(Python3 REQUIRED COMPONENTS Development)

TARGET_LINK_LIBRARIES(
  ${_target}
  PUBLIC Python3::Python
  PRIVATE Mu
          MuLang
          MuPy
          MuTwkApp
          Qt::Core
          TwkPython
          imgui::imgui
          ImGuiPythonBridge
)

# WETA: rpath libpython directly to avoid picking up the system install
SET_TARGET_PROPERTIES(
  ${_target} PROPERTIES
  SKIP_INSTALL_RPATH FALSE
  INSTALL_RPATH "${Python3_LIBRARY_DIRS}"
)

IF(RV_TARGET_DARWIN)
  TARGET_COMPILE_OPTIONS(
    ${_target}
    PRIVATE "-Wno-deprecated-writable-strings"
  )
ENDIF()

RV_STAGE(TYPE "LIBRARY" TARGET ${_target})
