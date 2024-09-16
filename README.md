# Shift_Resolve

## Description

Shift catalog of operators for Davinci Resolve.
This catalog includes multiple Shift operators to manage your Resolve project; the media pool elements like folders, videos and images; the timelines and the timeline items; the takes; and much more.

## Installation

To add this catalog to Shift, you can open the Catalog Manager `File > Catalog Manager` and add the catalog like and user Catalog. Just click on the `Add Catalog` button and select the shift_resolve.py file.

The catalog can be added through the environment too. For that add the path to the directory where the shift_resolve.py file is stored to the environment variable `SHIFT_CATALOG_PATH` from your environment before start Shift.

Take in consideration that the catalog can be added and used to create workflows in any instance of Shift. However, to be able to execute the operators from the catalog, Shift have to be open inside Davinci Resolve and with the Resolve Python API available. To set up the Python Interpreter and the Python API requirements from Danvici Resolve is recommended to check the official documentation from your Davinci Resolve version. You can also find a detailed explanation of how to setup Shift in Davinci Resolve in the [Resolve Shift Documentation](https://inbibo.co.uk/docs/shift/integration_resources/software/resolve).

## Dependencies

| **Dependency**                                                              | **Version** |
|-----------------------------------------------------------------------------|-------------|
| [Shift](https://inbibo.co.uk/shift)                      | \>= 1.0.0   |
| [Davinci Resolve](https://www.blackmagicdesign.com/products/davinciresolve) | 18.6        |

## Documentation

- [Shift Documentation](https://inbibo.co.uk/docs/shift)
- [Shift for Davinci Resolve](https://inbibo.co.uk/docs/shift/integration_resources/software/resolve)
- Davinci Resolve Documentation: Usually is located in your installation, for Windows Users, typically located here: `C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Readme.txt`

## Operators

- **DVR_ClipPropertyGet**: Operator to get properties from a clip.
- **DVR_ClipGet**: Operator to get a specific Clip from a list of Clips.
- **DVR_ClipsGet**: Operator to get all the clips from a Resolve folder.
- **DVR_FolderAdd**: Operator to create a folder inside other folder with the given name in Resolve.
- **DVR_FolderGet**: Operator to get a Folder from the media pool of the project.
- **DVR_FolderList**: Operator to get the list of folders within the given folder.
- **DVR_FolderNameGet**: Operator to get the name of a given folder.
- **DVR_FolderSet**: Operator to set the current active folder in the media pool of the project.
- **DVR_MetadataGet**: Operator to get the metadata of a given clip of the Media Pool.
- **DVR_MetadataSet**: Operator to edit the metadata of a given clip. 
- **DVR_ProjectExport**: Operator to export a given Resolve project in a Davinci Resolve Project file (.drp).
- **DVR_ProjectGet**: Operator to get the current Resolve project object.
- **DVR_ProjectImport**: Operator to import a Davinci Resolve project from a file.
- **DVR_ProjectOpen**: Operator to open a project with the provided name.
- **DVR_TakeAdd**: Operator to add a given clip like a take to a timeline item.
- **DVR_TakeGet**: Operator to get the clip and the index of a specific take in the given timeline item.
- **DVR_TakeSet**: Operator to set the take at the given index as the current take of the item.
- **DVR_TimelineExport**: Operator to export a Davinci Resolve timeline object.
- **DVR_TimelineGet**: Operator to get a Davinci Resolve timeline object.
- **DVR_TimelineSet**: Operator to set a given timeline like current timeline in the project.
- **DVR_TimelineImport**: Operator to import a timeline file in the Project.
- **DVR_TimelineItemGet**: Operator to get a timeline item object from a given list of items.
- **DVR_TimelineItemsGet**: Operator to get a list of timeline items from a given timeline.
- **DVR_TimelineNameGet**: Operator to get the name of a timeline.
- **DVR_TimelineNameSet**: Operator to set the name of a timeline.