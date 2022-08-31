import ntpath
import os
import traceback
import sys
import os.path
from os.path import exists
from pathlib import Path
from termcolor import colored
import xml.etree.ElementTree as ET
import shutil


# run_<datetime>.log
BSABUILD_LOG_DIR = "Logs\\BsaBuild\\"
BSABUILD_LOG_FILE = "run_{}.log"
ARCHIVE_EXE = "Archive.exe"


def echo_error(message: str):
    print(colored(message, 'red'))


def echo_warn(message: str):
    print(colored(message, 'yellow'))


def echo_info(message: str):
    print(message)


def scandir(dir, ext):    # dir: str, ext: list
    # https://stackoverflow.com/a/59803793/2441026
    subfolders, files = [], []
    for f in os.scandir(dir):
        if f.is_dir():
            subfolders.append(f.path)
        if f.is_file():
            if os.path.splitext(f.name)[1].lower() in ext:
                files.append(f.path)
    for dir in list(subfolders):
        sf, f = scandir(dir, ext)
        subfolders.extend(sf)
        files.extend(f)
    return subfolders, files


def copytree(src: str, dst: str):
    dstfolder = os.path.dirname(dst)
    if not os.path.exists(dstfolder) and dstfolder != "":
        os.makedirs(dstfolder)
    print(src + " -> " + dst)
    shutil.copy(src, dst)


class NexusPackager:
    TAG_GAME_PATH = "game_path"
    TAG_BUILD_DST = "build_dst"
    TAG_TARGET = "target"
    TAG_ROOT = "group_root"
    TAG_RULES = "rules"
    TAG_HARDCODED_FILES = "hardcoded_files"
    TAG_PREFIX_FILES = "prefix_files"
    TAG_PREFIX_ACCEPTED_EXTENSIONS = "prefix_accepted_extensions"
    TAG_PREFIX_SEARCH_DIRS = "prefix_search_dirs"
    CSV_SEPARATOR = ","
    SKIP_LINE = "\n"

    @staticmethod
    def create_unninstall_script(project_name: str, list_all_files: [], build_dst, group_root = ""):
        script_name = "unninstall." + project_name + ".bat"
        # start of script
        script_content =  "@echo off" +  NexusPackager.SKIP_LINE
        script_content += "setlocal" + NexusPackager.SKIP_LINE
        script_content += ":PROMPT" + NexusPackager.SKIP_LINE
        script_content += "SET /P AREYOUSURE=Are you sure you want to unninstall " + project_name + "(Y/[N])?"+ NexusPackager.SKIP_LINE
        script_content += 'IF /I "%AREYOUSURE%" NEQ "Y" GOTO END' + NexusPackager.SKIP_LINE
        script_content += NexusPackager.SKIP_LINE

        for file_name in list_all_files:
            if str(file_name).strip() != "":
                # delete command
                script_content += 'DEL "' + file_name + + '"' + NexusPackager.SKIP_LINE

        # end of the script
        script_content += ":END" + NexusPackager.SKIP_LINE
        script_content += "endlocal" + NexusPackager.SKIP_LINE
        script_content += NexusPackager.SKIP_LINE

        # dst directory where the unninstall script will be saved.
        path_script = os.path.join(".", build_dst, group_root, script_name)

        # create script
        with open(path_script, 'w') as f:
            f.write(script_content)

    @staticmethod
    def zip_project(proj_name: str, build_dst: str):
        output_filename = proj_name + ".zip"
        dir_name = os.path.join(".", build_dst)
        shutil.make_archive(output_filename, 'zip', dir_name)

    @staticmethod
    def parse_build_file(build_rules_file: str):
        """
        This method parses the build file rules and creates a build object that stores all neccessary rules to
        package the right files.
        :param build_rules_file: ncproj file wiht all necessary rules.
        :return: returns (True, BuildObject) if the nxproj file was rightly parsed, (False, None) otherwise.
        """
        path_rules = Path(build_rules_file)
        if not path_rules.is_file():
            echo_error(str.format("Config file {} does not exist!", build_rules_file))
            return False, None

        tree = ET.parse(path_rules)
        root = tree.getroot()

        game_path = Path("")
        build_dst_folder = ""
        mod_target_name = ""
        root_dir = ""
        raw_hardcoded_files = ""
        raw_prefix_files = ""
        raw_prefix_search_dirs = ""
        raw_prefix_accepted_extensions = ""
        for child in root:
            # GAME PATH
            if child.tag == NexusPackager.TAG_GAME_PATH:
                path_game_str = str(child.text).strip()
                game_path = Path(path_game_str)

            # BUILD DST
            elif child.tag == NexusPackager.TAG_BUILD_DST:
                build_dst_folder = str(child.text).strip()

            # BSA TARGET NAME
            elif child.tag == NexusPackager.TAG_TARGET:
                mod_target_name = str(child.text).strip()
                echo_info("MOD TARGET NAME: " + mod_target_name)

            # GROUP ROOT
            elif child.tag == NexusPackager.TAG_ROOT:
                root_dir = str(child.text).strip()
                echo_info("root directory: " + root_dir)

            # BUILD RULES
            elif child.tag == NexusPackager.TAG_RULES:
                for rules_child in child:
                    if rules_child.tag == NexusPackager.TAG_HARDCODED_FILES:
                        raw_hardcoded_files = str(rules_child.text).strip()
                    elif rules_child.tag == NexusPackager.TAG_PREFIX_FILES:
                        raw_prefix_files = str(rules_child.text).strip()
                    elif rules_child.tag == NexusPackager.TAG_PREFIX_SEARCH_DIRS:
                        raw_prefix_search_dirs = str(rules_child.text).strip()
                    elif rules_child.tag == NexusPackager.TAG_PREFIX_ACCEPTED_EXTENSIONS:
                        raw_prefix_accepted_extensions = str(rules_child.text).strip()

        # validate data
        if not game_path.is_dir():
            echo_error(str.format("Game folder {} does not exist!", path_game_str))
            return False, None

        if build_dst_folder == "":
            echo_error("Build folder not defined!")
            return False, None

        if mod_target_name == "":
            echo_error("Target name not defined!")
            return False, None

        if root_dir == "":
            echo_error("Target name not defined!")
            return False, None
        elif root_dir != "Data":
            echo_warn("Group root different of Data.")

        # parse filters
        hardcoded_files = raw_hardcoded_files.split(NexusPackager.CSV_SEPARATOR)
        prefix_files = raw_prefix_files.split(NexusPackager.CSV_SEPARATOR)
        prefix_search_dirs = raw_prefix_search_dirs.split(NexusPackager.CSV_SEPARATOR)
        prefix_accepted_extensions = raw_prefix_accepted_extensions.split(NexusPackager.CSV_SEPARATOR)

        hardcoded_files = list(filter(None, [s.strip() for s in hardcoded_files]))
        prefix_files = list(filter(None, [s.strip() for s in prefix_files]))
        prefix_search_dirs = list(filter(None, [s.strip() for s in prefix_search_dirs]))
        prefix_accepted_extensions = list(filter(None, [s.strip() for s in prefix_accepted_extensions]))

        list_all_valid_files = []
        path_prefix = str(os.path.join(game_path, root_dir))
        # APPEND ALL EXISTING HARDCODED FILES
        for file in hardcoded_files:
            path_file_ret = os.path.join(game_path, root_dir, file)
            path_hard = Path(path_file_ret)
            if not path_hard.is_file():
                echo_warn(str.format("Warning: hardcoded file {} does not exit.", path_hard))
            else:
                echo_info("ok " + str(path_hard))
                relative_path = str(path_hard).replace(path_prefix, "")
                relative_path = relative_path.lstrip("\\")
                list_all_valid_files.append(relative_path)
        # SEARCH FOR ALL MATCHING FILES
        for subdir in prefix_search_dirs:
            search_dir = os.path.join(game_path, root_dir, subdir)
            _, all_files = scandir(search_dir, prefix_accepted_extensions)
            for file_path in all_files:
                file = str(os.path.basename(file_path))
                for prefix in prefix_files:
                    # match rule! starts with the prefix and has the extension
                    if file.startswith(prefix):
                        # full file name
                        current_file_full = str(file_path)
                        # remove base directory
                        relative_path = current_file_full.replace(path_prefix, "")
                        relative_path = relative_path.lstrip("\\")
                        list_all_valid_files.append(relative_path)

        print(list_all_valid_files)
        for file in list_all_valid_files:
            print(file)

        # create build object
        builder = NexusPackager(game_path=game_path,
                                build_dst=build_dst_folder,
                                group_root=root_dir,
                                target=mod_target_name,
                                all_files=list_all_valid_files)
        return True, builder

    def __init__(self, game_path, build_dst: str, group_root="Data", target="", all_files=[]):
        """
        Nexus packager object.
        :param game_path: The path of the game, where the files are going to be looked for.
        :param build_dst:
        :param group_root:
        :param target:
        :param all_files:
        """
        self.game_path = game_path
        self.build_dst = build_dst
        self.group_root = group_root
        self.target = target
        self.all_files = all_files

    def _create_bsa_build_scripts(self):
        """
        Experimental. Create bsa build scripts.
        :return:
        """
        base_script = "Build" + self.target + ".txt"
        files_list = "Build" + self.target + "Files" + ".txt"
        log_file = "Logs\\Archives\\Build" + self.target + ".log"
        bsa_target = self.group_root + "\\" + self.target + ".bsa"
        # create files list
        files_content = ""
        for file in self.all_files:
            files_content += file + NexusPackager.SKIP_LINE
        print("------------------------------")
        print(files_content)
        # create script
        script_content = ""
        script_content += "Log: " + log_file + NexusPackager.SKIP_LINE
        script_content += "New Archive" + NexusPackager.SKIP_LINE
        script_content += "Set File Group Root: " + self.group_root + "\\" + NexusPackager.SKIP_LINE
        script_content += "Add File Group: " + files_list + NexusPackager.SKIP_LINE
        script_content += "Save Archive: " + bsa_target + NexusPackager.SKIP_LINE
        print("------------------------------")
        print(script_content)
        with open(base_script, 'w') as file_base_script:
            file_base_script.write(script_content)
        with open(files_list, 'w') as file_files_content:
            file_files_content.write(files_content)

    def create_local_copy(self):
        """
        Creates a local copy of the mod
        :return:
        """
        # crete build dir
        build_dst_dir = os.path.join(".", self.build_dst, self.group_root)
        if not os.path.exists(build_dst_dir) and build_dst_dir != "":
            os.makedirs(build_dst_dir)
        # create Data folder
        proj_folder = os.path.join(self.game_path, self.group_root)
        for item in self.all_files:
            file_original_full_path = os.path.join(proj_folder, item)
            file_new_location = os.path.join(build_dst_dir, item)
            # copy all files
            copytree(file_original_full_path, file_new_location)

    def package(self):
        self.create_local_copy()
        self.create_unninstall_script(self.target, self.all_files, self.build_dst, self.group_root)
        self.zip_project(self.target, self.build_dst)


#  NxBuilder.py --config file.bsaproj
#  NxBuilder.py --build file.bsaproj
if __name__ == '__main__':
    proj_file = "./Test/TestProject.nxproj"
    ret, builder = NexusPackager.parse_build_file(proj_file)
    if ret == False:
        exit(-1)
    builder.package()

"""
    run_opt = "config"
    proj_file = "DawnOfTheSilverHand.bsaproj"

    ret, builder = NexusPackager.parse_build_file(proj_file)

    if ret == False:
        exit(-1)

    if run_opt == "config":
        builder._create_bsa_build_scripts()
        builder.create_local_copy()
    elif run_opt == "build":
        builder.create_local_copy()
    elif run_opt == "help":
        print("todo")
    elif run_opt == "version":
        print("todo")
"""

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
