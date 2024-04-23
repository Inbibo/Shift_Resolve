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
            type=SType.kFileIn,
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


catalog = {
    "Description": "A catalog to use Davinci Resolve in Shift. "
                   "You can use the operators from this catalog to read, modify and export media, clips and "
                   "timeline data from Resolve.",
    "Version": "1.0.0",
    "Author": "Shift R&D Team",
    "Operators": [
    ]
}