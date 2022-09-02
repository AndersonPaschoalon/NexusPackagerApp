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
        print("todo")

    @staticmethod
    def print_version():
        print("")
        print(NexusBuildApp.APP_NAME, " -- ", NexusBuildApp.APP_VERSION)
        print("")

    @staticmethod
    def print_license():
        print("todo")

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
        return 1

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


