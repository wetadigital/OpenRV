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

    app_version = conf.makePak(
        name=conf.env.WAK_APP_NAME,
        version=conf.env.WAK_APP_VERSION,
        variables=[
            {
                "target": "PATH",
                "value": "${PREFIX}/WetaVFXPlatform-%(WETA_VFXPLATFORM_ID)s/bin",
                "action": "env_prp",
            },
            {
                "target": "LD_LIBRARY_PATH",
                "value": "${PREFIX}/WetaVFXPlatform-%(WETA_VFXPLATFORM_ID)s/lib",
                "action": "env_prp",
            },
            {
                "target": "RV_HOME",
                "value": "${PREFIX}/WetaVFXPlatform-%(WETA_VFXPLATFORM_ID)s",
                "action": "env_set",
            },
        ],
        requires={
            "imgui": {"ver_range": "1.91.9-508d0bc<1.92"},
            "imgui_node_editor": {"ver_range": "2025.03.25-dae8edc<2026"},
            "imgui_backend_qt": {"ver_range": "2024.12.11-023345c<2025"},
            "implot": {"ver_range": "2025.04.03-61af48e<2026"},
            "libtiff": {"ver_range": "|"},
            "OpenColorIO": {"ver_range": "|"},
            "python": {"ver_range": "|"},
            "qt": {"ver_range": "|"},
            "WetaVFXPlatform": {"ver_range": VFX_RANGE},
        },
        buildRequires={
            "python": {"ver_range": "|"},
            "WetaVFXPlatform": {"ver_range": VFX_RANGE},
        },
    )

    return app_version


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
        "gcc",  # Constrained by the ABI variant
        "ninja-1.10<2",
        "cmake",
        "weta_cmake_provider->=2.2",
        "qt",
        "libflex",
        # Don't use the system install of git with a pcre2 pak
        "git",
        # TODO: Remove version once unexp
        "pcre2-10.31-weta.1",
        "freetype",
        "libopengl",
        "libglu-9.0.2",
        "osmesa-23.2.1",
        "python",
        "glew",
        "bdwgc-8.2.2",
        "nasm-2.16.01",
        "libjpegturbo-3.1.1",
        "libopenimageio",
        "OpenColorIO",
        "libtiff",
        "libyamlcpp",
        # TODO: Check this is actually needed, no cmake targets use it - runtime?
        "ftgl-2.1.3-rc5.weta.1",
        "libopenssl",
        "libpython",
        "ffmpeg",
        "openexr",
        "imath",
        "pynanobind-2.8.0",
        "imgui-1.91.9-508d0bc",
        "imgui_node_editor-2025.03.25-dae8edc",
        "imgui_backend_qt-2024.12.11-023345c",
        "implot-2025.04.03-61af48e",
        # TODO: runtime req instead?
        "pyimgui-2.0.0",
        "openjph-0.21.3",
        "libaja-17.1.3",
        "libaio-0.3.112",
        "libasound2-1.2.6.1",
        "vulkansdk",
        "libfreeglut",
    ]

    for _ in conf.buildmatrix_make_variants("WetaVFXPlatform", filter_variants=["VP23"]):
        conf.buildmatrix_oz(area="/", limits=requirements, prefer_min=False)
        conf.env.env["HTTPS_PROXY"] = "www-proxy.wetafx.co.nz:3128"
        conf.env.env["HTTP_PROXY"] = "www-proxy.wetafx.co.nz:3128"
        conf.env.env["NO_PROXY"] = "localhost,127.0.0.0/8,wetafx.co.nz"
        conf.env.env["https_proxy"] = "www-proxy.wetafx.co.nz:3128"
        conf.env.env["http_proxy"] = "www-proxy.wetafx.co.nz:3128"
        conf.env.env["no_proxy"] = "localhost,127.0.0.0/8,wetafx.co.nz"

        conf.env.env["WETA_Qt5_CMAKE_CONFIG_DIR"] = f"{conf.env.QTDIR}/lib/cmake"
        conf.env.env["WETA_aja_CMAKE_CONFIG_DIR"] = f"{conf.path}/tmp/{conf.env.BOB_ABI}"
        conf.env.env["WETA_ffmpeg_CMAKE_CONFIG_DIR"] = f"{conf.path}/tmp/{conf.env.BOB_ABI}"

        # TODO: Fix up base paks
        conf.env.env["LIBIMGUI_BACKEND_QT_TYPE"] = "shared"
        conf.env.env["LIBIMGUI_NODE_EDITOR_TYPE"] = "header_only"
        conf.env.env["LIBOPENEXR_LIB"] = "OpenEXR"
        conf.env.env["LIBIMATH_LIB"] = "Imath"
        conf.env.env["LIBFREEGLUT_LIB"] = "glut"
        conf.env.env["LIBVULKANSDK_TYPE"] = "shared"
        conf.env.env["LIBVULKANSDK_LIB"] = "vulkan"

        # Configure the required executables:
        conf.find_program("moc")
        conf.find_program("uic")
        conf.find_program("rcc")

        configure_cmake_folder(
            conf,
            str(conf.path),
            RV_DEPS_QT5_LOCATION=conf.env.QTDIR,
            # Disable target requirements on link to allow linking against rt and dl
            CMAKE_LINK_LIBRARIES_ONLY_TARGETS="OFF",
            Qt5Core_MOC_EXECUTABLE=conf.env.MOC[0],
            Qt5Widgets_UIC_EXECUTABLE=conf.env.UIC[0],
            Qt5Core_RCC_EXECUTABLE=conf.env.RCC[0],
        )


# -------------------------------------------------
# Build
# -------------------------------------------------


def build(bld):

    for _ in bld.iterVariants(category="WetaVFXPlatform"):
        vfx_build_task = bld.cmakeBuild(
            name="build",
        )

        bld.cmakeInstall(
            name="install",
            dependsOn=[vfx_build_task],
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
