from setuptools import setup, find_packages, Command, Extension
import sys
import os
import subprocess

if sys.version_info < (3, 5):
    raise Exception("This package requires Python 3.5 or higher.")


PACKAGE_NAME = "isk"
VERSION = "0.10.0"
QUICK_DESCRIPTION = "Similar image search library and server, based on isk-daemon"
SOURCE_DIR_NAME = "src"


def readme():
    with open("README.md", "r", encoding="utf-8") as f:
        return f.read()


def add_src_to_syspath():
    currentdir = os.path.dirname(os.path.realpath(__file__))
    pkg_source_dir = os.path.join(currentdir, SOURCE_DIR_NAME)
    sys.path.insert(0, pkg_source_dir)


def prepare_build_kwargs():

    library_dirs = []
    include_dirs = []
    libraries = []
    extra_link_args = ["-g"]
    imagclib = []
    extra_compile_args = ["-DImMagick", "-DLinuxBuild", "-g"]

    pathvar = os.environ.get("PATH", "")
    for pv in map(lambda x: x.rstrip("/"), pathvar.split(':')):
        if os.path.exists(os.path.join(pv, 'Magick++-config')):
            break  # pv now holds directory in which Magick++-config was found
    else:
        print(
            "--- ERROR ---\n"
            "Unable to find Magick++-config. \n"
            "Are you sure you have ImageMagick and it's development files installed correctly?"
        )
        quit()

    imagcflag = subprocess.check_output(["Magick++-config", "--cxxflags", "--cppflags"], universal_newlines=True)
    if "-I" in imagcflag:
        if not include_dirs:  # Extract include dir from latter command output and append to include_dirs
            include_dirs.append([i[2:] for i in imagcflag.split(' ') if i.startswith("-I")][0])
        imagcflag = imagcflag.replace("\n", " ")
        imagcflag = imagcflag.split(' ')

        imagclib = subprocess.check_output(["Magick++-config", "--ldflags", "--libs"], universal_newlines=True)
        imagclib = imagclib.replace("\n", " ")
        imagclib = imagclib.split(' ')

    extra_compile_args += list(filter(lambda x: bool(x), map(lambda y: y.strip(), imagcflag)))
    extra_link_args += list(filter(lambda x: bool(x), map(lambda y: y.strip(), imagclib)))

    print("Found the following arguments:")
    print("extra_compile_args", extra_compile_args)
    print("extra_link_args", extra_link_args)

    kwargs = {
        "libraries": libraries,
        "extra_compile_args": extra_compile_args,
        "extra_link_args": extra_link_args,
        "include_dirs": include_dirs,
        "library_dirs": library_dirs,
    }
    return kwargs


build_kwargs = prepare_build_kwargs()


setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=QUICK_DESCRIPTION,
    author="Dmitry Litvinenko",
    author_email="anti1869@gmail.com",
    long_description=readme(),
    url="https://github.com/anti1869/isk",
    package_dir={'': SOURCE_DIR_NAME},
    packages=find_packages(SOURCE_DIR_NAME, exclude=('*.tests',)),
    include_package_data=True,
    zip_safe=False,
    package_data={},
    license="GPLv3",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    ext_modules=[
        Extension(
            "_imgdb", [
                "src/isk/imgSeekLib/imgdb.cpp",
                "src/isk/imgSeekLib/haar.cpp",
                "src/isk/imgSeekLib/imgdb.i",
                "src/isk/imgSeekLib/bloom_filter.cpp",
                ],
            swig_opts=['-c++'],
            **build_kwargs,
        )],
    install_requires=[
        "colorlog",
    ],
)
