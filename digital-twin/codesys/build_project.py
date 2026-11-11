# Run inside the CODESYS scripting engine. The original is opened and copied.
from copy import deepcopy
import os
import tempfile
import xml.etree.ElementTree as ET

from scriptengine import NativeImportResult

here = os.path.dirname(__file__)
repo = os.path.dirname(os.path.dirname(here))


def prop(element, name):
    return element.find("./Single[@Name='{}']".format(name))


def members(element):
    rows = prop(element, "VisualElemMemberList").find("List")
    return {row[0].text: row[1] for row in rows if len(row) == 2}


def adapt_visualization(project, visualization):
    # CODESYS native export preserves the tank drawing, geometry and bindings.
    with tempfile.NamedTemporaryFile(suffix=".export", delete=False) as scratch:
        path = scratch.name
    try:
        project.export_native([visualization], path)
        tree = ET.parse(path)
        elements = [element for element in tree.iter("Single")
                    if prop(element, "VisualElementName") is not None]
        indicator = next(element for element in elements
                         if members(element).get("743958181") is not None
                         and members(element)["743958181"].text == "GVL.SystemActive")
        sensor_controls = ("GVL.B1", "GVL.B2", "GVL.B3", "GVL.Start", "GVL.Stop")
        bindings = {"GVL.Start": "GVL.ModbusOK", "GVL.Stop": "GVL.RemoteOverride"}
        labels = {"Start": "Enlace Modbus", "Stop": "Mando remoto"}
        for element in elements:
            properties = members(element)
            binding = properties.get("743958181")
            if binding is not None and binding.text in sensor_controls:
                lamp_properties = deepcopy(prop(indicator, "VisualElemMemberList"))
                new_properties = {row[0].text: row[1] for row in lamp_properties.find("List")
                                  if len(row) == 2}
                for geometry in ("1649127785", "357335551", "2422045748", "2134141914",
                                 "550940142", "1473355128"):
                    new_properties[geometry].text = properties[geometry].text
                new_properties["743958181"].text = bindings.get(binding.text, binding.text)
                old_properties = prop(element, "VisualElemMemberList")
                element.insert(list(element).index(old_properties), lamp_properties)
                element.remove(old_properties)
                for name in ("VisualElementName", "VisualElementTypeName"):
                    prop(element, name).text = prop(indicator, name).text
            label = properties.get("390574330")
            if label is not None and label.text in labels:
                label.text = labels[label.text]
        tree.write(path, encoding="utf-8", xml_declaration=True)
        visualization.remove()
        result = project.import_native(filename=path)
        if result != NativeImportResult.ok:
            raise RuntimeError("Visualization import: {}".format(result))
        if not project.find("Visualization", True):
            raise RuntimeError("Visualization missing after import")
    finally:
        os.remove(path)


project = projects.open(os.path.join(repo, "codesys", "RA.project"))
try:
    project.find("Device", False)[0].set_simulation_mode(False)
    app = project.active_application
    gvl = app.find("GVL", False)[0]
    gvl.textual_declaration.replace(
        gvl.textual_declaration.text.replace(
            "END_VAR", "    ModbusOK : BOOL;\n    RemoteOverride : BOOL;\n"
            "    SerialInputs : BOOL;\nEND_VAR"
        )
    )
    manager = next(obj for obj in app.get_children(False) if obj.is_libman)
    library = next(lib for lib in librarymanager.get_all_libraries()
                   if lib.title == "ModbusFB" and str(lib.version) == "4.5.0.0")
    manager.add_library(library)
    pou = app.create_program("Twin_Poll")
    with open(os.path.join(here, "Twin_Poll.decl.st")) as declaration:
        pou.textual_declaration.replace(declaration.read())
    with open(os.path.join(here, "Twin_Poll.impl.st")) as implementation:
        pou.textual_implementation.replace(implementation.read())
    task = app.find("MainTask", True)[0]
    task.pous.remove("PLC_PRG")
    task.pous.add("Twin_Poll")
    adapt_visualization(project, app.find("Visualization", False)[0])
    app.generate_code()
    project.save_as(os.path.join(here, "TankTwin.project"))
finally:
    project.close()
