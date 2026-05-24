import argparse
import os
import zipfile

KIVY_DEPS_ROOT = os.environ.get("KIVY_DEPS_ROOT", None)
if not KIVY_DEPS_ROOT:
    print(
        "KIVY_DEPS_ROOT environment variable is not set. "
        "Please set it to the path where Android SDL2 libraries are located."
    )
    raise EnvironmentError("KIVY_DEPS_ROOT environment variable is not set")


def get_abi_from_wheel(wheel_name):
    """Determine ABI from wheel filename platform tag."""
    if "arm64_v8a" in wheel_name or "aarch64" in wheel_name:
        return "arm64-v8a"
    elif "x86_64" in wheel_name:
        return "x86_64"
    return None


def add_android_libs_to_wheels(wheels_path: str):
    libs_base = os.path.join(KIVY_DEPS_ROOT, "dist", "libs")
    if not os.path.exists(libs_base):
        raise FileNotFoundError(
            "Android libs folder does not exist at path: {}".format(libs_base)
        )

    if not os.path.exists(wheels_path):
        raise FileNotFoundError(
            "Specified folder does not exist at path: {}".format(wheels_path)
        )

    for wheel in os.listdir(wheels_path):
        if not wheel.endswith(".whl"):
            continue

        abi = get_abi_from_wheel(wheel)
        if not abi:
            print(
                "Could not determine ABI for wheel: {}, skipping".format(wheel)
            )
            continue

        libs_dir = os.path.join(libs_base, abi)
        if not os.path.exists(libs_dir):
            raise FileNotFoundError(
                "Libs folder for ABI {} does not exist at: {}".format(
                    abi, libs_dir
                )
            )

        so_files = [f for f in os.listdir(libs_dir) if f.endswith(".so")]
        if not so_files:
            print("No .so files found in {}".format(libs_dir))
            continue

        wheel_path = os.path.join(wheels_path, wheel)
        with zipfile.ZipFile(
            wheel_path,
            "a",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=6,
        ) as whl:
            print("Adding Android .so files to wheel: {}".format(wheel_path))
            for so_file in so_files:
                file_path = os.path.join(libs_dir, so_file)
                arcname = os.path.join(".libs", abi, so_file)
                print("  Adding {} as {}".format(so_file, arcname))
                whl.write(file_path, arcname)

            # Inject SDL2 Java sources under .java/ (mirrors .libs/ layout).
            # ABI-independent, so we add the whole tree once per wheel.
            java_dir = os.path.join(KIVY_DEPS_ROOT, "dist", "java")
            if os.path.isdir(java_dir):
                print("Adding Android Java sources to wheel: {}".format(wheel_path))
                for root, _dirs, files in os.walk(java_dir):
                    for fname in files:
                        file_path = os.path.join(root, fname)
                        rel = os.path.relpath(file_path, java_dir)
                        arcname = os.path.join(".java", rel)
                        print("  Adding {} as {}".format(rel, arcname))
                        whl.write(file_path, arcname)
            else:
                print(
                    "No Java sources found at {}, skipping .java/ injection".format(
                        java_dir
                    )
                )

            # Inject SDL2 headers under .include/ (mirrors .libs/ / .java/ layout).
            # ABI-independent, so we add the whole tree once per wheel.
            include_dir = os.path.join(KIVY_DEPS_ROOT, "dist", "include")
            if os.path.isdir(include_dir):
                print("Adding Android SDL headers to wheel: {}".format(wheel_path))
                for root, _dirs, files in os.walk(include_dir):
                    for fname in files:
                        file_path = os.path.join(root, fname)
                        rel = os.path.relpath(file_path, include_dir)
                        arcname = os.path.join(".include", rel)
                        print("  Adding {} as {}".format(rel, arcname))
                        whl.write(file_path, arcname)
            else:
                print(
                    "No headers found at {}, skipping .include/ injection".format(
                        include_dir
                    )
                )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Add Android .so files in .libs/{ABI}/ folder "
            "to all wheels in the specified directory."
        )
    )
    parser.add_argument(
        "wheels_path",
        help=(
            "Path to the directory containing the wheels "
            "to which Android .so libraries should be added."
        ),
    )
    args = parser.parse_args()

    add_android_libs_to_wheels(args.wheels_path)
