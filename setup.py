import cx_Freeze

exe = [cx_Freeze.Executable("rocketman.py")]

cx_Freeze.setup( name = "Rocketman", version = "0.2.2", options = {"build_exe": {"packages": ["errno", "os"], "include_files": []}}, executables = exe )