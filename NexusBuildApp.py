import os
import traceback
import sys
import getopt
from os.path import exists
from NexusPackager import NexusPackager
from Utils import Utils


class NexusBuildApp:

    APP_NAME = "NexusBuild"
    APP_VERSION = "0.1.0"
    SUCCESS = 0
    RET_ERROR_INVALID_ARGS = 1
    RET_ERROR_PARSING_ARGS = 2

    @staticmethod
    def help_menu():
        print("Packager for mods in the nexus.")

    @staticmethod
    def print_version():
        print("")
        print(NexusBuildApp.APP_NAME, " -- ", NexusBuildApp.APP_VERSION)
        print("")

    @staticmethod
    def print_license():
        license_txt = """
MIT License

Copyright (c) 2022 Anderson Paschoalon

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.        
        """
        print(license_txt)

    @staticmethod
    def create_template(project_name):
        project_name = str(project_name).strip()
        try:
            NexusPackager.create_nxproj_template(project_name)
        except:
            Utils.echo_error("Error Creating template.")
            traceback.print_exc()
        return 0

    @staticmethod
    def package_project(project_path):
        ret_val = True
        all_in_dir = os.listdir(project_path)
        list_projs = []
        for item in all_in_dir:
            if str(item).endswith(NexusPackager.EXT_NXPROJ):
                list_projs.append(str(item))
        Utils.echo_info("List of projects: " + str(list_projs))
        for proj in list_projs:
            Utils.echo_info("* Processing project " + proj + "...")
            ret, builder = NexusPackager.parse_build_file(proj)
            if ret:
                builder.package()
            else:
                Utils.echo_error("--> Error processing project " + proj + ".")
                ret_val = False
        Utils.echo_info("Processing projects procedure completed.")
        return ret_val

    @staticmethod
    def error_handler(ret_val):
        # sys.exit(NexusBuildApp.RET_ERROR_INVALID_ARGS)
        return -1

    @staticmethod
    def main(argv):
        operation_number = 0
        arg_str = ""
        ret_val = -1
        try:
            opts, args = getopt.getopt(argv, "p:t:h:v:l", ["path=", "template=", "help", "version", "license"])
        except getopt.GetoptError:
            print("**Error parsing arguments.")
            traceback.print_exc()
            sys.exit(NexusBuildApp.RET_ERROR_PARSING_ARGS)
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                NexusBuildApp.help_menu()
                return
            elif opt in ("-l", "--license"):
                NexusBuildApp.print_license()
                return
            elif opt in ("-v", "--version"):
                NexusBuildApp.print_version()
                return
            elif opt in ("--template", "-t"):
                operation_number = 1
                arg_str = arg
            elif opt in ("-p", "--path"):
                operation_number = 2
                arg_str = arg
        if operation_number == 1:
            ret_val = NexusBuildApp.create_template(project_name=arg_str)
            NexusBuildApp.error_handler(ret_val)
        elif operation_number == 2:
            ret_val = NexusBuildApp.package_project(project_path=arg_str)
            NexusBuildApp.error_handler(ret_val)


