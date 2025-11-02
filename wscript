#! /usr/bin/env python
# -*- coding: utf-8 -*-
"Build definition and execution"

import os


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
            "boost": {"ver_range": "|"},  # Constrained by the VFX variant
            "ffmpeg": {"ver_range": ">=8.0.0-weta.1"},
            "imgui": {"ver_range": "1.91.9-508d0bc<1.92"},
            "imgui_node_editor": {"ver_range": "2025.03.25-dae8edc<2026"},
            "imgui_backend_qt": {"ver_range": "2024.12.11-023345c<2025"},
            "implot": {"ver_range": "2025.04.03-61af48e<2026"},
            "libtiff": {"ver_range": "|"},  # Constrained by the VFX variant
            "OpenColorIO": {"ver_range": "|"},  # Constrained by the VFX variant
            "pyimgui": {"ver_range": "|"},  # Constrained by the python variant
            "pyopengl": {"ver_range": "|"},  # Constrained by the python variant
            "pyopentimelineio": {"ver_range": "|"},  # Constrained by the python variant
            "pynanobind": {"ver_range": "|"},  # Constrained by the python variant
            "pyrequests": {"ver_range": "|"},  # Constrained by the python variant
            "python": {"ver_range": "|"},  # Constrained by the VFX variant
            "pyside": {"ver_range": "|"},  # Constrained by the VFX variant
            "pysix": {"ver_range": "|"},  # Constrained by the python variant
            "qt": {"ver_range": "|"},  # Constrained by the VFX variant
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
                "target": "PYTHONPATH",
                "value": "${PREFIX}/flavor-dbg/WetaVFXPlatform-%(WETA_VFXPLATFORM_ID)s/plugins/Python",
                "action": "env_prp",
            },
            {
                "target": "RV_HOME",
                "value": "${PREFIX}/flavor-opt/WetaVFXPlatform-%(WETA_VFXPLATFORM_ID)s",
                "action": "env_set",
            },
        ],
        **pak_vars,
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
                "target": "PYTHONPATH",
                "value": "${PREFIX}/flavor-dbg/WetaVFXPlatform-%(WETA_VFXPLATFORM_ID)s/plugins/Python",
                "action": "env_prp",
            },
            {
                "target": "RV_HOME",
                "value": "${PREFIX}/flavor-dbg/WetaVFXPlatform-%(WETA_VFXPLATFORM_ID)s",
                "action": "env_set",
            },
        ],
        **pak_vars,
    )

    return [f"{app_version}@now", f"{app_version_dbg}@now"]


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
    conf.env.WAK_SCM_TAG_PREFIX = "weta/openrv-"

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
    paks = make_app_version(conf)

    requirements = [
        "OpenColorIO",
        "bdwgc",
        "bison",
        "cmake",
        "ffmpeg->=8.0.0-weta.1<9",
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
    ]

    for _ in conf.buildmatrix_make_nested_variants(
        ["flavor", "WetaVFXPlatform"],
        category="flavored_platform",
        filter_variants={
            "WetaVFXPlatform": ["VP23"],
        },
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
        conf.env.env[
            "WETA_jpegturbo_CMAKE_CONFIG_DIR"
        ] = f"{conf.path}/tmp/{conf.env.BOB_ABI}"

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

        with conf.makeVariant("package_install"):
            conf.buildmatrix_oz(area="/", add=paks, build=False)


# -------------------------------------------------
# Build
# -------------------------------------------------


def build_install_packages(bld, install_task):

    packages = [
        "additional_nodes-1.2",
        "data_display_indicators-1.2",
        "missing_frame_bling-1.7",
        "pyhello-1.2",
        "session_manager-1.9",
        "annotate-1.20",
        "doc_browser-1.4",
        "multiple_source_media_rep-1.3",
        "pymystuff-1.2",
        "source_setup-4.3",
        "annot_tools-0.1",
        "export_cuts-1.5",
        "node_graph_viz-0.1",
        "pyside_example-1.2",
        "stereo_autoload-1.6",
        "channel_select-1.3",
        "lat_long_viewer-1.2",
        "ocio_source_setup-2.5",
        "rvio_basic_scripts-1.2",
        "stereo_disassembly-1.3",
        "collapse_missing_frames-1.2",
        "layer_select-1.7",
        "openrv_help_menu-1.0",
        "rvnuke-1.12",
        "sync-1.5",
        "custom_lut_menu_mode-2.9",
        "maya_tools-1.6",
        "os_dependent_path_conversion_mode-1.7",
        "scrub_offset-1.6",
        "webview2-0.3",
        "custom_mattes-2.3",
        "media_library_demo-1.0",
        "otio_reader-1.2",
        "sequence_from_file-1.4",
        "window_title-1.6",
    ]

    # Configure this here to avoid 'package_install' being added to bld.env.PREFIX,
    # otherwise we have to use '..' which rvpkg doesn't like
    package_install_dir = f"{bld.env.PREFIX}/plugins"

    tasks = []

    with bld.useVariant("package_install"):
        tasks.append(bld(
            rule=" ".join([
                'rvpkg',
                "-force",
                "-install",
                "-add",
                package_install_dir,
            ] + [" {}".format(os.path.join('build', bld.env.WAK_CMAKE_BUILD_DIR, 'stage', 'packages', f'{package}.rvpkg')) for package in packages]),
            # Depend on the install task to make sure bld.env.PREFIX exists already
            dependsOn=[install_task],
            cwd=bld.path,
            always=True,
        ))

    return tasks


def build(bld):

    install_tasks = []

    for _ in bld.iterVariants(category="flavored_platform"):
        vfx_build_task = bld.cmakeBuild(
            name="build",
        )

        vfx_install_task = bld.cmakeInstall(
            name="install",
            dependsOn=[vfx_build_task],
        )
        install_tasks.append(vfx_install_task)

        build_install_packages(bld, vfx_install_task)

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

    version_check_options = {
        "check_undeclared_python_requirements": {
            # pymu is injected by us here: src/lib/app/PyTwkApp/PyInterface.cpp
            "ignore_modules": ["pymu"]
        }
    }

    bld.runOzPerVersionChecks(
        dependsOn=install_tasks,
        description="Run pak level sanity checks",
        options=version_check_options,
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
