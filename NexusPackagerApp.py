import os
import traceback
import sys
import getopt
from NexusPackager import NexusPackager
from Utils import Utils
from Cd import Cd


class NexusPackagerApp:
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
    LICENCE = """
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
    APP_MANPAGE = """
    NAME
        NexusPackagerApp.exe - application to help package generic mods for nexus.
    
    SYNOPSIS
        NexusPackagerApp.exe [-p game-installation-folder] [-f nxproj-file-path] 

    USAGE
        Package all your projects at game-installation-folder:
            NexusPackagerApp.exe -p game-installation-folder
        Package an specific project:
            NexusPackagerApp.exe -f nxproj-file-path
        Crete a templete for a nxproj file:
            NexusPackagerApp.exe -t template-file-name
        Check if a nxproj file is in the right format.
            NexusPackagerApp.exe -c nxproj-file-path
    
    DESCRIPTION 
	    About the Application:

        Nexus Build App is a  simple packager for Nexus mods. You will be able to
        define rules on what files should be searched in your working directory,
        copy and zip them.
    
        This expecially usefull if you follow some naming conventions for your
        files. For example, if all your files starts with a giver prefix name, 
        this application will be able to search all of them, and pack them with
        the same directory hierarchy into a zip filein any direcotry of your 
        system. But you can also include files that dont follow any specified rule
        as well.
        
        This application is designed to process .nxproj file, written in XML 
        format. This file must contains a set of rules so the application can
        find all the required files to pack.
    
        This application will also generate an uninstall bat script, which can be 
        executed from the mod installation directory. This script will delete all
        unpacked files from the zip.
        
        About nxproj files:
        
        If you are familiar with build files such as Makefiles, well, thats the 
        idea. The idea is to write once the rules to package a mod, and then every  
        time you build it, no file will be missed. Our "makefile" is a .nxproj file 
        (Nexus Project file). They are actually XML files, with the following tags:
        *	game_path: The Path where the game is installed. If this file is placed
            at the root folder of the game, this parameter may be filled with "."
            instead of the absoluth pack of the game.
        *	plugin_folder: If this tag is defined, the files are going to be 
            searched in this folder folder only. Otherwise they are going to be
            searched all over the game_path folder. On Skyrim for example, all the
            mod files are located in the Data folder.
        *	package_name: Name of the Zip package that is going to be created.
        *	build_dst: Directory where the zip will be saved. This directory will
            be created where the application is executed.
        *	rules: This tag contains a set of rules that are going to be followed 
            to search the files.
        * 	rules/hardcoded_files: Any file listed here will be included. The files
            must be comma separated. The absolute path of the file will be 
            <game_path>/<plugin_folder>/<hardcoded_file>. This tag should be used 
            for files that do not follow prefix rules.
        *	rules/prefix_files: For files that used prefix rules, this tag can be 
            used instead. Files whose name starts with the prefix will be included.
        *	rules/prefix_accepted_extensions: Only files with the extensions 
            included here (comma separated) will be included in the package.
        *	rules/prefix_search_dirs: directory where the files will be searched.
    
        Use-case:
        
        Supose you are executing NexusBuildApp.exe from you desktop, and you 
        created a nxproj file called MyMod in your Skyrim installation folder. 
        Supose your mod does have the following files:
        *	An main file placed at the Data folder called MyMod.esp
        *	Some .pex scripts files, all starting with MyMod_ prefix: 
        * 	You want your mod package to be created in a Release folder in your 
            desktop.
        *	You want the zip file to be called MyModPackage
        This one is therefore a valid nxproj file:
        <build>
            <game_path>
                .
            </game_path>
            <plugin_folder>
                Data
            </plugin_folder>
            <package_name>
                MyModPackage
            </package_name>
            <build_dst>
                Release
            </build_dst>
            <rules>
                <hardcoded_files>
                    MyMod.esp,
                </hardcoded_files>
    
                <prefix_files>
                    MyMod_
                </prefix_files>
                <prefix_accepted_extensions>
                    .pex,
                </prefix_accepted_extensions>
                <prefix_search_dirs>
                    scripts,
                </prefix_search_dirs>
            </rules>
        </build>
        
        Rename it to 
            MyMod.nxproj
    
        Place this file at:
            C:\\Program Files (x86)\Steam\steamapps\common\Skyrim
            
        To package your mod, type in the command line the following command:
            NexusPackagerApp.exe -p "C:\\Program Files (x86)\Steam\steamapps\common\Skyrim"
        
        NexusPackagerApp will search for any nxproj file, and execute this rules.
        At the end, you will have a folder "Release" created in your desktop, and 
        a MyModPackage.zip inside it.


    
    
    OPTIONS
    
    
    """

    @staticmethod
    def help_menu():
        print(NexusPackagerApp.APP_MANPAGE)
        print("")
        return NexusPackagerApp.SUCCESS

    @staticmethod
    def print_version():
        """
        Prints project version
        :return:
        """
        print("")
        print(NexusPackagerApp.APP_NAME, " -- ", NexusPackagerApp.APP_VERSION)
        print("")
        return NexusPackagerApp.SUCCESS

    @staticmethod
    def print_license():
        """
        Prints project licence.
        :return:
        """
        print(NexusPackagerApp.LICENCE)
        return NexusPackagerApp.SUCCESS

    @staticmethod
    def check(project_file):
        """
        Just checks if a nxproject file is in the right format.
        :param project_file:
        :return:
        """
        if not os.path.exists(project_file):
            Utils.echo_error("Error: Cannot find project file <" + project_file + "> !")
            return NexusPackagerApp.ERR0R_DIR_DO_NOT_EXIT
        Utils.echo_info("* Processing project " + project_file + "...")
        ret_parse, builder = NexusPackager.parse_build_file(project_file)
        if not ret_parse:
            Utils.echo_error("--> Error processing project " + project_file + ".")
            return NexusPackagerApp.ERROR_INVALID_PROJ_FILE
        Utils.echo_info("Checking procedure completed. No error was found.")
        return NexusPackagerApp.SUCCESS

    @staticmethod
    def create_template(project_name):
        project_name = str(project_name).strip()
        try:
            NexusPackager.create_nxproj_template(project_name)
        except:
            Utils.echo_error("Error Creating template.")
            traceback.print_exc()
            return NexusPackagerApp.ERROR_CREATING_FILE
        return NexusPackagerApp.SUCCESS

    @staticmethod
    def package_project(project_file):
        ret_val = NexusPackagerApp.SUCCESS
        if not os.path.exists(project_file):
            Utils.echo_error("Error: Cannot find project file <" + project_file + "> !")
            return NexusPackagerApp.ERR0R_FILE_DO_NOT_EXIT

        Utils.echo_info("* Processing project " + project_file + "...")
        ret_parse, builder = NexusPackager.parse_build_file(project_file)
        if ret_parse:
            builder.package()
        else:
            Utils.echo_error("--> Error processing project " + project_file + ".")
            ret_val = NexusPackagerApp.ERROR_PACKAGING_PROJECT

        Utils.echo_info("Processing projects procedure completed.")
        return ret_val

    @staticmethod
    def package_projects(project_path):
        ret_val = NexusPackagerApp.SUCCESS
        if not os.path.isdir(project_path):
            Utils.echo_error("Error, project path <" +
                             str(project_path) +
                             "> is not a valid directory or do not exist!")
            return NexusPackagerApp.ERR0R_FILE_DO_NOT_EXIT

        all_in_dir = os.listdir(project_path)
        list_projs = []
        for item in all_in_dir:
            if str(item).endswith(NexusPackager.EXT_NXPROJ):
                list_projs.append(str(item))

        if len(list_projs) == 0:
            Utils.echo_warn("No valid project found at directory <" +
                            str(project_path) +
                            ">. NexusBuild projects files must end with the extension " + NexusPackager.EXT_NXPROJ)
            return NexusPackagerApp.SUCCESS

        Utils.echo_info("List of projects: " + str(list_projs))
        for proj in list_projs:
            Utils.echo_info("* Processing project " + proj + "...")
            ret_parse = False
            builder = None
            with Cd(project_path):
                ret_parse, builder = NexusPackager.parse_build_file(proj)
            if ret_parse:
                builder.package()
            else:
                Utils.echo_error("--> Error processing project " + proj + ".")
                return NexusPackagerApp.ERROR_PACKAGING_PROJECT

        Utils.echo_info("Processing projects procedure completed.")
        return ret_val

    @staticmethod
    def error_handler(ret_val):
        # error system
        if ret_val == NexusPackagerApp.ERROR_DEFAULT:
            Utils.echo_error("ERROR_DEFAULT")
        elif ret_val == NexusPackagerApp.ERROR_PARSING_ARGS:
            Utils.echo_error("ERROR_PARSING_ARGS")
        elif ret_val == NexusPackagerApp.ERROR_INVALID_ARGS:
            Utils.echo_error("ERROR_INVALID_ARGS")
        elif ret_val == NexusPackagerApp.ERROR_EXCEPTION:
            Utils.echo_error("ERROR_EXCEPTION")
        elif ret_val == NexusPackagerApp.ERR0R_FILE_DO_NOT_EXIT:
            Utils.echo_error("ERR0R_FILE_DO_NOT_EXIT")
        elif ret_val == NexusPackagerApp.ERROR_CREATING_FILE:
            Utils.echo_error("ERROR_CREATING_FILE")
        elif ret_val == NexusPackagerApp.ERR0R_DIR_DO_NOT_EXIT:
            Utils.echo_error("ERR0R_DIR_DO_NOT_EXIT")
        # processing project errors
        elif ret_val == NexusPackagerApp.ERROR_INVALID_PROJ_FILE:
            Utils.echo_error("ERROR_INVALID_PROJ_FILE")
        elif ret_val == NexusPackagerApp.ERROR_PACKAGING_PROJECT:
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
            sys.exit(NexusPackagerApp.ERROR_PARSING_ARGS)
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                NexusPackagerApp.help_menu()
                return
            elif opt in ("-v", "--version"):
                NexusPackagerApp.print_version()
                return
            elif opt in ("-l", "--license"):
                NexusPackagerApp.print_license()
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
            ret_val = NexusPackagerApp.check(project_file=arg_str)
            NexusPackagerApp.error_handler(ret_val)
        elif operation_number == 2:
            ret_val = NexusPackagerApp.package_project(project_file=arg_str)
            NexusPackagerApp.error_handler(ret_val)
        elif operation_number == 3:
            ret_val = NexusPackagerApp.package_projects(project_path=arg_str)
            NexusPackagerApp.error_handler(ret_val)
        elif operation_number == 4:
            ret_val = NexusPackagerApp.create_template(project_name=arg_str)
            NexusPackagerApp.error_handler(ret_val)

        return ret_val


if __name__ == '__main__':
    ret = NexusPackagerApp.ERROR_DEFAULT
    try:
        ret = NexusPackagerApp.main(sys.argv[1:])
    except:
        ret = NexusPackagerApp.ERROR_EXCEPTION
        traceback.print_exc()
        NexusPackagerApp.error_handler(ret)
    sys.exit(ret)
