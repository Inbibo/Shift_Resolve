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

    def isDvrAvailable(self):
        """Method to check if Davinci Resolve is available in the current Env.

        @return bool: True if drv is available, False otherwise.

        """
        try:
            import DaVinciResolveScript as dvr_script
            res = True
        except:
            res = False
        return res

    def checkDvr(self):
        """Method that checks if drv module is available and ready to use. If not raises an error."""
        if not self.isDvrAvailable():
            raise EnvironmentError("This operator can be executed only inside Davinci Resolve with "
                                   "Python installed and the API configured.")


class DVR_ProjectExport(DVR_Base):
    """Operator to get the current Resolve project object.
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
        o_result = SPlug(
            code="result",
            value=False,
            type=SType.kBool,
            direction=SDirection.kOut,
            parent=self)

        self.addPlug(i_project)
        self.addPlug(i_filepath)
        self.addPlug(o_result)

    def execute(self, force=False):
        """Returns the current project from Davinci Resolve.

        @param force Bool: Sets the flag for forcing the execution even on clean nodes. (Default = False)

        """
        self.checkDvr()
        project = self.getPlug("project", SDirection.kIn).value
        filepath = self.getPlug("filepath", SDirection.kIn).value
        if not project:
            raise ValueError("A Davinci Resolve project is required to export.")
        if not filepath or not filepath.endswith(".drp"):
            raise ValueError("A filepath for a .drp file is required to export the project.")
        try:
            result = projectManager.ExportProject(project.GetName(), filepath)
        except Exception as e:
            logger.error(e)
            raise RuntimeError("The project couldn't be exported. Check the log for more information.")
        self.getPlug("result", SDirection.kOut).setValue(result)
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
            try:
                timeIdx = int(timeKey)
            except Exception as e:
                raise ValueError("The key value must be an integer for the 'ByIndex' Get Method.")
            if timeIdx > project.GetTimelineCount() or timeIdx < 0:
                raise ValueError("Timeline index out of range. "
                                 "There are {0} timelines available.".format(project.GetTimelineCount()))
            elif timeIdx == 0:
                logger.warning("The resolve lists for timelines starts at index 1.")
            # Get the timeline for the given index
            try:
                timeline = project.GetTimelineByIndex(timeIdx)
            except Exception as e:
                raise RuntimeError("The current timeline could not be get.")
        elif getMethod == "Current":
            try:
                timeline = project.GetCurrentTimeline()
            except Exception as e:
                raise RuntimeError("The current timeline could not be get.")
        else:
            raise ValueError("Get Method '{0}' is not supported".format(getMethod))
        self.getPlug("timeline", SDirection.kOut).setValue(timeline)
        super(self.__class__, self).execute()


class DVR_TimelineExport(DVR_Base):
    """Operator to export a Davinci Resolve Timeline object.
    You can select a specific file format for the export or set Auto to get the format from the filepath extension.
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
        o_result = SPlug(
            code="result",
            value="",
            type=SType.kString,
            direction=SDirection.kIn,
            parent=self)


        self.addPlug(i_timeline)
        self.addPlug(i_filepath)
        self.addPlug(i_format)
        self.addPlug(o_result)

    def execute(self, force=False):
        """Returns the specified timeline obj from Resolve.

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
                filepath.rpartition["."][2]
            ))
        # Export the timeline
        try:
            if type(timelineType.get("type")) is list:
                result = timeline.Export(filepath, timelineType.get("type")[0], timelineType.get("type")[1])
            else:
                result = timeline.Export(filepath, timelineType.get("type"))
        except Exception as e:
            logger.error(e)
            raise RuntimeError("Timeline export process have fail.")
        self.getPlug("result", SDirection.kOut).setValue(result)
        super(self.__class__, self).execute()


catalog = {
    "Description": "A catalog to use Davinci Resolve in Shift. "
                   "You can use the operators from this catalog to read, modify and export media, clips and "
                   "timeline data from Resolve.",
    "Version": "1.0.0",
    "Author": "Shift R&D Team",
    "Operators": [
        [DVR_ProjectExport, []],
        [DVR_ProjectGet, []],
        [DVR_TimelineGet, []],
        [DVR_TimelineExport, []]
    ]
}
