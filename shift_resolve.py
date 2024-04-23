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

    def _checkDvr(self):
        """Method that checks if drv module is available and ready to use. If not raises an error."""
        if not self.isDvrAvailable():
            raise EnvironmentError("This operator can be executed only inside Davinci Resolve with "
                                   "Python installed and the API configured.")




catalog = {
    "Description": "A catalog to use Davinci Resolve in Shift. "
                   "You can use the operators from this catalog to read, modify and export media, clips and "
                   "timeline data from Resolve.",
    "Version": "1.0.0",
    "Author": "Shift R&D Team",
    "Operators": [
    ]
}