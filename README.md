# Nexus Build App

![Nexus Packager App](./Doc/logo2.png)

Nexus Packager App is a command-line tool for automating the packaging process of Nexus mods.

I create this app because I wanted a flexible and simple tool to package both my Skyrim and Age of Mythology mods.

This application:

* Package files defined by rules into a ZIP, and preserve its original directory structure;
* Scriptable rules, write once, so you will never forget any files;
* Creates an uninstall script. 

## Manual

```
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
    *   game_path: The Path where the game is installed. If this file is placed
        at the root folder of the game, this parameter may be filled with "."
        instead of the absoluth pack of the game.
    *   plugin_folder: If this tag is defined, the files are going to be
        searched in this folder folder only. Otherwise they are going to be
        searched all over the game_path folder. On Skyrim for example, all the
        mod files are located in the Data folder.
    *   package_name: Name of the Zip package that is going to be created.
    *   build_dst: Directory where the zip will be saved. This directory will
        be created where the application is executed.
    *   rules: This tag contains a set of rules that are going to be followed
        to search the files.
    *   rules/hardcoded_files: Any file listed here will be included. The files
        must be comma separated. The absolute path of the file will be
        <game_path>/<plugin_folder>/<hardcoded_file>. This tag should be used
        for files that do not follow prefix rules.
    *   rules/prefix_files: For files that used prefix rules, this tag can be
        used instead. Files whose name starts with the prefix will be included.
    *   rules/prefix_accepted_extensions: Only files with the extensions
        included here (comma separated) will be included in the package.
    *   rules/prefix_search_dirs: directory where the files will be searched.

    Use-case:

    Supose you are executing NexusBuildApp.exe from you desktop, and you
    created a nxproj file called MyMod in your Skyrim installation folder.
    Supose your mod does have the following files:
    *   An main file placed at the Data folder called MyMod.esp
    *   Some .pex scripts files, all starting with MyMod_ prefix:
    *   You want your mod package to be created in a Release folder in your
        desktop.
    *   You want the zip file to be called MyModPackage
    
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
        C:\Program Files (x86)\Steam\steamapps\common\Skyrim

    To package your mod, type in the command line the following command:
        NexusPackagerApp.exe -p "C:\Program Files (x86)\Steam\steamapps\common\Skyrim"

    NexusPackagerApp will search for any nxproj file, and execute this rules.
    At the end, you will have a folder "Release" created in your desktop, and
    a MyModPackage.zip inside it.

OPTIONS
    -p <game-install-folder>, --path=<game-install-folder>
        Build all projects defined by .nxproj files inside a directory
        <game-install-folder>.
    -f <nxproj-project-file>, --file=<nxproj-project-file>
        Build an specified project defined by a .nxproj file.
    -t <nxproj-file-name>, --template=<nxproj-file-name>
        Generate an .nxproj file template file with the name <nxproj-file-name>.
    -c <nxproj-file-name>, --check=<nxproj-file-name>
        Check if the syntax of a <nxproj-file-name> is valid or not, but do not
        build the package.
    -h, --help
        Prints this help manual.
    -l, --license:
        Prints application license.
    -v, --version:
        Prints application version

```