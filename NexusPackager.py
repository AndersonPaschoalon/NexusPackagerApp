import os
import traceback
import os.path
from pathlib import Path
import xml.etree.ElementTree as ET
import shutil
from Utils import Utils


class NexusPackager:
    # tags
    TAG_GAME_PATH = "game_path"
    TAG_BUILD_DST = "build_dst"
    TAG_PACKAGE_NAME = "package_name"
    TAG_ROOT = "plugin_folder"
    TAG_RULES = "rules"
    TAG_HARDCODED_FILES = "hardcoded_files"
    TAG_PREFIX_FILES = "prefix_files"
    TAG_PREFIX_ACCEPTED_EXTENSIONS = "prefix_accepted_extensions"
    TAG_PREFIX_SEARCH_DIRS = "prefix_search_dirs"
    # default
    DEFAULT_BUILD_DST = "Release"
    # Special characters
    CSV_SEPARATOR = ","
    SKIP_LINE = "\n"
    EXT_NXPROJ = ".nxproj"
    EXT_ZIP = ".zip"
    # BSA Build
    # run_<datetime>.log
    BSABUILD_LOG_DIR = "Logs\\BsaBuild\\"
    BSABUILD_LOG_FILE = "run_{}.log"
    ARCHIVE_EXE = "Archive.exe"

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
            Utils.echo_error(str.format("Config file {} does not exist!", build_rules_file))
            return False, None

        tree = ET.parse(path_rules)
        root = tree.getroot()

        game_path = Path("")
        build_dst_folder = ""
        mod_target_name = ""
        plugin_dir = ""
        raw_hardcoded_files = ""
        raw_prefix_files = ""
        raw_prefix_search_dirs = ""
        raw_prefix_accepted_extensions = ""
        path_game_str = ""
        for child in root:
            # GAME PATH
            if child.tag == NexusPackager.TAG_GAME_PATH:
                path_game_str = str(child.text).strip()
                # TEST ##########################################################################################################################
                if path_game_str.startswith("."):
                    # dot directory (current)
                    dot_dir = os.getcwd()
                    path_game_str = path_game_str.replace(".", dot_dir)
                # TEST ##########################################################################################################################
                game_path = Path(path_game_str)



            # BUILD DST
            elif child.tag == NexusPackager.TAG_BUILD_DST:
                build_dst_folder = str(child.text).strip()

            # BSA TARGET NAME
            elif child.tag == NexusPackager.TAG_PACKAGE_NAME:
                mod_target_name = str(child.text).strip()
                Utils.echo_info("MOD TARGET NAME: " + mod_target_name)

            # GROUP ROOT
            elif child.tag == NexusPackager.TAG_ROOT:
                plugin_dir = str(child.text).strip()
                Utils.echo_info("Plugin directory: " + plugin_dir)

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
            Utils.echo_error(str.format("Game folder {} does not exist!", path_game_str))
            return False, None

        if plugin_dir == "":
            Utils.echo_info("Plugin folder is not defined!")

        if build_dst_folder == "":
            Utils.echo_warn(str.format("Build folder not defined! {} will be set as default.",
                                       NexusPackager.DEFAULT_BUILD_DST))
            build_dst_folder = NexusPackager.DEFAULT_BUILD_DST

        if mod_target_name == "":
            Utils.echo_error("Target name not defined!")
            return False, None

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
        path_prefix = str(os.path.join(game_path, plugin_dir))
        # APPEND ALL EXISTING HARDCODED FILES
        for file in hardcoded_files:
            path_file_ret = os.path.join(game_path, plugin_dir, file)
            path_hard = Path(path_file_ret)
            if not path_hard.is_file():
                Utils.echo_warn(str.format("Warning: hardcoded file {} does not exit.", path_hard))
            else:
                Utils.echo_info("ok " + str(path_hard))
                relative_path = str(path_hard).replace(path_prefix, "")
                relative_path = relative_path.lstrip("\\")
                list_all_valid_files.append(relative_path)
        # SEARCH FOR ALL MATCHING FILES
        for subdir in prefix_search_dirs:
            search_dir = os.path.join(game_path, plugin_dir, subdir)
            _, all_files = Utils.scandir(search_dir, prefix_accepted_extensions)
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
        pkg_builder = NexusPackager(game_path=game_path,
                                    build_dst=build_dst_folder,
                                    plugin_folder=plugin_dir,
                                    package_name=mod_target_name,
                                    all_files=list_all_valid_files)
        return True, pkg_builder

    @staticmethod
    def create_unninstall_script(project_name: str, list_all_files: [], build_dst, plugin_folder=""):
        script_name = "unninstall." + project_name + ".bat"
        # start of script
        script_content = "@echo off" + NexusPackager.SKIP_LINE
        script_content += "setlocal" + NexusPackager.SKIP_LINE
        script_content += ":PROMPT" + NexusPackager.SKIP_LINE
        script_content += "SET /P AREYOUSURE=Are you sure you want to unninstall " + project_name + "(Y/[N])?" + \
                          NexusPackager.SKIP_LINE
        script_content += 'IF /I "%AREYOUSURE%" NEQ "Y" GOTO END' + NexusPackager.SKIP_LINE
        script_content += NexusPackager.SKIP_LINE
        for file_name in list_all_files:
            if str(file_name).strip() != "":
                # delete command
                script_content += str.format('DEL "{}" {}', file_name, NexusPackager.SKIP_LINE)
        # end of the script
        script_content += ":END" + NexusPackager.SKIP_LINE
        script_content += "endlocal" + NexusPackager.SKIP_LINE
        script_content += NexusPackager.SKIP_LINE
        # dst directory where the unninstall script will be saved.
        path_script = os.path.join(".", build_dst, project_name, plugin_folder, script_name)
        # create script
        with open(path_script, 'w') as f:
            f.write(script_content)

    @staticmethod
    def zip_project(proj_name: str, build_dst: str):
        output_filename = proj_name
        build_dst_pkg = os.path.join(".", build_dst, output_filename + '.zip')
        dir_name = os.path.join(".", build_dst, proj_name)
        shutil.make_archive(output_filename, 'zip', dir_name)
        output_filename_zip = output_filename + '.zip'
        try:
            shutil.move(output_filename_zip, build_dst_pkg)
        except:
            Utils.echo_error(str.format("Error moving zip {} to folder {}.", output_filename_zip, build_dst_pkg))
            Utils.echo_error("** Check if the folder or any file is opened, and try again!")
            traceback.print_exc()

    @staticmethod
    def create_nxproj_template(proj_name: str):
        template_str = """
<build>
    <!--
    (Mandatory)
    directory where the game is installed. For skyrim it is usually:
    C:\\Program Files (x86)\Steam\steamapps\common\Skyrim
    -->
    <game_path>
    </game_path>
    <!--
    (Optional)
    Folder where the plugins are placed, usually Data.
    -->
    <plugin_folder>
    </plugin_folder>   
    <!--
    (Mandatory) 
    Name of the mod 
    -->
    <package_name>
    </package_name>     
    <!--
    (Default: Release)
    Folder where the Files will be placed. Suggestion: Release, Debug, version  name...
    -->
    <build_dst>
    </build_dst>
    <rules>
        <!--
        Files that must be packed, but do not follow any prefix rules.
        If you don't use prefix rules, just list all files hare, and leave the next tags empty.
        -->
        <hardcoded_files>
        </hardcoded_files>
        <!-- Prefix rules followed by your mod files. -->
        <prefix_files>
        </prefix_files>
        <!-- All extensions that are going to be packed. -->
        <prefix_accepted_extensions>
        </prefix_accepted_extensions>
        <!-- folders where the files that follow the prefix rule are going to be searched. -->
        <prefix_search_dirs>
        </prefix_search_dirs>
    </rules>
</build>        
"""
        nx_file = proj_name + NexusPackager.EXT_NXPROJ
        with open(nx_file, 'w') as f:
            f.write(template_str)


    def __init__(self, game_path, build_dst: str, plugin_folder="Data", package_name="", all_files=[]):
        """
        Nexus packager object.
        :param game_path: The path of the game, where the files are going to be looked for.
        :param plugin_folder:
        :param package_name:
        :param build_dst:
        :param all_files:
        """
        self.game_path = game_path
        self.plugin_folder = plugin_folder
        self.package_name = package_name
        self.build_dst = build_dst
        self.all_files = all_files

    def _create_bsa_build_scripts(self):
        """
        Experimental. Create bsa build scripts.
        :return:
        """
        base_script = "Build" + self.package_name + ".txt"
        files_list = "Build" + self.package_name + "Files" + ".txt"
        log_file = "Logs\\Archives\\Build" + self.package_name + ".log"
        bsa_target = self.plugin_folder + "\\" + self.package_name + ".bsa"
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
        script_content += "Set File Group Root: " + self.plugin_folder + "\\" + NexusPackager.SKIP_LINE
        script_content += "Add File Group: " + files_list + NexusPackager.SKIP_LINE
        script_content += "Save Archive: " + bsa_target + NexusPackager.SKIP_LINE
        print("------------------------------")
        print(script_content)
        with open(base_script, 'w') as file_base_script:
            file_base_script.write(script_content)
        with open(files_list, 'w') as file_files_content:
            file_files_content.write(files_content)

    def _create_local_copy(self):
        """
        Creates a local copy of the mod
        :return:
        """
        # crete build dir
        build_dst_dir = os.path.join(".", self.build_dst, self.package_name, self.plugin_folder)
        if not os.path.exists(build_dst_dir) and build_dst_dir != "":
            os.makedirs(build_dst_dir)
        # create Data folder
        proj_folder = os.path.join(self.game_path, self.plugin_folder)
        for item in self.all_files:
            file_original_full_path = os.path.join(proj_folder, item)
            file_new_location = os.path.join(build_dst_dir, item)
            # copy all files
            Utils.copytree(file_original_full_path, file_new_location)

    def package(self):
        self._create_local_copy()
        self.create_unninstall_script(self.package_name, self.all_files, self.build_dst, self.plugin_folder)
        self.zip_project(self.package_name, self.build_dst)


#  NxBuilder.py --config file.bsaproj
#  NxBuilder.py --build file.bsaproj
if __name__ == '__main__':
    proj_file = "./Test/TestProject.nxproj"
    ret, builder = NexusPackager.parse_build_file(proj_file)
    if ret:
        exit(-1)
    builder.package()
