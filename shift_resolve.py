import os
from shift.core.workflow import SOperator
from shift.core.workflow import SPlug
from shift.core.constants import SType
from shift.core.constants import SDirection
from shift.core.logger import shiftLogger as logger

try:
    import DaVinciResolveScript as dvr_script

    resolve = dvr_script.scriptapp("Resolve")
    projectManager = resolve.GetProjectManager()
except:
    # If DRV is not available, define the API objects like empty variables
    dvr_script = None
    resolve = None
    projectManager = None
    logger.warning("The DaVinciResolveScript API could not be imported during the loading of 'shift_resolve' catalog. "
                   "You won't be able to execute the operators from this catalog.")


def getHost():
    """Method to check the current host. If Davinci Resolve is available the result will be resolve.

    @return str: The name of the Host.

    """
    host = None
    try:
        import DaVinciResolveScript as dvr_script
        host = "resolve"
    except:
        pass

    return host


class DVR_Base(SOperator):
    """Base Davinci Resolve Operator class with utility methods."""
    # Define operator constants
    if resolve is not None:
        timelineTypes = {
            "FCP7 XML": {"suffix": ".xml", "type": resolve.EXPORT_FCP_7_XML},
            "EDL - CMX 3600": {"suffix": ".edl", "type": [resolve.EXPORT_EDL, resolve.EXPORT_NONE]},
            "FCPXML 1.3": {"suffix": ".fcpxml", "type": resolve.EXPORT_FCPXML_1_3},
            "FCPXML 1.4": {"suffix": ".fcpxml", "type": resolve.EXPORT_FCPXML_1_4},
            "FCPXML 1.5": {"suffix": ".fcpxml", "type": resolve.EXPORT_FCPXML_1_5},
            "FCPXML 1.6": {"suffix": ".fcpxml", "type": resolve.EXPORT_FCPXML_1_6},
            "FCPXML 1.7": {"suffix": ".fcpxml", "type": resolve.EXPORT_FCPXML_1_7},
            "FCPXML 1.8": {"suffix": ".fcpxml", "type": resolve.EXPORT_FCPXML_1_8},
            "AAF": {"suffix": ".aaf", "type": [resolve.EXPORT_AAF, resolve.EXPORT_AAF_NEW]},
            "DaVinci Resolve Timeline": {"suffix": ".drt", "type": resolve.EXPORT_DRT},
            "EDL - CDL": {"suffix": ".edl", "type": [resolve.EXPORT_EDL, resolve.EXPORT_CDL]},
            "EDL - SDL": {"suffix": ".edl", "type": [resolve.EXPORT_EDL, resolve.EXPORT_SDL]},
            "EDL - Missing Clips": {"suffix": ".edl", "type": [resolve.EXPORT_EDL, resolve.EXPORT_MISSING_CLIPS]},
            "HDR10 Profile A": {"suffix": ".xml", "type": resolve.EXPORT_HDR_10_PROFILE_A},
            "HDR10 Profile B": {"suffix": ".xml", "type": resolve.EXPORT_HDR_10_PROFILE_B},
            "Dolby Vision 2.9": {"suffix": ".xml", "type": resolve.EXPORT_DOLBY_VISION_VER_2_9},
            "Dolby Vision 4.0": {"suffix": ".xml", "type": resolve.EXPORT_DOLBY_VISION_VER_4_0},
            "CSV": {"suffix": ".csv", "type": resolve.EXPORT_TEXT_CSV},
            "Tabbed Text": {"suffix": ".txt", "type": resolve.EXPORT_TEXT_TAB},
        }
    else:
        # If Resolve it's not available we don't want the OP creation fail, we create a dummy constant
        timelineTypes = {
            "FCP7 XML": {"suffix": ".xml", "type": None},
            "EDL - CMX 3600": {"suffix": ".edl", "type": None},
            "FCPXML 1.3": {"suffix": ".fcpxml", "type": None},
            "FCPXML 1.4": {"suffix": ".fcpxml", "type": None},
            "FCPXML 1.5": {"suffix": ".fcpxml", "type": None},
            "FCPXML 1.6": {"suffix": ".fcpxml", "type": None},
            "FCPXML 1.7": {"suffix": ".fcpxml", "type": None},
            "FCPXML 1.8": {"suffix": ".fcpxml", "type": None},
            "AAF": {"suffix": ".aaf", "type": None},
            "DaVinci Resolve Timeline": {"suffix": ".drt", "type": None},
            "EDL - CDL": {"suffix": ".edl", "type": None},
            "EDL - SDL": {"suffix": ".edl", "type": None},
            "EDL - Missing Clips": {"suffix": ".edl", "type": None},
            "HDR10 Profile A": {"suffix": ".xml", "type": None},
            "HDR10 Profile B": {"suffix": ".xml", "type": None},
            "Dolby Vision 2.9": {"suffix": ".xml", "type": None},
            "Dolby Vision 4.0": {"suffix": ".xml", "type": None},
            "CSV": {"suffix": ".csv", "type": None},
            "Tabbed Text": {"suffix": ".txt", "type": None},
        }

    def checkDvr(self):
        """Method that checks if drv module is available and ready to use. If not raises an error."""
        if getHost() != "resolve":
            raise EnvironmentError("This operator can be executed only inside Davinci Resolve with "
                                   "Python installed and the API configured.")

    def getDrvIdx(self, value, objTypeName, lenght):
        """Converts the given value to a integer index and checks that is a valid index for the obj.
        If the index is not valid, the functions raise and error or log a warning.

        @param value str: The string that should contain an integer to be converted.
        @param objTypeName str: The type name of the object where the index will be used.
        @param lenght int: The maximum index value that can be accepted in the object.

        @return int: The index verified and ready to use.

        @raises ValueError: Raise an error if the value is not a valid index.

        """
        try:
            idx = int(value)
        except Exception as e:
            raise ValueError("The key value cannot be converted into a valid index as it is not an integer.")
        if idx > lenght or idx < 0:
            raise ValueError("{0} index out of range. "
                             "There are {0} items available.".format(objTypeName, idx))
        elif idx == 0:
            logger.warning("The resolve lists for {0} starts at index 1.".format(objTypeName))
        return idx

    def getObjClass(self, objIn):
        """Gets the class name of the given object.

        @param objIn obj: An object that should be a Resolve BlackmagicFusion.PyRemoteObject.

        return str: The name of the class.

        """
        objInClass = None
        if objIn is None:
            return objInClass
        try:
            objInClass = objIn.ClassName
        except:
            objInClass = None
        if objInClass is None:
            try:
                objInClass = type(objIn).__name__
            except:
                objInClass = None
        return objInClass

    def checkIndividualClass(self, objIn, objExpected):
        """Check the given object class individually, not list expected.

        @param objIn obj: An object that should be a Resolve BlackmagicFusion.PyRemoteObject instance.
        @param objExpected str: The name of the class object expected.

        @return bool: True if the class is not the same.
        @return str: The name of the class of the objIn.

        """
        raiseError = False
        objClass = self.getObjClass(objIn)
        if objExpected == "clip" and objClass != "Media pool item":
            raiseError = True
        elif objExpected == "item" and objClass != "Timeline item":
            raiseError = True
        elif objExpected == "timeline" and objClass != "Timeline":
            raiseError = True
        elif objExpected == "project" and objClass != "Project":
            raiseError = True
        return raiseError, objClass

    def checkClass(self, objIn, objExpected, isList=False):
        """Checks the given object class and raise and error if is not correct.

        @param objIn obj: An object that should be a Resolve BlackmagicFusion.PyRemoteObject instance.
        @param objExpected str: The name of the class object expected.
        @param isList bool: True if the objIn is a list of objects. False if it's only 1 object. (Default=False)

        """
        if not isList:
            raiseError, objClass = self.checkIndividualClass(objIn, objExpected)
            if raiseError:
                raise ValueError("The {0} input is not valid, got {1}".format(objExpected, objClass))
        else:
            for element in objIn:
                raiseError, objClass = self.checkIndividualClass(element, objExpected)
                if raiseError:
                    raise ValueError("One element from the list is not "
                                     "a {0}, is a {1}".format(objExpected, objClass))


class DVR_ClipPropertyGet(DVR_Base):
    """Operator to get properties from a clip.
    Allows the creation of new plugs. It will pick output plug names like property names
    to be read from the given clip and will store the obtained value inside them.
    Custom input plugs will be ignored.
    Works in Davinci Resolve.

    """

    def __init__(self, code, parent):
        super(self.__class__, self).__init__(code, editable=True, parent=parent)
        i_clip = SPlug(
            code="clip",
            value=None,
            type=SType.kInstance,
            direction=SDirection.kIn,
            parent=self)

        self.addPlug(i_clip)

    def execute(self, force=False):
        """Gets the desired properties from the given clip.

        @param force Bool: Sets the flag for forcing the execution even on clean nodes. (Default = False)

        """
        self.checkDvr()
        plugsList = [plug for plug in self.getPlugs(SDirection.kOut) if plug.type != SType.kTrigger]
        clip = self.getPlug("clip").value
        self.checkClass(clip, "clip")
        if plugsList:
            for p in plugsList:
                try:
                    fieldValue = clip.GetClipProperty(p.code)
                    if fieldValue:
                        p.setValue(fieldValue)
                except Exception as e:
                    raise ValueError("The property '{0}' could not be read: \n {1}".format(p.code, str(e)))
        super(self.__class__, self).execute()


class DVR_ClipGet(DVR_Base):
    """Operator to get a specific Clip from a list of Clips
    Works in Davinci Resolve.

    """

    def __init__(self, code, parent):
        super(self.__class__, self).__init__(code, editable=True, parent=parent)
        i_clips = SPlug(
            code="clips",
            value=None,
            type=SType.kInstance,
            direction=SDirection.kIn,
            parent=self)
        i_getMethod = SPlug(
            code="getMethod",
            value="ByName",
            type=SType.kEnum,
            options=["ByName"],
            direction=SDirection.kIn,
            parent=self)
        i_key = SPlug(
            code="key",
            value="",
            type=SType.kString,
            direction=SDirection.kIn,
            parent=self)
        o_clip = SPlug(
            code="clip",
            value=None,
            type=SType.kInstance,
            direction=SDirection.kOut,
            parent=self)

        self.addPlug(i_clips)
        self.addPlug(i_getMethod)
        self.addPlug(i_key)
        self.addPlug(o_clip)

    def execute(self, force=False):
        """Gets the desired clip from a list of clips.

        @param force Bool: Sets the flag for forcing the execution even on clean nodes. (Default = False)

        """
        self.checkDvr()
        clips = self.getPlug("clips", SDirection.kIn).value
        getMethod = self.getPlug("getMethod", SDirection.kIn).value
        clipKey = self.getPlug("key", SDirection.kIn).value
        targetClip = None
        if clips is None:
            raise ValueError("A clip list is required to get an specific clip.")
        if getMethod == "ByName":
            for clip in clips:
                if clip.GetClipProperty("Clip Name") == clipKey:
                    targetClip = clip
                    break
        else:
            raise ValueError("Get Method '{0}' is not supported. Please choose between: "
                             "'ByName'.".format(getMethod))

        self.getPlug("clip", SDirection.kOut).setValue(targetClip)
        super(self.__class__, self).execute()


class DVR_ClipsGet(DVR_Base):
    """Operator to get all the clips from a Resolve folder.

    Works in Davinci Resolve.

    """

    def __init__(self, code, parent):
        super(self.__class__, self).__init__(code, editable=True, parent=parent)
        i_folder = SPlug(
            code="folder",
            value=None,
            type=SType.kInstance,
            direction=SDirection.kIn,
            parent=self)
        o_clips = SPlug(
            code="clips",
            value=None,
            type=SType.kInstance,
            direction=SDirection.kOut,
            parent=self)

        self.addPlug(i_folder)
        self.addPlug(o_clips)

    def execute(self, force=False):
        """Gets the list of clips from the given folder.

        @param force Bool: Sets the flag for forcing the execution even on clean nodes. (Default = False)

        """
        self.checkDvr()
        folder = self.getPlug("folder", SDirection.kIn).value
        if folder is None:
            raise ValueError("A folder object is needed to retrieve the clips.")

        try:
            clips = folder.GetClipList()
        except Exception as e:
            raise RuntimeError("The clips couldn't be get from the folder: \n {0}".format(str(e)))

        self.getPlug("clips", SDirection.kOut).setValue(clips)
        super(self.__class__, self).execute()


class DVR_FolderAdd(DVR_Base):
    """Operator to create a folder inside other folder with the given name in Resolve.

    Works in Davinci Resolve.

    """

    def __init__(self, code, parent):
        super(self.__class__, self).__init__(code, editable=True, parent=parent)
        i_project = SPlug(
            code="project",
            value=None,
            type=SType.kInstance,
            direction=SDirection.kIn,
            parent=self)
        i_folder = SPlug(
            code="folder",
            value=None,
            type=SType.kInstance,
            direction=SDirection.kIn,
            parent=self)
        i_name = SPlug(
            code="name",
            value="",
            type=SType.kString,
            direction=SDirection.kIn,
            parent=self)
        o_folder = SPlug(
            code="folder",
            value=None,
            type=SType.kInstance,
            direction=SDirection.kOut,
            parent=self)

        self.addPlug(i_project)
        self.addPlug(i_folder)
        self.addPlug(i_name)
        self.addPlug(o_folder)

    def execute(self, force=False):
        """Add a new subFolder in the given folder with the given name.

        @param force Bool: Sets the flag for forcing the execution even on clean nodes. (Default = False)

        """
        self.checkDvr()
        currentFolder = self.getPlug("folder", SDirection.kIn).value
        folderName = self.getPlug("name", SDirection.kIn).value
        project = self.getPlug("project", SDirection.kIn).value
        if currentFolder is None:
            raise ValueError("A folder object is needed to create the subFolder inside.")
        if project is None:
            raise ValueError("A project object is needed to create the folder.")
        try:
            folder = project.GetMediaPool().AddSubFolder(currentFolder, folderName)
        except Exception as e:
            raise RuntimeError("The folder couldn't be created: \n {0}".format(str(e)))

        self.getPlug("folder", SDirection.kOut).setValue(folder)
        super(self.__class__, self).execute()


class DVR_FolderGet(DVR_Base):
    """Operator to get a Folder from the media pool of the project.
    Select the getMethod to return the current active folder, the root folder or a specific folder
    by a full path to the folder.
    Works in Davinci Resolve.

    """

    def __init__(self, code, parent):
        super(self.__class__, self).__init__(code, editable=True, parent=parent)
        i_project = SPlug(
            code="project",
            value=None,
            type=SType.kInstance,
            direction=SDirection.kIn,
            parent=self)
        i_getMethod = SPlug(
            code="getMethod",
            value="Current",
            type=SType.kEnum,
            options=["Current", "Root", "FullPath"],
            direction=SDirection.kIn,
            parent=self)
        i_folderPath = SPlug(
            code="folderPath",
            value="",
            type=SType.kString,
            direction=SDirection.kIn,
            parent=self)
        i_createFolders = SPlug(
            code="createFolders",
            value=False,
            type=SType.kBool,
            direction=SDirection.kIn,
            parent=self)
        o_folder = SPlug(
            code="folder",
            value=None,
            type=SType.kInstance,
            direction=SDirection.kOut,
            parent=self)

        self.addPlug(i_project)
        self.addPlug(i_getMethod)
        self.addPlug(i_folderPath)
        self.addPlug(i_createFolders)
        self.addPlug(o_folder)

    def _recursiveFolderResearch(self, currentFolder, currentPath, targetPath, mediapool, createFolders=False):
        """Recursive function to find a folder object based in the full path of the folder.
        The Resolve API doesn't allow to get a folder by name or full path, only allows to get the
        root, current and subfolders. Because of this, this function is a utility to research over a given folder and subfolders
        to be able to return a folder given a full path from the root folder.

        @param currentFolder Resolve.Folder: The current folder to check the subFolders from.
        @param currentPath str: The current status of the path that is being research.
        @param targetPath str: The target result of the path. The full folder path to get.
        @param mediapool Resolve.MediaPool: The media pool object from the Resolve API.
        @param createFolders bool: If it's true, any not found folder, will be created. (Default=False)

        @returns Resolve.Folder: The Folder that match the targetPath.

        """
        subFolders = currentFolder.GetSubFolderList()
        for subFolder in subFolders:
            subFolderName = subFolder.GetName()
            pathCheck = currentPath + "{0}/".format(subFolderName)
            if pathCheck == targetPath:
                return subFolder  # Here we end the recursion
            elif targetPath.startswith(pathCheck):
                # The folder is correct, but we still need another recursion level at least
                return self._recursiveFolderResearch(subFolder, pathCheck, targetPath, mediapool, createFolders=createFolders)
        if createFolders:
            newFolderName = targetPath.replace(currentPath, "").partition("/")[0]
            subFolder = mediapool.AddSubFolder(currentFolder, newFolderName)
            subFolderName = subFolder.GetName()
            pathCheck = currentPath + "{0}/".format(subFolderName)
            if pathCheck == targetPath:
                return subFolder  # Here we end the recursion
            elif targetPath.startswith(pathCheck):
                # The folder is correct, but we still need another recursion level at least
                return self._recursiveFolderResearch(subFolder, pathCheck, targetPath, mediapool,
                                                     createFolders=createFolders)
        return  # If we go to this return means that the folder haven't been found.

    def execute(self, force=False):
        """Gets the requested folder object from the media pool.

        @param force Bool: Sets the flag for forcing the execution even on clean nodes. (Default = False)

        """
        self.checkDvr()
        project = self.getPlug("project").value
        getMethod = self.getPlug("getMethod").value
        folderPath = self.getPlug("folderPath").value
        createFolders = self.getPlug("createFolders").value
        if project is None:
            raise ValueError("A project object is needed to get the folder from.")
        mediapool = project.GetMediaPool()
        if getMethod == "Current":
            folder = mediapool.GetCurrentFolder()
        elif getMethod == "Root":
            folder = mediapool.GetRootFolder()
        elif getMethod == "FullPath":
            if not folderPath:
                raise ValueError("A folder path is required to use the FullPath get method.")
            folderPath = folderPath.replace("\\", "/")
            inputFolderPath = folderPath if folderPath.endswith("/") else folderPath + "/"
            try:
                folder = self._recursiveFolderResearch(
                    mediapool.GetRootFolder(), "", inputFolderPath, mediapool, createFolders=createFolders)
            except Exception as e:
                raise RuntimeError("The folder couldn't be found using the FullPath get method. "
                                   "Check that the Folder path is correct: \n {0}".format(str(e)))
        else:
            raise ValueError("Get Method '{0}' is not supported. Please choose between: "
                             "'Current', 'Root', 'FullPath'.".format(getMethod))


        self.getPlug("folder", SDirection.kOut).setValue(folder)
        super(self.__class__, self).execute()


class DVR_FolderNameGet(DVR_Base):
    """Operator to get the name of a given folder.
    Works in Davinci Resolve.

    """

    def __init__(self, code, parent):
        super(self.__class__, self).__init__(code, parent=parent)
        i_folder = SPlug(
            code="folder",
            value=None,
            type=SType.kInstance,
            direction=SDirection.kIn,
            parent=self)
        o_name = SPlug(
            code="name",
            value="",
            type=SType.kString,
            direction=SDirection.kOut,
            parent=self)

        self.addPlug(i_folder)
        self.addPlug(o_name)

    def execute(self, force=False):
        """Gets the name of the given folder object.

        @param force Bool: Sets the flag for forcing the execution even on clean nodes. (Default = False)

        """
        self.checkDvr()
        folder = self.getPlug("folder").value
        self.checkClass(folder, "folder")
        folderName = folder.GetName()
        self.getPlug("name", SDirection.kOut).setValue(folderName)
        super(self.__class__, self).execute()


class DVR_FolderSet(DVR_Base):
    """Operator to set the current active folder in the media pool of the project.
    Works in Davinci Resolve.

    """

    def __init__(self, code, parent):
        super(self.__class__, self).__init__(code, editable=True, parent=parent)
        i_project = SPlug(
            code="project",
            value=None,
            type=SType.kInstance,
            direction=SDirection.kIn,
            parent=self)
        i_folder = SPlug(
            code="folder",
            value=None,
            type=SType.kInstance,
            direction=SDirection.kIn,
            parent=self)

        self.addPlug(i_project)
        self.addPlug(i_folder)

    def execute(self, force=False):
        """Sets the current active folder in the media pool of the project.

        @param force Bool: Sets the flag for forcing the execution even on clean nodes. (Default = False)

        """
        self.checkDvr()
        folder = self.getPlug("folder", SDirection.kIn).value
        project = self.getPlug("project", SDirection.kIn).value
        if folder is None:
            raise ValueError("A folder object is needed to create the subFolder inside.")
        if project is None:
            raise ValueError("A project object is needed to create the folder.")
        msg = ""
        try:
            result = project.GetMediaPool().SetCurrentFolder(folder)
        except Exception as e:
            msg = str(e)
            result = False
        if not result:
            raise RuntimeError("The folder couldn't be set as active: {0}".format(msg))

        super(self.__class__, self).execute()


class DVR_MetadataGet(DVR_Base):
    """Operator to get the metadata of a given clip of the Media Pool.
    Allows the creation of new plugs. It will pick output plug names like field of the metadata to be read from the given clip and will store the obtained value inside them. Custom input plugs will be ignored.

    Works in Davinci Resolve.

    """

    def __init__(self, code, parent):
        super(self.__class__, self).__init__(code, editable=True, parent=parent)
        i_clip = SPlug(
            code="clip",
            value=None,
            type=SType.kInstance,
            direction=SDirection.kIn,
            parent=self)

        self.addPlug(i_clip)

    def execute(self, force=False):
        """Gets the required metadata of the given clip using each custom output plugs like fields to read.

        @param force Bool: Sets the flag for forcing the execution even on clean nodes. (Default = False)

        """
        self.checkDvr()

        plugsList = [plug for plug in self.getPlugs(SDirection.kOut) if plug.type != SType.kTrigger]
        clip = self.getPlug("clip").value
        if clip is None:
            raise ValueError("A clip object is needed to read the metadata from.")
        if plugsList:
            for p in plugsList:
                try:
                    fieldValue = clip.GetMetadata(p.code)
                    if fieldValue:
                        p.setValue(fieldValue)
                except Exception as e:
                    logger.warning("The metadata of type '{0}' could not be read.".format(p.code))

        super(self.__class__, self).execute()


class DVR_MetadataSet(DVR_Base):
    """Operator to edit the metadata of a given clip. You can create custom plugs to set different
    metadata field in the given clip. The name of each custom plug will be used like the metadata field name,
    and the value of the plug like the value of the metadata to set fot that field.
    Works in Davinci Resolve.

    """

    def __init__(self, code, parent):
        super(self.__class__, self).__init__(code, editable=True, parent=parent)
        i_clip = SPlug(
            code="clip",
            value=None,
            type=SType.kInstance,
            direction=SDirection.kIn,
            parent=self)

        self.addPlug(i_clip)

    def execute(self, force=False):
        """Edit the metadata for the given clip using each custom input plugs like fields to edit.

        @param force Bool: Sets the flag for forcing the execution even on clean nodes. (Default = False)

        """
        self.checkDvr()

        plugsList = self.getPlugs(SDirection.kIn)
        clip = self.getPlug("clip").value
        msg = ""
        errorPlugs = []
        if len(plugsList) > 2:
            for p in plugsList:
                if not p.type is SType.kTrigger and p.code != "clip":
                    try:
                        resAux = clip.SetMetadata(p.code, p.value)
                    except Exception as e:
                        msg += "\n " + str(e)
                        resAux = False
                    if not resAux:
                        errorPlugs.append(p.code)

        if errorPlugs:
            raise RuntimeError("The metadata of the attributes '{0}' "
                               "could not be set:  \n  {1}".format(str(errorPlugs), msg))

        super(self.__class__, self).execute()


class DVR_ProjectExport(DVR_Base):
    """Operator to get export a given Resolve project in a Davinci Resolve Project file (.drp).
    Works in Davinci Resolve.

    """

    def __init__(self, code, parent):
        super(self.__class__, self).__init__(code, parent=parent)

        i_project = SPlug(
            code="project",
            value=None,
            type=SType.kInstance,
            direction=SDirection.kIn,
            parent=self)
        i_filepath = SPlug(
            code="filepath",
            value="",
            type=SType.kFileOut,
            direction=SDirection.kIn,
            parent=self)
        o_filepath = SPlug(
            code="filepath",
            value="",
            type=SType.kFileOut,
            direction=SDirection.kOut,
            parent=self)

        self.addPlug(i_project)
        self.addPlug(i_filepath)
        self.addPlug(o_filepath)

    def execute(self, force=False):
        """Exports a given Resolve project in the Resolve project files format.

        @param force Bool: Sets the flag for forcing the execution even on clean nodes. (Default = False)

        """
        self.checkDvr()
        project = self.getPlug("project", SDirection.kIn).value
        filepath = self.getPlug("filepath", SDirection.kIn).value
        if not project:
            raise ValueError("A Davinci Resolve project is required to export.")
        if not filepath or not filepath.endswith(".drp"):
            raise ValueError("A filepath for a .drp file is required to export the project.")
        msg = ""
        try:
            result = projectManager.ExportProject(project.GetName(), filepath)
        except Exception as e:
            msg = str(e)
            result = False
        if not result:
            raise RuntimeError("The project couldn't be exported:  \n  {0}".format(msg))
        self.getPlug("filepath", SDirection.kOut).setValue(filepath)
        super(self.__class__, self).execute()


class DVR_ProjectGet(DVR_Base):
    """Operator to get the current Resolve project object.
    Works in Davinci Resolve.

    """

    def __init__(self, code, parent):
        super(self.__class__, self).__init__(code, parent=parent)

        o_project = SPlug(
            code="project",
            value=None,
            type=SType.kInstance,
            direction=SDirection.kOut,
            parent=self)

        self.addPlug(o_project)

    def execute(self, force=False):
        """Returns the current project from Davinci Resolve.

        @param force Bool: Sets the flag for forcing the execution even on clean nodes. (Default = False)

        """
        self.checkDvr()
        project = projectManager.GetCurrentProject()
        self.getPlug("project", SDirection.kOut).setValue(project)
        super(self.__class__, self).execute()


class DVR_TakeAdd(DVR_Base):
    """Operator to add a given clip like a take to a timeline item.
    The clip input will be added to the take selector of the item input.
    If you don't specify any start and end frame, or the frame are the same,
    the frame range will be ignored and the take will be added with the full range.
    Works in Davinci Resolve.

    """

    def __init__(self, code, parent):
        super(self.__class__, self).__init__(code, parent=parent)

        i_item = SPlug(
            code="item",
            value=None,
            type=SType.kInstance,
            direction=SDirection.kIn,
            parent=self)
        i_clip = SPlug(
            code="clip",
            value=None,
            type=SType.kInstance,
            direction=SDirection.kIn,
            parent=self)
        i_startFrame = SPlug(
            code="startFrame",
            value=0,
            type=SType.kInt,
            direction=SDirection.kIn,
            parent=self)
        i_endFrame = SPlug(
            code="endFrame",
            value=0,
            type=SType.kInt,
            direction=SDirection.kIn,
            parent=self)

        self.addPlug(i_item)
        self.addPlug(i_clip)
        self.addPlug(i_startFrame)
        self.addPlug(i_endFrame)

    def execute(self, force=False):
        """Adds a given clip to a given item like a take.

        @param force Bool: Sets the flag for forcing the execution even on clean nodes. (Default = False)

        """
        self.checkDvr()
        item = self.getPlug("item", SDirection.kIn).value
        clip = self.getPlug("clip", SDirection.kIn).value
        startFrame = self.getPlug("startFrame", SDirection.kIn).value
        endFrame = self.getPlug("endFrame", SDirection.kIn).value
        # Check input values
        self.checkClass(item, "item")
        self.checkClass(clip, "clip")
        if startFrame > endFrame:
            raise ValueError("The given frame range is not valid: {0}-{1}".format(startFrame, endFrame))
        msg = "No error provided"
        try:
            if startFrame == endFrame:  # We use the equal condition like flag to ignore the frame range.
                result = item.AddTake(clip)
            else:
                result = item.AddTake(clip, startFrame, endFrame)
        except Exception as e:
            result = False
            msg = str(e)
        if not result:
            raise RuntimeError("The take could not be added: {0}".format(msg))
        super(self.__class__, self).execute()


class DVR_TakeGet(DVR_Base):
    """Returns the clip and the index of a specific take in the given timeline item.
    You can select the getMethod of your choice to input a clip name, an index or return the current selection.
    If you select the ByIndex method you have to specify an integer from 1 to the number of
    takes in the item in the key plug.
    If you select the ByName method you have to specify a clip name in the key plug.
    Works in Davinci Resolve.

    """

    def __init__(self, code, parent):
        super(self.__class__, self).__init__(code, parent=parent)

        i_item = SPlug(
            code="item",
            value=None,
            type=SType.kInstance,
            direction=SDirection.kIn,
            parent=self)
        i_getMethod = SPlug(
            code="getMethod",
            value="ByName",
            type=SType.kEnum,
            options=["ByName", "ByIndex", "Current"],
            direction=SDirection.kIn,
            parent=self)
        i_key = SPlug(
            code="key",
            value="",
            type=SType.kString,
            direction=SDirection.kIn,
            parent=self)
        o_clip = SPlug(
            code="clip",
            value=None,
            type=SType.kInstance,
            direction=SDirection.kOut,
            parent=self)
        o_index = SPlug(
            code="index",
            value=0,
            type=SType.kInt,
            direction=SDirection.kOut,
            parent=self)

        self.addPlug(i_item)
        self.addPlug(i_getMethod)
        self.addPlug(i_key)
        self.addPlug(o_clip)
        self.addPlug(o_index)

    def execute(self, force=False):
        """Returns a clip and index from a specific take of the given item.

        @param force Bool: Sets the flag for forcing the execution even on clean nodes. (Default = False)

        """
        self.checkDvr()
        item = self.getPlug("item", SDirection.kIn).value
        getMethod = self.getPlug("getMethod", SDirection.kIn).value
        takeKey = self.getPlug("key", SDirection.kIn).value
        # Check input values
        self.checkClass(item, "item")

        if getMethod == "ByName":
            take = None
            for idx in range(1, item.GetTakesCount() + 1):
                takeAux = item.GetTakeByIndex(idx)
                clipAux = takeAux.get("mediaPoolItem")
                if not clipAux:
                    logger.warning("The take with index {0} doesn't have a mediaPoolItem associated.".format(idx))
                    continue
                if clipAux.GetClipProperty("Clip Name") == takeKey:
                    take = [idx, clipAux]
                    break
            if take is None:
                take = [-1, None]
                logger.debug("Take with a clip name '{0}' not found.".format(takeKey))
        elif getMethod == "ByIndex":
            # Index sanity checks
            takeIdx = self.getDrvIdx(takeKey, "Take", item.GetTakesCount())
            # Get the take for the given index
            try:
                takeClip = item.GetTakeByIndex(takeIdx).get("mediaPoolItem")
            except Exception as e:
                raise RuntimeError("The take at index {0} could not be get.".format(takeIdx))
            take = [takeIdx, takeClip]
        elif getMethod == "Current":
            try:
                takeIdx = item.GetSelectedTakeIndex()
                takeClip = item.GetTakeByIndex(takeIdx).get("mediaPoolItem")
            except Exception as e:
                raise RuntimeError("The current take could not be get.")
            take = [takeIdx, takeClip]
        else:
            raise ValueError("Get Method '{0}' is not supported. Please choose between: "
                             "'ByName', 'ByIndex', 'Current'.".format(getMethod))
        self.getPlug("clip", SDirection.kOut).setValue(take[1])
        self.getPlug("index", SDirection.kOut).setValue(take[0])
        super(self.__class__, self).execute()


class DVR_TakeSet(DVR_Base):
    """Sets the take at the given index as the current take of the given item.
    Works in Davinci Resolve.

    """

    def __init__(self, code, parent):
        super(self.__class__, self).__init__(code, parent=parent)

        i_item = SPlug(
            code="item",
            value=None,
            type=SType.kInstance,
            direction=SDirection.kIn,
            parent=self)
        i_index = SPlug(
            code="index",
            value="",
            type=SType.kInt,
            direction=SDirection.kIn,
            parent=self)
        o_clip = SPlug(
            code="clip",
            value=None,
            type=SType.kInstance,
            direction=SDirection.kOut,
            parent=self)

        self.addPlug(i_item)
        self.addPlug(i_index)
        self.addPlug(o_clip)

    def execute(self, force=False):
        """Set a specific take in the given item.

        @param force Bool: Sets the flag for forcing the execution even on clean nodes. (Default = False)

        """
        self.checkDvr()
        item = self.getPlug("item", SDirection.kIn).value
        takeIndex = self.getPlug("index", SDirection.kIn).value
        # Check input values
        self.checkClass(item, "item")
        takeMax = item.GetTakesCount()
        if takeIndex < 1 or takeIndex > takeMax:
            raise ValueError("Index out of range. The item have only {0} takes.".format(takeMax))
        # Set the take for the given index
        msg = "No error provided."
        try:
            result = item.SelectTakeByIndex(takeIndex)
        except Exception as e:
            msg = str(e)
            result = False
        if not result:
            raise RuntimeError("The take with index {0} could not be set: {1}".format(takeIndex, msg))
        clip = item.GetTakeByIndex(takeIndex).get("mediaPoolItem")
        self.getPlug("clip", SDirection.kOut).setValue(clip)
        super(self.__class__, self).execute()


class DVR_ProjectImport(DVR_Base):
    """Operator to import a Davinci Resolve project from a file.
    Works in Davinci Resolve.

    """

    def __init__(self, code, parent):
        super(self.__class__, self).__init__(code, parent=parent)

        i_filepath = SPlug(
            code="filepath",
            value="",
            type=SType.kFileIn,
            direction=SDirection.kIn,
            parent=self)

        self.addPlug(i_filepath)

    def execute(self, force=False):
        """Imports a given project in Davinci Resolve.

        @param force Bool: Sets the flag for forcing the execution even on clean nodes. (Default = False)

        """
        self.checkDvr()
        filepath = self.getPlug("filepath", SDirection.kIn).value
        if not filepath or not filepath.endswith(".drp"):
            raise ValueError("The filepath to the project have to be a .drp format.")
        msg = ""
        try:
            result = projectManager.ImportProject(filepath)
        except Exception as e:
            msg = str(e)
            result = False
        if not result:
            raise RuntimeError("The project couldn't be imported: {0}".format(msg))
        super(self.__class__, self).execute()


class DVR_TimelineExport(DVR_Base):
    """Operator to export a Davinci Resolve Timeline object.
    Select the desired timeline format to export and provide a file path to save it with the correct extension for that
    format. Is the extension is not correct the operator will raise and error and suggest the correct extension.
    Works in Davinci Resolve.

    """

    def __init__(self, code, parent):
        super(self.__class__, self).__init__(code, parent=parent)
        i_timeline = SPlug(
            code="timeline",
            value=None,
            type=SType.kInstance,
            direction=SDirection.kIn,
            parent=self)
        i_filepath = SPlug(
            code="filepath",
            value="",
            type=SType.kFileOut,
            direction=SDirection.kIn,
            parent=self)
        i_format = SPlug(
            code="format",
            value="FCP7 XML",
            type=SType.kEnum,
            options=list(self.timelineTypes.keys()),  # Get the format types from the class constant
            direction=SDirection.kIn,
            parent=self)
        o_filepath = SPlug(
            code="filepath",
            value="",
            type=SType.kFileOut,
            direction=SDirection.kOut,
            parent=self)

        self.addPlug(i_timeline)
        self.addPlug(i_filepath)
        self.addPlug(i_format)
        self.addPlug(o_filepath)

    def execute(self, force=False):
        """Export the given timeline in the given format from Resolve.

        @param force Bool: Sets the flag for forcing the execution even on clean nodes. (Default = False)

        """
        self.checkDvr()
        timeline = self.getPlug("timeline", SDirection.kIn).value
        filepath = self.getPlug("filepath", SDirection.kIn).value
        timelineFormat = self.getPlug("format", SDirection.kIn).value
        # Check the input values
        if timeline is None:
            raise ValueError("A Timeline object is required to execute the export")
        timelineType = self.timelineTypes.get(timelineFormat)
        if timelineType is None:
            raise ValueError("The timeline format '{0}' it's not recognized.".format(timelineFormat))
        # Check filepath suffix
        if not filepath.endswith(timelineType.get("suffix")):
            raise ValueError("The filepath must end with the format suffix type '{0}', not '{1}'.".format(
                timelineType.get("suffix"),
                filepath.rpartition(".")[2]
            ))
        # Export the timeline
        msg = ""
        try:
            if type(timelineType.get("type")) is list:
                result = timeline.Export(filepath, timelineType.get("type")[0], timelineType.get("type")[1])
            else:
                result = timeline.Export(filepath, timelineType.get("type"))
        except Exception as e:
            msg = str(e)
            result = False

        if not result:
            raise RuntimeError("Timeline export process has fail:  \n {0}".format(msg))
        self.getPlug("filepath", SDirection.kOut).setValue(filepath)
        super(self.__class__, self).execute()


class DVR_TimelineGet(DVR_Base):
    """Operator to get a Davinci Resolve Timeline object.
    Select the getMethod to be able to retrieve a timeline by name, by index number or
    get the current open timeline. For the ByName and ByIndex methods you can specify the value
    in the key input plug.
    Works in Davinci Resolve.

    """

    def __init__(self, code, parent):
        super(self.__class__, self).__init__(code, parent=parent)
        i_project = SPlug(
            code="project",
            value=None,
            type=SType.kInstance,
            direction=SDirection.kIn,
            parent=self)
        i_getMethod = SPlug(
            code="getMethod",
            value="ByName",
            type=SType.kEnum,
            options=["ByName", "ByIndex", "Current"],
            direction=SDirection.kIn,
            parent=self)
        i_key = SPlug(
            code="key",
            value="",
            type=SType.kString,
            direction=SDirection.kIn,
            parent=self)
        o_timeline = SPlug(
            code="timeline",
            value=None,
            type=SType.kInstance,
            direction=SDirection.kOut,
            parent=self)

        self.addPlug(i_project)
        self.addPlug(i_getMethod)
        self.addPlug(i_key)
        self.addPlug(o_timeline)

    def execute(self, force=False):
        """Returns the specified timeline obj from Resolve.

        @param force Bool: Sets the flag for forcing the execution even on clean nodes. (Default = False)

        """
        self.checkDvr()
        project = self.getPlug("project", SDirection.kIn).value
        getMethod = self.getPlug("getMethod", SDirection.kIn).value
        timeKey = self.getPlug("key", SDirection.kIn).value

        if getMethod == "ByName":
            timeline = None
            for index in range(1, project.GetTimelineCount() + 1):
                timelineAux = project.GetTimelineByIndex(index)
                if timelineAux.GetName() == timeKey:
                    timeline = timelineAux
                    break
            if timeline is None:
                logger.warning("Timeline with name '{0}' not found.".format(timeKey))
        elif getMethod == "ByIndex":
            # Index sanity checks
            timeIdx = self.getDrvIdx(timeKey, "Timeline", project.GetTimelineCount())
            # Get the timeline for the given index
            try:
                timeline = project.GetTimelineByIndex(timeIdx)
            except Exception as e:
                raise RuntimeError("The timeline at index {0} could not be get.".format(timeIdx))
        elif getMethod == "Current":
            try:
                timeline = project.GetCurrentTimeline()
            except Exception as e:
                raise RuntimeError("The current timeline could not be get.")
        else:
            raise ValueError("Get Method '{0}' is not supported. Please choose between: "
                             "'ByName', 'ByIndex', 'Current'.".format(getMethod))
        self.getPlug("timeline", SDirection.kOut).setValue(timeline)
        super(self.__class__, self).execute()


class DVR_TimelineSet(DVR_Base):
    """Operator to set a given timeline like current timeline in the project.
    Works in Davinci Resolve.

    """

    def __init__(self, code, parent):
        super(self.__class__, self).__init__(code, parent=parent)
        i_project = SPlug(
            code="project",
            value=None,
            type=SType.kInstance,
            direction=SDirection.kIn,
            parent=self)
        i_timeline = SPlug(
            code="timeline",
            value=None,
            type=SType.kInstance,
            direction=SDirection.kIn,
            parent=self)

        self.addPlug(i_project)
        self.addPlug(i_timeline)

    def execute(self, force=False):
        """Set the given timeline like current timeline in the project.

        @param force Bool: Sets the flag for forcing the execution even on clean nodes. (Default = False)

        """
        self.checkDvr()
        project = self.getPlug("project", SDirection.kIn).value
        timeline = self.getPlug("timeline", SDirection.kIn).value

        if project is None:
            raise ValueError("A project entity is required to set the timeline. Got {0}".format(project))

        if timeline is None:
            raise ValueError("A timeline entity is required to set the timeline. Got {0}".format(timeline))

        msg = ""
        try:
            result = project.SetCurrentTimeline(timeline)
        except Exception as e:
            msg = str(e)
            result = False
        if not result:
            raise RuntimeError("The current timeline could not be set: \n {0}".format(msg))

        super(self.__class__, self).execute()


class DVR_TimelineImport(DVR_Base):
    """Operator to import a timeline file in the Project. The required parameters are the resolve project
    and the filepath to the timeline file. But you can set optional parameters:
    timelineName: Specifies the name of the timeline to be created.
    importSourceClips: Specifies whether source clips should be imported, True by default. Not valid for DRT import
    sourceClipsPath: Specifies a filesystem path to search for source clips if the media is inaccessible
    in their original path and if importSourceClips is True.
    sourceClipsFolders: List of Media Pool folder objects to search for source clips if the media is
    not present in current folder and if "importSourceClips" is False. Not valid for DRT import.
    Works in Davinci Resolve.

    """

    def __init__(self, code, parent):
        super(self.__class__, self).__init__(code, parent=parent)
        i_project = SPlug(
            code="project",
            value=None,
            type=SType.kInstance,
            direction=SDirection.kIn,
            parent=self)
        i_filepath = SPlug(
            code="filepath",
            value="",
            type=SType.kFileIn,
            direction=SDirection.kIn,
            parent=self)
        i_timelineName = SPlug(
            code="timelineName",
            value="",
            type=SType.kString,
            direction=SDirection.kIn,
            parent=self)
        i_importSourceClips = SPlug(
            code="importSourceClips",
            value=True,
            type=SType.kBool,
            direction=SDirection.kIn,
            parent=self)
        i_sourceClipsPath = SPlug(
            code="sourceClipsPath",
            value="",
            type=SType.kDir,
            direction=SDirection.kIn,
            parent=self)
        i_sourceClipsFolders = SPlug(
            code="sourceClipsFolders",
            value=None,
            type=SType.kInstance,
            direction=SDirection.kIn,
            parent=self)
        o_timeline = SPlug(
            code="timeline",
            value=None,
            type=SType.kInstance,
            direction=SDirection.kOut,
            parent=self)

        self.addPlug(i_project)
        self.addPlug(i_filepath)
        self.addPlug(i_timelineName)
        self.addPlug(i_importSourceClips)
        self.addPlug(i_sourceClipsPath)
        self.addPlug(i_sourceClipsFolders)
        self.addPlug(o_timeline)

    def execute(self, force=False):
        """Imports a given timeline file in the given DVR project.

        @param force Bool: Sets the flag for forcing the execution even on clean nodes. (Default = False)

        """
        self.checkDvr()
        project = self.getPlug("project", SDirection.kIn).value
        filepath = self.getPlug("filepath", SDirection.kIn).value
        timelineName = self.getPlug("timelineName", SDirection.kIn).value
        importSourceClips = self.getPlug("importSourceClips", SDirection.kIn).value
        sourceClipsPath = self.getPlug("sourceClipsPath", SDirection.kIn).value
        sourceClipsFolders = self.getPlug("sourceClipsFolders", SDirection.kIn).value
        if not os.path.isfile(filepath):
            raise ValueError("A valid filepath to a timeline file is required. Got {0}".format(filepath))
        isDrt = filepath.endswith(".drt")
        if project is None:
            raise ValueError("A valid project instance is required to import the timeline. Got {0}".format(project))
        # Build optional arguments when required
        importOptions = {}
        if not isDrt:  # DRT doesn't support this optional parameters
            importOptions["importSourceclips"] = importSourceClips
            if timelineName:
                importOptions["timelineName"] = timelineName
            if sourceClipsPath:
                importOptions["sourceClipsPath"] = sourceClipsPath
            if sourceClipsFolders:
                importOptions["sourceClipsFolders"] = sourceClipsFolders
        # Import the timeline
        try:
            timeline = project.GetMediaPool().ImportTimelineFromFile(filepath, importOptions)
        except Exception as e:
            raise RuntimeError("Timeline import process has failed: {0}".format(str(e)))

        if timelineName and isDrt:  # To allow renaming of DRT files, rename the file after import
            msg = ""
            try:
                result = timeline.SetName(timelineName)
            except Exception as e:
                msg = str(e)
                result = False
            if not result:
                logger.warning("The timeline could not be renamed after the import: \n{0}".format(msg))
        self.getPlug("timeline", SDirection.kOut).setValue(timeline)
        super(self.__class__, self).execute()


class DVR_TimelineItemGet(DVR_Base):
    """Operator to get a timeline item object from a given list of items.
    You can search for a specific clip with a specific name. With the nameSource input

    you can choose to check the name from the timeline item or the name from the media pool item (clip).
    The operator returns the timeline item object (item) and the media pool item (clip).
    Works in Davinci Resolve.

    """

    def __init__(self, code, parent):
        super(self.__class__, self).__init__(code, parent=parent)
        i_items = SPlug(
            code="items",
            value=None,
            type=SType.kInstance,
            direction=SDirection.kIn,
            parent=self)
        i_nameSource = SPlug(
            code="nameSource",
            value="TimelineItem",
            type=SType.kEnum,
            options=["TimelineItem", "MediaPoolClip"],
            direction=SDirection.kIn,
            parent=self)
        i_name = SPlug(
            code="name",
            value="",
            type=SType.kString,
            direction=SDirection.kIn,
            parent=self)
        o_item = SPlug(
            code="item",
            value=None,
            type=SType.kInstance,
            direction=SDirection.kOut,
            parent=self)
        o_mediaPoolItem = SPlug(
            code="clip",
            value=None,
            type=SType.kInstance,
            direction=SDirection.kOut,
            parent=self)

        self.addPlug(i_items)
        self.addPlug(i_nameSource)
        self.addPlug(i_name)
        self.addPlug(o_item)
        self.addPlug(o_mediaPoolItem)


    def execute(self, force=False):
        """Returns a list of timeline items from the given timeline.

        @param force Bool: Sets the flag for forcing the execution even on clean nodes. (Default = False)

        """
        self.checkDvr()
        items = self.getPlug("items", SDirection.kIn).value
        nameSource = self.getPlug("nameSource", SDirection.kIn).value
        inName = self.getPlug("name", SDirection.kIn).value

        # Check the input values
        if not items:
            raise ValueError("No items provided. A list of timeline items is required to get one item.")
        resultItem = None
        for item in items:
            if nameSource == "TimelineItem":
                itemName = item.GetName()
            elif nameSource == "MediaPoolClip":
                mediaPoolItemObj = item.GetMediaPoolItem()
                if not mediaPoolItemObj:
                    continue
                itemName = mediaPoolItemObj.GetClipProperty("Clip Name")
            else:
                raise ValueError("Name source {0} is nor valid. Please choose between 'TimelineItem' or 'MediaPoolClip'.".format(nameSource))

            if itemName != inName:
                continue
            resultItem = item
            break

        if resultItem:
            try:
                mediaPoolItem = resultItem.GetMediaPoolItem()
            except Exception as e:
                logger.warning(e)
                logger.warning("The MediaPool Item could not be get from the timeline item. Returning None.")
                mediaPoolItem = None
        else:
            mediaPoolItem = None
        self.getPlug("item", SDirection.kOut).setValue(resultItem)
        self.getPlug("clip", SDirection.kOut).setValue(mediaPoolItem)
        super(self.__class__, self).execute()


class DVR_TimelineItemsGet(DVR_Base):
    """Operator to get a list of timelineItems from a given timeline.
    You can use different methods: 'All' to get the clips from all the tracks of the given trackType,
    'ByTrackIdx' to get only the items from the give track index or 'ByTrackName' to get the clips from the
    given track Name.
    Works in Davinci Resolve.

    """

    def __init__(self, code, parent):
        super(self.__class__, self).__init__(code, parent=parent)
        i_timeline = SPlug(
            code="timeline",
            value=None,
            type=SType.kInstance,
            direction=SDirection.kIn,
            parent=self)
        i_trackType = SPlug(
            code="trackType",
            value="video",
            type=SType.kEnum,
            options=["video", "audio", "subtitle"],
            direction=SDirection.kIn,
            parent=self)
        i_getMethod = SPlug(
            code="getMethod",
            value="All",
            type=SType.kEnum,
            options=["All", "ByTrackIdx", "ByTrackName"],
            direction=SDirection.kIn,
            parent=self)
        i_key = SPlug(
            code="key",
            value="",
            type=SType.kString,
            direction=SDirection.kIn,
            parent=self)
        o_items = SPlug(
            code="items",
            value=None,
            type=SType.kInstance,
            direction=SDirection.kOut,
            parent=self)

        self.addPlug(i_timeline)
        self.addPlug(i_trackType)
        self.addPlug(i_getMethod)
        self.addPlug(i_key)
        self.addPlug(o_items)

    def _getItemsFromTrack(self, timeline, trackType, trackIdx):
        """Gets the timeline items list for the given track type and index from the given timeline.

        @param timeline DaVinciResolve.Timeline: The timeline object from where the clips will be get.

        @param trackType str: The track type to read. Must be video, audio or subtitle.
        @param trackIdx int: The index of the track to read the clips from.

        @return list: The list of timeline items.

        """
        try:
            items = timeline.GetItemListInTrack(trackType, trackIdx)
        except Exception as e:
            raise RuntimeError("The clips could not be read from the timeline: \n{0}".format(str(e)))
        return items


    def execute(self, force=False):
        """Returns a list of timeline items from the given timeline.

        @param force Bool: Sets the flag for forcing the execution even on clean nodes. (Default = False)

        """
        self.checkDvr()
        timeline = self.getPlug("timeline", SDirection.kIn).value
        trackType = self.getPlug("trackType", SDirection.kIn).value
        getMethod = self.getPlug("getMethod", SDirection.kIn).value
        trackKey = self.getPlug("key", SDirection.kIn).value
        # Check the input values
        if timeline is None:
            raise ValueError("A Timeline object is required to get the items.")
        # Get the items with the selected method
        if getMethod == "All":
            items = []
            for trackIdx in range(1, timeline.GetTrackCount(trackType) + 1):
                items.extend(self._getItemsFromTrack(timeline, trackType, trackIdx))
            if not items:
                logger.warning("No Timeline Items found.")
        elif getMethod == "ByTrackIdx":
            trackIdx = self.getDrvIdx(trackKey, "Timeline", timeline.GetTrackCount(trackType))
            items = self._getItemsFromTrack(timeline, trackType, trackIdx)
        elif getMethod == "ByTrackName":
            items = []
            for trackIdx in range(1, timeline.GetTrackCount(trackType) + 1):
                if timeline.GetTrackName(trackType, trackIdx) == trackKey:
                    items = self._getItemsFromTrack(timeline, trackType, trackIdx)
                    break
            if not items:
                logger.warning("Track name not found or the track is empty.")
        else:
            raise ValueError("Get method '{0}' is not valid. Please choose between "
                             "'ByTrackIdx', 'ByTrackName' or 'All'.".format(getMethod))


        self.getPlug("items", SDirection.kOut).setValue(items)
        super(self.__class__, self).execute()


class DVR_TimelineNameGet(DVR_Base):
    """Operator to get the name of a timeline.
    Works in Davinci Resolve.

    """

    def __init__(self, code, parent):
        super(self.__class__, self).__init__(code, parent=parent)
        i_timeline = SPlug(
            code="timeline",
            value=None,
            type=SType.kInstance,
            direction=SDirection.kIn,
            parent=self)
        o_name = SPlug(
            code="name",
            value="",
            type=SType.kString,
            direction=SDirection.kOut,
            parent=self)


        self.addPlug(i_timeline)
        self.addPlug(o_name)

    def execute(self, force=False):
        """Returns the specified timeline obj from Resolve.

        @param force Bool: Sets the flag for forcing the execution even on clean nodes. (Default = False)

        """
        self.checkDvr()
        timeline = self.getPlug("timeline", SDirection.kIn).value

        # Check the input values
        if timeline is None:
            raise ValueError("A Timeline object is required to get the name from.")

        # Export the timeline
        try:
            name = timeline.GetName()
        except Exception as e:
            raise RuntimeError("The timeline name could not be get: \n{0}".format(str(e)))
        self.getPlug("name", SDirection.kOut).setValue(name)
        super(self.__class__, self).execute()


class DVR_TimelineNameSet(DVR_Base):
    """Operator to set the name of a timeline.
    Works in Davinci Resolve.

    """

    def __init__(self, code, parent):
        super(self.__class__, self).__init__(code, parent=parent)
        i_timeline = SPlug(
            code="timeline",
            value=None,
            type=SType.kInstance,
            direction=SDirection.kIn,
            parent=self)
        i_name = SPlug(
            code="name",
            value="",
            type=SType.kString,
            direction=SDirection.kIn,
            parent=self)

        self.addPlug(i_timeline)
        self.addPlug(i_name)

    def execute(self, force=False):
        """Returns the specified timeline obj from Resolve.

        @param force Bool: Sets the flag for forcing the execution even on clean nodes. (Default = False)

        """
        self.checkDvr()
        timeline = self.getPlug("timeline", SDirection.kIn).value
        name = self.getPlug("name", SDirection.kIn).value
        # Check the input values
        if timeline is None:
            raise ValueError("A Timeline object is required to set the name.")

        # Export the timeline
        msg = ""
        try:
            result = timeline.SetName(name)
        except Exception as e:
            msg = str(e)
            result = False

        if not result:
            raise RuntimeError("The timeline name could not be set:  \n  {0}".format(msg))
        super(self.__class__, self).execute()

# TODO Issue #5 - Define Resolve DCC, create a Resolve method to launch Shift, ...
catalog = {
    "Description": "A catalog to use Davinci Resolve in Shift. "
                   "You can use the operators from this catalog to read, modify and export media, clips and "
                   "timeline data from Resolve.",
    "Version": "1.0.0",
    "Author": "Shift R&D Team",
    "Operators": [
        [DVR_ClipPropertyGet, []],
        [DVR_ClipGet, []],
        [DVR_ClipsGet, []],
        [DVR_FolderAdd, []],
        [DVR_FolderGet, []],
        [DVR_FolderNameGet, []],
        [DVR_FolderSet, []],
        [DVR_MetadataGet, []],
        [DVR_MetadataSet, []],
        [DVR_ProjectExport, []],
        [DVR_ProjectGet, []],
        [DVR_ProjectImport, []],
        [DVR_TakeAdd, []],
        [DVR_TakeGet, []],
        [DVR_TakeSet, []],
        [DVR_TimelineExport, []],
        [DVR_TimelineGet, []],
        [DVR_TimelineSet, []],
        [DVR_TimelineImport, []],
        [DVR_TimelineItemGet, []],
        [DVR_TimelineItemsGet, []],
        [DVR_TimelineNameGet, []],
        [DVR_TimelineNameSet, []]
    ]
}
