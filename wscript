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
ABI_RANGE = "gcc-9.4.0<gcc-9.5|gcc-171<gcc-172"


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

    app_version = conf.makeLibPak(
        name=conf.env.WAK_APP_NAME,
        version=conf.env.WAK_APP_VERSION,
        prefix="",  # remove "lib" prefix
        type="static",
        includes="${PREFIX}/%(BOB_ABI)s/include",
        lib=conf.env.WAK_APP_NAME,
        libpath=["${PREFIX}/%(BOB_ABI)s/lib"],
        requires={
            "abi": {"ver_range": ABI_RANGE},
        },
        buildRequires={
            "abi": {"ver_range": ABI_RANGE},
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
    ]

    for _ in conf.buildmatrix_make_variants("WetaVFXPlatform", filter_variants=["VP23"]):
        conf.buildmatrix_oz(area="/", limits=requirements, prefer_min=False)
        conf.env.env["HTTPS_PROXY"] = "www-proxy.wetafx.co.nz:3128"
        conf.env.env["HTTP_PROXY"] = "www-proxy.wetafx.co.nz:3128"
        conf.env.env["NO_PROXY"] = "localhost,127.0.0.0/8,wetafx.co.nz"
        conf.env.env["https_proxy"] = "www-proxy.wetafx.co.nz:3128"
        conf.env.env["http_proxy"] = "www-proxy.wetafx.co.nz:3128"
        conf.env.env["no_proxy"] = "localhost,127.0.0.0/8,wetafx.co.nz"
        configure_cmake_folder(
            conf,
            str(conf.path),
            RV_DEPS_QT5_LOCATION=conf.env.QTDIR,
            # Disable target requirements on link to allow linking against rt and dl
            CMAKE_LINK_LIBRARIES_ONLY_TARGETS="OFF",
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
