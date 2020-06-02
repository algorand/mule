import platform

def get_os_type():
    return platform.system().lower()

def get_cpu_arch_type():
    arch = platform.machine()
    if arch == "x86_64":
        return "amd64"
    elif arch == "armv6l":
        return "arm"
    elif arch == "armv7l":
        return "arm"
    elif arch == "aarch64":
        return "arm64"
    return "unknown"
