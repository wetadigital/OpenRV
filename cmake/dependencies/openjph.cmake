#
#
# SPDX-License-Identifier: Apache-2.0
#

#
# Official sources: https://github.com/aous72/OpenJPH
#
# Build instructions: https://github.com/aous72/OpenJPH/blob/master/docs/compiling.md
#

INCLUDE(ProcessorCount) # require CMake 3.15+
PROCESSORCOUNT(_cpu_count)

# version 2+ requires changes to IOjp2 project
RV_CREATE_STANDARD_DEPS_VARIABLES("RV_DEPS_OPENJPH" "0.21.3" "make" "")
IF(RV_TARGET_LINUX)
  # Overriding _lib_dir created in 'RV_CREATE_STANDARD_DEPS_VARIABLES' since this CMake-based project isn't using lib64
  SET(_lib_dir
      ${_install_dir}/lib
  )
ENDIF()
RV_SHOW_STANDARD_DEPS_VARIABLES()

SET(_download_url
    "https://github.com/aous72/OpenJPH/archive/refs/tags/${_version}.tar.gz"
)
SET(_download_hash
    "d0a3fb5f643a8948d5874624ff94a229"
)

IF(RV_TARGET_WINDOWS)
  RV_MAKE_STANDARD_LIB_NAME("openjph.0.21" "0.21.3" "SHARED" "")
  SET(_libname
        "openjph.0.21.lib"
    )
    SET(_implibpath
        ${_lib_dir}/${_libname}
    )
ELSE()
  RV_MAKE_STANDARD_LIB_NAME("openjph" "0.21.3" "SHARED" "")
ENDIF()
 MESSAGE("****OPENJPH RV_MAKE_STANDARD_LIB_NAME IMPLIB _implibpath:${_implibpath} _implibname:${_implibname} _libname:${_libname} _libpath:${_libpath}")


# The '_configure_options' list gets reset and initialized in 'RV_CREATE_STANDARD_DEPS_VARIABLES'

# Do not build the executables (Openjph calls them "codec executables"). 
# BUILD_THIRDPARTY options is valid only if BUILD_CODEC=ON.
# PNG, TIFF and ZLIB are not needed anymore because they are used for the executables only.
LIST(APPEND _configure_options "-DBUILD_CODEC=OFF")

EXTERNALPROJECT_ADD(
  ${_target}
  URL ${_download_url}
  URL_MD5 ${_download_hash}
  DOWNLOAD_NAME ${_target}_${_version}.tar.gz
  DOWNLOAD_DIR ${RV_DEPS_DOWNLOAD_DIR}
  DOWNLOAD_EXTRACT_TIMESTAMP TRUE
  SOURCE_DIR ${_source_dir}
  BINARY_DIR ${_build_dir}
  INSTALL_DIR ${_install_dir}
  # DEPENDS ZLIB::ZLIB Tiff::Tiff PNG::PNG
  CONFIGURE_COMMAND ${CMAKE_COMMAND} ${_configure_options}
  BUILD_COMMAND ${_cmake_build_command}
  INSTALL_COMMAND ${_cmake_install_command}
  BUILD_IN_SOURCE FALSE
  BUILD_ALWAYS FALSE
  BUILD_BYPRODUCTS ${_byproducts}
  USES_TERMINAL_BUILD TRUE
)

# The macro is using existing _target, _libname, _lib_dir and _bin_dir variabless
RV_COPY_LIB_BIN_FOLDERS()

ADD_DEPENDENCIES(dependencies ${_target}-stage-target)

ADD_LIBRARY(OpenJph::OpenJph SHARED IMPORTED GLOBAL)

ADD_DEPENDENCIES(OpenJph::OpenJph ${_target})

IF(NOT RV_TARGET_WINDOWS)
  SET_PROPERTY(
    TARGET OpenJph::OpenJph
    PROPERTY IMPORTED_LOCATION ${_libpath}
  )
  SET_PROPERTY(
    TARGET OpenJph::OpenJph
    PROPERTY IMPORTED_SONAME ${_libname}
  )
ELSE()
  MESSAGE("****OPENJPH IMPORTEDLOCATION ${_implibpath} IMPLIB ${_implibpath} ${_libname} ${_libpath}")
  # An import library (.lib) file is often used to resolve references to 
  # functions and variables in a DLL, enabling the linker to generate code 
  # for loading the DLL and calling its functions at runtime.
  SET_PROPERTY(
    TARGET OpenJph::OpenJph
    PROPERTY IMPORTED_LOCATION "${_libpath}"
  )
  SET_PROPERTY(
    TARGET OpenJph::OpenJph
    PROPERTY IMPORTED_IMPLIB ${_implibpath}
  )
ENDIF()

# It is required to force directory creation at configure time otherwise CMake complains about importing a non-existing path
SET(_openjph_include_dir
    "${_include_dir}"
)
FILE(MAKE_DIRECTORY "${_openjph_include_dir}")
TARGET_INCLUDE_DIRECTORIES(
  OpenJph::OpenJph
  INTERFACE ${_openjph_include_dir}
)

LIST(APPEND RV_DEPS_LIST OpenJph::OpenJph)
