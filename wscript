#! /usr/bin/env python
# -*- coding: utf-8 -*-
"Build definition and execution"


# -------------------------------------------------
# Globals
# -------------------------------------------------


# These ranges are used when defining pak requirements.
# There's a disconnect here between these manually-specified values and the
# variants returned by BuildMatrix, so these will need to be updated whenever
# a new build variant is introduced.
VFX_RANGE = "2023.0.6<2024"


# -------------------------------------------------
# Options
# -------------------------------------------------


def options(opt):
    opt.load("wak.tools")
    opt.load("compiler_cxx")
    opt.load("buildmatrix_wak")


# -------------------------------------------------
# Helpers
# -------------------------------------------------


def make_app_version(conf):
    pak_vars = {
        "name": conf.env.WAK_APP_NAME,
        "version": conf.env.WAK_APP_VERSION,
        "requires": {
            "boost": {"ver_range": "|"},
            "ffmpeg": {"ver_range": ">=8.0.0"},
            "imgui": {"ver_range": "1.91.9-508d0bc<1.92"},
            "imgui_node_editor": {"ver_range": "2025.03.25-dae8edc<2026"},
            "imgui_backend_qt": {"ver_range": "2024.12.11-023345c<2025"},
            "implot": {"ver_range": "2025.04.03-61af48e<2026"},
            "libtiff": {"ver_range": "|"},
            "OpenColorIO": {"ver_range": "|"},
            "pyimgui": {"ver_range": "|"},
            "pynanobind": {"ver_range": "|"},
            "python": {"ver_range": "|"},
            "qt": {"ver_range": "|"},
            "WetaVFXPlatform": {"ver_range": VFX_RANGE},
        },
        "buildRequires": {
            "python": {"ver_range": "|"},
            "WetaVFXPlatform": {"ver_range": VFX_RANGE},
        },
    }

    app_version = conf.makePak(
        variables=[
            {
                "target": "PATH",
                "value": "${PREFIX}/flavor-opt/WetaVFXPlatform-%(WETA_VFXPLATFORM_ID)s/bin",
                "action": "env_prp",
            },
            {
                "target": "LD_LIBRARY_PATH",
                "value": "${PREFIX}/flavor-opt/WetaVFXPlatform-%(WETA_VFXPLATFORM_ID)s/lib",
                "action": "env_prp",
            },
            {
                "target": "RV_HOME",
                "value": "${PREFIX}/flavor-opt/WetaVFXPlatform-%(WETA_VFXPLATFORM_ID)s",
                "action": "env_set",
            },
        ],
        **pak_vars
    )

    app_version_dbg = conf.makePak(
        appName=f"{conf.env.WAK_APP_NAME}_dbg",
        variables=[
            {
                "target": "PATH",
                "value": "${PREFIX}/flavor-dbg/WetaVFXPlatform-%(WETA_VFXPLATFORM_ID)s/bin",
                "action": "env_prp",
            },
            {
                "target": "LD_LIBRARY_PATH",
                "value": "${PREFIX}/flavor-dbg/WetaVFXPlatform-%(WETA_VFXPLATFORM_ID)s/lib",
                "action": "env_prp",
            },
            {
                "target": "RV_HOME",
                "value": "${PREFIX}/flavor-dbg/WetaVFXPlatform-%(WETA_VFXPLATFORM_ID)s",
                "action": "env_set",
            },
        ],
        **pak_vars
    )

    return app_version, app_version_dbg


def configure_cmake_folder(conf, path, **kwargs):

    # Load the C++ compiler tool after a compiler has been selected via oz paks
    conf.load("compiler_cxx")
    conf.load("wak.tools.cmake")

    # Additional link and CXX flags are defined within ".buildmatrix.yaml"
    conf.buildmatrix_set_flags(flavor_override="opt")

    return conf.cmakeGenerate(
        source_dir=path,
        **kwargs,
    )


# -------------------------------------------------
# Configure
# -------------------------------------------------


def configure(conf):
    conf.env.WAK_APP_NAME = "openrv"
    conf.env.WAK_NON_CI_RELEASE_CMDS = ["tag"]

    conf.load("wak.tools")
    conf.load("wak.tools.deploySource")
    conf.load("buildmatrix_wak")

    # Checkout the build in the release dir and run the build from there.
    # This ensures that the source is deployed alongside the code, and allows the debug information to contain
    # actual file paths.
    conf.env.WAK_STAGED_RELEASE = "1"
    conf.env.WAK_STAGED_RELEASE_SRC = "1"
    conf.env.WAK_STAGED_RELEASE_BASE = "/digi/src/"
    conf.env.WAK_STAGED_RELEASE_SRC_GROUP = "dev"
    conf.env.WAK_STAGED_RELEASE_SRC_PERMS = "0444"

    # Make the lib pak
    make_app_version(conf)

    requirements = [
        "OpenColorIO",
        "bdwgc",
        "bison",
        "cmake",
        "ffmpeg->=8.0.0<9",
        "freetype",
        "ftgl",
        "gcc",  # Constrained by the ABI variant
        "glew",
        "imath",
        "imgui",
        "imgui_backend_qt",
        "imgui_node_editor",
        "implot",
        "libaio",
        "libasound2",
        "libflex",
        "libfreeglut",
        "libglu",
        "libjpegturbo",
        "libopengl",
        "libopenimageio",
        "libopenssl",
        "libpython",
        "libtiff",
        "libyamlcpp",
        "nasm",
        "ninja-1.10<2",
        "openexr",
        "openjph",
        "osmesa",
        "pymeson",
        "python",
        "qt",
        "readline",
        "vulkansdk",
        "weta_cmake_provider->=2.2",
        # TODO: libaja 17.5 seems to introduce issues, validate
        "libaja->17.1<17.5",
        # TODO: add these requires to qt pak:
        "libsnappy-1.1.3",
        "minizip_ng-4.0.10",
        "libevent-2.1.12",
        # TODO: remove these as ffmpeg8 should bring them in as part of build requires:
        "libvpx",
        "libx265",
        "x264",
    ]

    for _ in conf.buildmatrix_make_nested_variants(
        ["flavor", "WetaVFXPlatform"],
        category="flavored_platform",
        filter_variants={"WetaVFXPlatform": ["VP23"],},
    ):
        # Use the flavor to determine the correct CMAKE_BUILD_TYPE
        build_type = "Debug" if conf.buildmatrix_get_flavor() == "dbg" else "Release"

        conf.buildmatrix_oz(area="/", limits=requirements, prefer_min=False)
        conf.env.env["HTTPS_PROXY"] = "www-proxy.wetafx.co.nz:3128"
        conf.env.env["HTTP_PROXY"] = "www-proxy.wetafx.co.nz:3128"
        conf.env.env["NO_PROXY"] = "localhost,127.0.0.0/8,wetafx.co.nz"
        conf.env.env["https_proxy"] = "www-proxy.wetafx.co.nz:3128"
        conf.env.env["http_proxy"] = "www-proxy.wetafx.co.nz:3128"
        conf.env.env["no_proxy"] = "localhost,127.0.0.0/8,wetafx.co.nz"

        conf.env.env["WETA_Qt5_CMAKE_CONFIG_DIR"] = f"{conf.env.QTDIR}/lib/cmake"

        # TODO: Fix up base paks
        conf.env.env["LIBIMGUI_BACKEND_QT_TYPE"] = "shared"
        conf.env.env["LIBIMGUI_NODE_EDITOR_TYPE"] = "header_only"
        conf.env.env["LIBOPENEXR_LIB"] = "OpenEXR"
        conf.env.env["LIBIMATH_LIB"] = "Imath"
        conf.env.env["LIBFREEGLUT_LIB"] = "glut"
        conf.env.env["LIBREADLINE_TYPE"] = "header_only"
        conf.env.env["LIBVULKANSDK_TYPE"] = "shared"
        conf.env.env["LIBVULKANSDK_LIB"] = "vulkan"

        # Configure the required executables:
        conf.find_program("moc")
        conf.find_program("uic")
        conf.find_program("rcc")

        configure_cmake_folder(
            conf,
            str(conf.path),
            CMAKE_BUILD_TYPE=build_type,
            RV_DEPS_QT5_LOCATION=conf.env.QTDIR,
            # Disable target requirements on link to allow linking against rt and dl
            CMAKE_LINK_LIBRARIES_ONLY_TARGETS="OFF",
            Qt5Core_MOC_EXECUTABLE=conf.env.MOC[0],
            Qt5Widgets_UIC_EXECUTABLE=conf.env.UIC[0],
            Qt5Core_RCC_EXECUTABLE=conf.env.RCC[0],
            RV_FFMPEG_NON_FREE_DECODERS_TO_ENABLE="hevc;aac;mpeg2video;prores;dnxhd",
        )


# -------------------------------------------------
# Build
# -------------------------------------------------


def build(bld):

    for _ in bld.iterVariants(category="flavored_platform"):
        vfx_build_task = bld.cmakeBuild(
            name="build",
        )

        bld.cmakeInstall(
            name="install",
            dependsOn=[vfx_build_task],
        )

        # Copy the required QT binaries/resources into our pak as OpenRV expects
        # this. It is possible to edit the qt.conf files throughout this repo to
        # point to the real QT pak instead, but in order for QT to be able to use
        # the OpenRV plugins the plugins config will have to point at OpenRV -
        # which hides any standard QT plugins in the QT pak itself.
        bld(
            rule=f"rsync -auv {bld.env.QTDIR}/lib {bld.env.QTDIR}/libexec {bld.env.QTDIR}/resources {bld.env.QTDIR}/translations {bld.env.PREFIX}",
            # Depend on the build task to make sure bld.env.PREFIX exists already
            dependsOn=[vfx_build_task],
            always=True,
        )

    if bld.isRelease():
        bld.setOzAppDetails(
            app=f"{bld.env.WAK_APP_NAME}",
            options={
                "contacts": {
                    "Department": "Engineering",
                    "Maintainer": "jbatchelor@wetafx.co.nz",
                },
                "description": "Open source version of RV, the Sci-Tech award-winning media review and playback software.",
                "info": {
                    "JIRA": f"https://jira.wetafx.co.nz/projects/HABITAT",
                    "Teams": "https://teams.microsoft.com/l/channel/19%3A9464d1bfef714b7cb94b88c7feaa86fc%40thread.skype/build-test-deployment?groupId=b544b9ae-752e-45f6-843d-49fb0317a731&tenantId=5ecba919-6cf8-411b-a462-db882331fd21",
                },
                "third_party": True,
                "license": "Apache License Version 2.0",
            },
            description="set/refresh the app metadata",
        )
