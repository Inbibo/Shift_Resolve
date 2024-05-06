import os
try:
    import DaVinciResolveScript as dvr_script

    resolve = dvr_script.scriptapp("Resolve")
    projectManager = resolve.GetProjectManager()
except:
    # If DRV is not available, define the API objects like empty variables
    dvr_script = None
    resolve = None
    projectManager = None

from shift.core.workflow import SOperator
from shift.core.workflow import SPlug
from shift.core.constants import SType
from shift.core.constants import SDirection
from shift.core.logger import shiftLogger as logger


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
        result = True
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
                    if result:
                        result = resAux  # Only edit the result if it's True for now
                    if not resAux:
                        errorPlugs.append(p.code)

        if not result:
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
            raise ValueError("Get Method '{0}' is not supported".format(getMethod))
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
            raise ValueError("Get method '{0}' is not valid. Please choose between 'ByTrackIdx', 'ByTrackName' or 'All'.".format(getMethod))


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
        [DVR_MetadataSet, []],
        [DVR_ProjectExport, []],
        [DVR_ProjectGet, []],
        [DVR_TimelineExport, []],
        [DVR_TimelineGet, []],
        [DVR_TimelineItemGet, []],
        [DVR_TimelineItemsGet, []],
        [DVR_TimelineNameGet, []],
        [DVR_TimelineNameSet, []]
    ]
}
