import os
import traceback
import sys
import getopt
from NexusPackager import NexusPackager
from Utils import Utils


class NexusBuildApp:
    APP_NAME = "NexusBuild"
    APP_VERSION = "0.1.0"
    SUCCESS = 0
    # error system
    ERROR_DEFAULT = 1
    ERROR_PARSING_ARGS = 2
    ERROR_INVALID_ARGS = 3
    ERROR_EXCEPTION = 4
    ERR0R_FILE_DO_NOT_EXIT = 5
    ERROR_CREATING_FILE = 6
    ERR0R_DIR_DO_NOT_EXIT = 7
    # processing project errors
    ERROR_INVALID_PROJ_FILE = 10
    ERROR_PACKAGING_PROJECT = 11

    @staticmethod
    def help_menu():
        print("                          ===>>> NEXUS BUILD APP <<<===                                          ")
        print("")
        print("    Nexus Build App is a  simple packager for Nexus mods. This application is designed to process a")
        print(".nxproj file, written in XML format. This files contains a set of rules to find all the files of a mod")
        print("and copy them into a zip package.It also generate an uninstall bat script, which can be executed delete")
        print("all the files.")
        print("The .nxproj file defines:")
        print(" * game_path: The Path where the game is installed.")
        print(" * plugin_folder: if this tag is defined, the files are going to be searched in the folder folder")
        print("   <game_path>/<plugin_folder>. If it is not, they are going to be searched at the root folder")
        print("   of the game")
        print(" * package_name: Name of the Zip package that is going to be created.")
        print(" * build_dst: Directory where the zip will be saved.")
        print(" * rules: This tag contains a set of rules that are going to be followed to search the files.")
        print(" * hardcoded_files: Any file listed here will be included. The files must be comma separated. The ")
        print("   absolute path of the file will be <game_path>/<plugin_folder>/<hardcoded_file>. ")
        print("   This tag should be used for files that do not follow prefix rules.")
        print(" * prefix_files: For files that used prefix rules, this tag can be used instead. Files whose name")
        print("   starts with the prefix will be included.")
        print(" * prefix_accepted_extensions: Only files with the extensions included here (comma separated) will be")
        print("   included in the package.")
        print(" * prefix_search_dirs: directory where the files will be searched.")
        print("")
        print("Usage:")
        print("nexus-build-app.exe <option> [<argument>]")
        print("    -v|--version: show current version of this app.")
        print("    -l|--license: display the license of this app.")
        print("    -h|--help: display this help menu")
        print("    -f|-file: package using a .nxproj ")
        print("")
        print("")
        print("")
        return NexusBuildApp.SUCCESS

    @staticmethod
    def print_version():
        """
        Prints project version
        :return:
        """
        print("")
        print(NexusBuildApp.APP_NAME, " -- ", NexusBuildApp.APP_VERSION)
        print("")
        return NexusBuildApp.SUCCESS

    @staticmethod
    def print_license():
        """
        Prints project licence.
        :return:
        """
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
        return NexusBuildApp.SUCCESS

    @staticmethod
    def check(project_file):
        """
        Just checks if a nxproject file is in the right format.
        :param project_file:
        :return:
        """
        if not os.path.exists(project_file):
            Utils.echo_error("Error: Cannot find project file <" + project_file + "> !")
            return NexusBuildApp.ERR0R_DIR_DO_NOT_EXIT
        Utils.echo_info("* Processing project " + project_file + "...")
        ret_parse, builder = NexusPackager.parse_build_file(project_file)
        if not ret_parse:
            Utils.echo_error("--> Error processing project " + project_file + ".")
            return NexusBuildApp.ERROR_INVALID_PROJ_FILE
        Utils.echo_info("Checking procedure completed. No error was found.")
        return NexusBuildApp.SUCCESS

    @staticmethod
    def create_template(project_name):
        project_name = str(project_name).strip()
        try:
            NexusPackager.create_nxproj_template(project_name)
        except:
            Utils.echo_error("Error Creating template.")
            traceback.print_exc()
            return NexusBuildApp.ERROR_CREATING_FILE
        return NexusBuildApp.SUCCESS

    @staticmethod
    def package_project(project_file):
        ret_val = NexusBuildApp.SUCCESS
        if not os.path.exists(project_file):
            Utils.echo_error("Error: Cannot find project file <" + project_file + "> !")
            return NexusBuildApp.ERR0R_FILE_DO_NOT_EXIT

        Utils.echo_info("* Processing project " + project_file + "...")
        ret_parse, builder = NexusPackager.parse_build_file(project_file)
        if ret_parse:
            builder.package()
        else:
            Utils.echo_error("--> Error processing project " + project_file + ".")
            ret_val = NexusBuildApp.ERROR_PACKAGING_PROJECT

        Utils.echo_info("Processing projects procedure completed.")
        return ret_val

    @staticmethod
    def package_projects(project_path):
        ret_val = NexusBuildApp.SUCCESS
        if not os.path.isdir(project_path):
            Utils.echo_error("Error, project path <" +
                             str(project_path) +
                             "> is not a valid directory or do not exist!")
            return NexusBuildApp.ERR0R_FILE_DO_NOT_EXIT

        all_in_dir = os.listdir(project_path)
        list_projs = []
        for item in all_in_dir:
            if str(item).endswith(NexusPackager.EXT_NXPROJ):
                list_projs.append(str(item))

        if len(list_projs) == 0:
            Utils.echo_warn("No valid project found at directory <" +
                            str(project_path) +
                            ">. NexusBuild projects files must end with the extension " + NexusPackager.EXT_NXPROJ)
            return NexusBuildApp.SUCCESS

        Utils.echo_info("List of projects: " + str(list_projs))
        for proj in list_projs:
            Utils.echo_info("* Processing project " + proj + "...")
            ret_parse, builder = NexusPackager.parse_build_file(proj)
            if ret_parse:
                builder.package()
            else:
                Utils.echo_error("--> Error processing project " + proj + ".")
                return NexusBuildApp.ERROR_PACKAGING_PROJECT

        Utils.echo_info("Processing projects procedure completed.")
        return ret_val

    @staticmethod
    def error_handler(ret_val):
        # error system
        if ret_val == NexusBuildApp.ERROR_DEFAULT:
            Utils.echo_error("ERROR_DEFAULT")
        elif ret_val == NexusBuildApp.ERROR_PARSING_ARGS:
            Utils.echo_error("ERROR_PARSING_ARGS")
        elif ret_val == NexusBuildApp.ERROR_INVALID_ARGS:
            Utils.echo_error("ERROR_INVALID_ARGS")
        elif ret_val == NexusBuildApp.ERROR_EXCEPTION:
            Utils.echo_error("ERROR_EXCEPTION")
        elif ret_val == NexusBuildApp.ERR0R_FILE_DO_NOT_EXIT:
            Utils.echo_error("ERR0R_FILE_DO_NOT_EXIT")
        elif ret_val == NexusBuildApp.ERROR_CREATING_FILE:
            Utils.echo_error("ERROR_CREATING_FILE")
        elif ret_val == NexusBuildApp.ERR0R_DIR_DO_NOT_EXIT:
            Utils.echo_error("ERR0R_DIR_DO_NOT_EXIT")
        # processing project errors
        elif ret_val == NexusBuildApp.ERROR_INVALID_PROJ_FILE:
            Utils.echo_error("ERROR_INVALID_PROJ_FILE")
        elif ret_val == NexusBuildApp.ERROR_PACKAGING_PROJECT:
            Utils.echo_error("ERROR_PACKAGING_PROJECT")

    @staticmethod
    def main(argv):
        Utils.echo_debug("Starting nexus build app...")
        operation_number = 0
        arg_str = ""
        ret_val = -1
        try:
            opts, args = getopt.getopt(argv, "c:f:p:t:hvl", ["check=",  # 1
                                                             "file=",  # 2
                                                             "path=",  # 3
                                                             "template=",  # 4
                                                             "help",
                                                             "version",
                                                             "license"])
        except getopt.GetoptError:
            print("**Error parsing arguments.")
            traceback.print_exc()
            sys.exit(NexusBuildApp.ERROR_PARSING_ARGS)
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                NexusBuildApp.help_menu()
                return
            elif opt in ("-v", "--version"):
                NexusBuildApp.print_version()
                return
            elif opt in ("-l", "--license"):
                NexusBuildApp.print_license()
                return
            elif opt in ("-c", "--check"):
                operation_number = 1
                arg_str = arg
            elif opt in ("-f", "--file"):
                operation_number = 2
                arg_str = arg
            elif opt in ("-p", "--path"):
                operation_number = 3
                arg_str = arg
            elif opt in ("--template", "-t"):
                operation_number = 4
                arg_str = arg

        if operation_number == 1:
            ret_val = NexusBuildApp.check(project_file=arg_str)
            NexusBuildApp.error_handler(ret_val)
        elif operation_number == 2:
            ret_val = NexusBuildApp.package_project(project_file=arg_str)
            NexusBuildApp.error_handler(ret_val)
        elif operation_number == 3:
            ret_val = NexusBuildApp.package_projects(project_path=arg_str)
            NexusBuildApp.error_handler(ret_val)
        elif operation_number == 4:
            ret_val = NexusBuildApp.create_template(project_name=arg_str)
            NexusBuildApp.error_handler(ret_val)

        return ret_val


if __name__ == '__main__':
    ret = NexusBuildApp.ERROR_DEFAULT
    try:
        ret = NexusBuildApp.main(sys.argv[1:])
    except:
        ret = NexusBuildApp.ERROR_EXCEPTION
        traceback.print_exc()
        NexusBuildApp.error_handler(ret)
    sys.exit(ret)
